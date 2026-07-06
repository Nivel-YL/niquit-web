#!/usr/bin/env python3
"""Publisher: promotes approved articles from draft to live.

Reads BLOG_TOPIC_BACKLOG.md, finds topics with status='approved',
publishes up to PUBLISH_COUNT of them (oldest first) by flipping
draft: true → draft: false in all 5 language files, then updates
the backlog status to 'published'.

A push after this script runs triggers Netlify auto-deploy.
"""

import datetime
import os
import re
import sys
from pathlib import Path

import yaml
from slugify import slugify

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
        path.write_text(text.replace('draft: true', 'draft: false', 1), encoding='utf-8')
        published_langs.append(lang)
        print(f'  [{lang}] published: {path.relative_to(REPO_ROOT)}')

    return published_langs


def main() -> None:
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
            topic['status'] = 'published'
            topic.setdefault('published', {})
            for lang in langs:
                topic['published'][lang] = today.isoformat()
            published_ids.append(topic['id'])
            print(f'  → marked published ({", ".join(langs)})')
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


if __name__ == '__main__':
    main()
