#!/usr/bin/env python3
"""Publisher: promotes approved articles from draft to live.

Reads BLOG_TOPIC_BACKLOG.md, finds topics with status='approved',
publishes up to PUBLISH_COUNT of them (oldest first) by flipping
draft: true → draft: false in all 5 language files, then updates
the backlog status to 'published'.

A push after this script runs triggers Cloudflare Pages auto-deploy.
"""

import datetime
import os
import re
import sys
from pathlib import Path

import yaml
from slugify import slugify

import pipeline_status
from link_validator import create_github_issue, validate_links

# ── paths ────────────────────────────────────────────────────────────────────

REPO_ROOT    = Path(__file__).parent.parent
BLOG_DIR     = REPO_ROOT / 'src' / 'content' / 'blog'
BACKLOG_PATH = REPO_ROOT / 'BLOG_TOPIC_BACKLOG.md'

# ── config ───────────────────────────────────────────────────────────────────

LANGUAGES     = ['en', 'ru', 'de', 'es', 'fr']
PUBLISH_COUNT = int(os.environ.get('PUBLISH_COUNT', '1'))
BACKLOG_RE    = re.compile(r'<!--BACKLOG\n(.*?)BACKLOG-->', re.DOTALL)

# ── backlog helpers ───────────────────────────────────────────────────────────

def load_backlog() -> list[dict]:
    content = BACKLOG_PATH.read_text(encoding='utf-8')
    m = BACKLOG_RE.search(content)
    if not m:
        raise RuntimeError(f'No <!--BACKLOG ... BACKLOG--> block in {BACKLOG_PATH}')
    return yaml.safe_load(m.group(1))['topics']


def save_backlog(topics: list[dict]) -> None:
    def _normalize(obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        if isinstance(obj, dict):
            return {k: _normalize(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_normalize(v) for v in obj]
        return obj

    normalized = _normalize(topics)
    new_yaml = yaml.dump(
        {'topics': normalized},
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
    )
    content = BACKLOG_PATH.read_text(encoding='utf-8')
    new_block = f'<!--BACKLOG\n{new_yaml}BACKLOG-->'
    new_content = BACKLOG_RE.sub(new_block, content, count=1)
    BACKLOG_PATH.write_text(new_content, encoding='utf-8')


# ── publish logic ─────────────────────────────────────────────────────────────

def publish_topic(topic: dict, today: datetime.date) -> list[str]:
    """Flip draft: true → draft: false for all language files of a topic.
    Returns list of languages successfully published."""
    slug = slugify(topic['title_en'])
    published_langs: list[str] = []

    for lang in LANGUAGES:
        path = BLOG_DIR / lang / f'{slug}.md'
        if not path.exists():
            print(f'  [{lang}] WARNING: file not found — {path.relative_to(REPO_ROOT)}',
                  file=sys.stderr)
            continue
        text = path.read_text(encoding='utf-8')
        if 'draft: true' not in text:
            print(f'  [{lang}] already live, skipping')
            continue

        # Last gate before this goes live (2026-08-04): draft-time validation
        # in blog_editor.py already checks links, but this also catches a
        # link broken by a manual edit made during human review between
        # 'drafted' and 'approved', which draft-time validation never sees
        # since it already ran and passed before that edit happened.
        # require_published=True here (unlike the draft-time call) because a
        # link to a still-draft sibling would 404 the moment this page
        # actually goes live, where it was fine to leave unresolved earlier.
        link_problems = validate_links(text, lang, BLOG_DIR, require_published=True)
        if link_problems:
            print(f'  [{lang}] BLOCKED: {len(link_problems)} bad link(s), not publishing', file=sys.stderr)
            issue_url = create_github_issue(
                title=f'[blog-pipeline] Publish blocked: bad link(s) in {slug} ({lang})',
                body=(
                    f'Article: `{path.relative_to(REPO_ROOT)}`\n\n'
                    f'Publisher would not flip this to draft: false because of:\n\n'
                    + '\n'.join(f'- {p}' for p in link_problems)
                    + '\n\nFix the link(s) and re-run the publisher, or this topic stays queued.'
                ),
            )
            if issue_url:
                print(f'  [{lang}] escalated to {issue_url}', file=sys.stderr)
            continue

        text = text.replace('draft: true', 'draft: false', 1)
        text = re.sub(r'publishDate: \d{4}-\d{2}-\d{2}', f'publishDate: {today.isoformat()}', text, count=1)
        path.write_text(text, encoding='utf-8')
        published_langs.append(lang)
        print(f'  [{lang}] published: {path.relative_to(REPO_ROOT)}')

    return published_langs


def main() -> None:
    try:
        topics   = load_backlog()
        approved = [t for t in topics if t.get('status') == 'approved']

        if not approved:
            print('No approved articles in queue. Nothing to publish.')
            sys.exit(0)

        today        = datetime.date.today()
        to_publish   = approved[:PUBLISH_COUNT]
        published_ids: list[str] = []

        for topic in to_publish:
            print(f'\nPublishing: {topic["id"]} — {topic["title_en"]}')
            langs = publish_topic(topic, today)
            if langs:
                # Update backlog entry in-place (topics list is already loaded)
                topic.setdefault('published', {})
                for lang in langs:
                    topic['published'][lang] = today.isoformat()
                # Only 'published' once every language is actually live. A
                # language the link validator just blocked stays draft: true
                # on disk, so leaving status at 'approved' here (instead of
                # unconditionally marking 'published' the moment ANY language
                # went out) keeps this topic in the queue so the next
                # publisher run retries the blocked one too, rather than
                # silently losing it the moment it drops out of 'approved'.
                if set(topic['published']) >= set(LANGUAGES):
                    topic['status'] = 'published'
                    print(f'  → marked published ({", ".join(langs)})')
                else:
                    still_missing = [l for l in LANGUAGES if l not in topic['published']]
                    print(f'  → partially published ({", ".join(langs)}); staying in queue, missing: {", ".join(still_missing)}')
                published_ids.append(topic['id'])
            else:
                print(f'  → no files updated, skipping backlog update', file=sys.stderr)

        save_backlog(topics)

        remaining = len([t for t in topics if t.get('status') == 'approved'])
        print(f'\nPublished : {len(published_ids)} article(s): {", ".join(published_ids)}')
        print(f'In queue  : {remaining} approved article(s) still waiting')

        # Export IDs for GitHub Actions commit message
        gh_env = os.environ.get('GITHUB_ENV')
        if gh_env:
            with open(gh_env, 'a', encoding='utf-8') as f:
                f.write(f'PUBLISHED_IDS={",".join(published_ids)}\n')

        if not published_ids:
            sys.exit(1)
    finally:
        # Regenerate PIPELINE_STATUS.md from current backlog state, every run,
        # success, no-op, or early exit alike, so the status file never goes stale.
        pipeline_status.write_pipeline_status()


if __name__ == '__main__':
    main()
