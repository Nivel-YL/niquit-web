"""Shared internal-link validator for the blog content pipeline.

Used from two call sites, which catch different things:

  - blog_editor.py, right after an article is written, before it is ever
    saved or committed. Cheap and early: a bad link never becomes a
    'drafted' topic, so no audit-step API cost is wasted on a doomed
    article and no human reviewer ever sees it.

  - publisher.py, right before draft: true -> draft: false. The last gate
    before an article goes live, so it also catches a link broken by a
    manual edit made during human review between 'drafted' and 'approved'
    (draft-time validation can never see that, it already ran and passed).

Both call sites exist because they close different gaps; neither alone is
enough (draft-time validation would have caught none of the links that
were ALREADY published and broken on 2026-08-03/04 - those pre-date this
module - but going forward, requiring both is what keeps a bad link out
of both the drafted pool and the live site, ever again).
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

LANGUAGES = ['en', 'ru', 'de', 'es', 'fr']
# English pages carry no URL prefix on this site (src/pages/blog/[slug].astro),
# only ru/de/es/fr do (src/pages/{lang}/blog/[slug].astro).
PREFIXED_LANGUAGES = ['ru', 'de', 'es', 'fr']
# Domains a link has been seen pointing at instead of a relative path.
# niquit.app itself is included deliberately: every real internal link on
# this site is relative (/lang/blog/slug), so an *absolute* link to the
# site's own domain is itself a defect, not just the stale ones.
STALE_OR_SELF_DOMAINS = ('netlify.app', 'niquit-web.pages.dev', 'niquit.app')


def _existing_slugs(blog_dir: Path) -> dict[str, dict[str, bool]]:
    """lang -> {slug: is_draft} for every article file currently on disk."""
    result: dict[str, dict[str, bool]] = {}
    for lang in LANGUAGES:
        result[lang] = {}
        lang_dir = blog_dir / lang
        if not lang_dir.exists():
            continue
        for f in lang_dir.glob('*.md'):
            text = f.read_text(encoding='utf-8')
            is_draft = bool(re.search(r'^draft:\s*true', text, re.MULTILINE))
            result[lang][f.stem] = is_draft
    return result


def validate_links(body: str, lang: str, blog_dir: Path, require_published: bool = False) -> list[str]:
    """Check every in-body link/pseudo-link in `body` (an article written in
    `lang`). Returns a list of human-readable problems; empty means clean.

    `require_published`: at draft time a link to a same-cluster sibling
    that is itself still draft:true is normal (they often get approved and
    published together) so leave this False. At publish time it must be
    True, since a link to a still-draft target would 404 the moment this
    article goes live.

    Catches all three failure modes actually seen in production so far:
    a relative /blog/ link to a slug that doesn't exist or the wrong
    language, an absolute URL to the site's own domain (stale niquit.
    netlify.app or otherwise) instead of a relative path, and a
    [text] with the (url) dropped entirely, which renders as literal
    square brackets on the live page instead of a link.
    """
    problems: list[str] = []
    slugs = _existing_slugs(blog_dir)

    for m in re.finditer(r'\[([^\]]+)\](?!\()', body):
        problems.append(f'"[{m.group(1)}]" has no (url) after it - dropped link')

    for m in re.finditer(r'\]\((https?://[^)]+)\)', body):
        url = m.group(1)
        if any(d in url for d in STALE_OR_SELF_DOMAINS):
            problems.append(f'"{url}" is an absolute URL to the site itself - internal links must be a relative /lang/blog/slug path')

    for m in re.finditer(r'\]\((/[^)]+)\)', body):
        link = m.group(1)
        if link.startswith('/images/'):
            continue
        parts = [p for p in link.split('/') if p]
        if not parts:
            continue
        if parts[0] == 'en':
            problems.append(f'"{link}" - "en" is never a URL prefix on this site (English pages have no lang prefix, use /blog/slug)')
            continue
        idx, link_lang = 0, 'en'
        if parts[0] in PREFIXED_LANGUAGES:
            link_lang, idx = parts[0], 1
        if idx >= len(parts) or parts[idx] != 'blog':
            continue
        slug = '/'.join(parts[idx + 1:])
        if not slug:
            continue
        if link_lang != lang:
            problems.append(f'"{link}" points at lang={link_lang} but this article is lang={lang}')
        elif slug not in slugs.get(link_lang, {}):
            problems.append(f'"{link}" - no article with that slug exists for lang={link_lang}')
        elif require_published and slugs[link_lang][slug]:
            problems.append(f'"{link}" - target is still draft:true, would 404 on a live page')

    return problems


def create_github_issue(title: str, body: str) -> str | None:
    """Create a GitHub issue via the REST API using the Actions-provided GITHUB_TOKEN.
    Never raises, a failed escalation should not crash the calling pipeline, it is
    only logged. Returns the issue URL, or None if it could not be created.
    """
    token = os.environ.get('GITHUB_TOKEN')
    repo = os.environ.get('GITHUB_REPOSITORY')
    if not token or not repo:
        print(
            f'WARNING: cannot create GitHub issue (missing GITHUB_TOKEN/GITHUB_REPOSITORY). '
            f'Title would have been: {title}',
            file=sys.stderr,
        )
        return None

    req = urllib.request.Request(
        f'https://api.github.com/repos/{repo}/issues',
        data=json.dumps({'title': title, 'body': body}).encode('utf-8'),
        headers={
            'Authorization': f'Bearer {token}',
            'Accept': 'application/vnd.github+json',
            'Content-Type': 'application/json',
            'X-GitHub-Api-Version': '2022-11-28',
        },
        method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return data.get('html_url')
    except urllib.error.URLError as exc:
        print(f'WARNING: failed to create GitHub issue: {exc}', file=sys.stderr)
        return None
