#!/usr/bin/env python3
"""Automated blog editor for niquit.netlify.app.

Picks the first pending topic from BLOG_TOPIC_BACKLOG.md,
researches it with web search, writes native articles in 5 languages,
generates an SVG cover, and commits everything as a draft.
"""

import datetime
import hashlib
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import anthropic
import yaml
from slugify import slugify

# ── paths ────────────────────────────────────────────────────────────────────

REPO_ROOT    = Path(__file__).parent.parent
BLOG_DIR     = REPO_ROOT / 'src' / 'content' / 'blog'
IMAGES_DIR   = REPO_ROOT / 'public' / 'images' / 'blog'
BACKLOG_PATH = REPO_ROOT / 'BLOG_TOPIC_BACKLOG.md'
VOICE_GUIDE  = REPO_ROOT / 'docs' / 'CONTENT_VOICE_GUIDE.md'

# ── config ───────────────────────────────────────────────────────────────────

RESEARCH_MODEL = 'claude-haiku-4-5'   # fact gathering — speed + cost
WRITE_MODEL    = 'claude-sonnet-5'    # article writing — quality matters

LANGUAGES = ['en', 'ru', 'de', 'es', 'fr']

LANG_LABELS = {
    'en': 'English-speaking audience (global)',
    'ru': 'Russian-speaking audience',
    'de': 'German-speaking audience',
    'es': 'Spanish-speaking audience (Spain and Latin America)',
    'fr': 'French-speaking audience (France and Francophone countries)',
}

LANG_NAMES = {
    'en': 'English',
    'ru': 'Russian (Русский)',
    'de': 'German (Deutsch)',
    'es': 'Spanish (Español)',
    'fr': 'French (Français)',
}

CLUSTER_ICONS = {
    'A': '\U0001f91d',    # 🤝 pouches/snuff
    'B': '\U0001f4a8',    # 💨 vape
    'C': '\U0001f6ac',    # 🚬 cigarettes
    'D': '\U0001f3af',    # 🎯 multi-source
    'E': '\U0001f9e0',    # 🧠 psychology
    'F': '❤️',            # ❤️ health
    'G': '⚡',            # ⚡ practice
    'H': '\U0001f52e',    # 🔮 myths
}

NAVY  = '#0A1A33'
PANEL = '#0F2244'
CORAL = '#FF6B5C'

# ── backlog ───────────────────────────────────────────────────────────────────

BACKLOG_RE = re.compile(r'<!--BACKLOG\n(.*?)BACKLOG-->', re.DOTALL)


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


# ── SVG cover ─────────────────────────────────────────────────────────────────

def generate_svg(topic_id: str, cluster: str) -> str:
    seed   = int(hashlib.md5(topic_id.encode()).hexdigest()[:8], 16)
    ox     = (seed % 41) - 20
    oy     = ((seed >> 8) % 41) - 20
    rot    = ((seed >> 16) % 31) - 15
    icon   = CLUSTER_ICONS.get(cluster, '\U0001f4dd')
    cx, cy = 600 + ox, 315 + oy
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630">\n'
        f'  <defs>\n'
        f'    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1" gradientUnits="objectBoundingBox">\n'
        f'      <stop offset="0%" stop-color="{NAVY}"/>\n'
        f'      <stop offset="100%" stop-color="{PANEL}"/>\n'
        f'    </linearGradient>\n'
        f'  </defs>\n'
        f'  <rect width="1200" height="630" fill="url(#bg)"/>\n'
        f'  <text x="{cx}" y="{cy}" font-size="420" text-anchor="middle"\n'
        f'        dominant-baseline="middle" opacity="0.10"\n'
        f'        transform="rotate({rot},{cx},{cy})">{icon}</text>\n'
        f'  <rect x="80" y="120" width="5" height="390" fill="{CORAL}" rx="2.5"/>\n'
        f'  <rect x="0" y="600" width="1200" height="30" fill="{CORAL}" opacity="0.18"/>\n'
        f'</svg>'
    )


# ── Claude calls ──────────────────────────────────────────────────────────────

def research(client: anthropic.Anthropic, topic_title: str, lang: str) -> str:
    resp = client.messages.create(
        model=RESEARCH_MODEL,
        max_tokens=1024,
        tools=[{'type': 'web_search_20260209', 'name': 'web_search', 'max_uses': 2}],
        system=(
            'You are a content researcher. Use web search to gather accurate, current '
            'facts about the given topic. Prioritize: specific statistics with sources, '
            'recent scientific findings, and concrete numbers. Summarize concisely in '
            'English regardless of target language.'
        ),
        messages=[{
            'role': 'user',
            'content': (
                f'Research for a blog article targeting: {LANG_LABELS[lang]}\n'
                f'Topic: {topic_title}\n\n'
                'Gather: current statistics, key scientific facts, and data points that '
                'would be surprising or highly informative to someone wanting to quit nicotine. '
                'Include local or regional statistics relevant to the target audience where '
                'they differ meaningfully from global averages.'
            ),
        }],
    )
    parts = [b.text for b in resp.content if hasattr(b, 'text') and b.text]
    return '\n\n'.join(parts) if parts else '(No research returned)'


def write_article(
    client: anthropic.Anthropic,
    topic_title: str,
    lang: str,
    research_text: str,
    voice_guide_text: str,
) -> tuple[str, str, str]:
    # voice_guide_text is identical across all 5 write calls in a run —
    # cache_control tells Anthropic to cache it (up to 90% cheaper on cache hits)
    resp = client.messages.create(
        model=WRITE_MODEL,
        max_tokens=4096,
        system=[{
            'type': 'text',
            'text': voice_guide_text,
            'cache_control': {'type': 'ephemeral'},
        }],
        messages=[{
            'role': 'user',
            'content': (
                f'Write a blog article about: {topic_title}\n'
                f'Language: {LANG_NAMES[lang]}\n\n'
                f'Research findings:\n{research_text}\n\n'
                'Use EXACTLY this output format:\n'
                '1. Line 1: # [Article title in target language]\n'
                '2. Line 2: > [SEO meta description, 120-155 characters, in target language]\n'
                '3. Blank line, then the full article body (800-1200 words)\n\n'
                f'Write natively in {LANG_NAMES[lang]}. Not a translation from English. '
                'Apply all rules from the system prompt.'
            ),
        }],
    )

    text = next(b.text for b in resp.content if b.type == 'text').strip()

    title_m = re.search(r'^#\s+(.+)$', text, re.MULTILINE)
    title   = title_m.group(1).strip() if title_m else topic_title

    desc_m      = re.search(r'^>\s+(.+)$', text, re.MULTILINE)
    description = desc_m.group(1).strip() if desc_m else ''
    if not description:
        paras = [p.strip() for p in text.split('\n\n') if p.strip() and not p.startswith('#')]
        description = (paras[0][:152] + '...') if paras else ''

    body = re.sub(r'^#\s+.+\n?', '', text, count=1)
    body = re.sub(r'^>\s+.+\n?', '', body, count=1)
    body = body.strip()

    return title, description, body


# ── frontmatter ───────────────────────────────────────────────────────────────

def build_frontmatter(title: str, description: str, today: datetime.date, lang: str, slug: str) -> str:
    t = title.replace('"', '\\"')
    d = description.replace('"', '\\"')
    return '\n'.join([
        '---',
        f'title: "{t}"',
        f'description: "{d}"',
        f'publishDate: {today.isoformat()}',
        f'lang: {lang}',
        'draft: true',
        f'heroImage: /images/blog/{slug}.svg',
        '---',
    ])


# ── per-language pipeline (runs in parallel) ──────────────────────────────────

def process_language(
    lang: str,
    client: anthropic.Anthropic,
    topic_title: str,
    voice_guide_txt: str,
    article_slug: str,
    today: datetime.date,
) -> str:
    print(f'[{lang}] researching...', flush=True)
    research_text = research(client, topic_title, lang)

    print(f'[{lang}] writing...', flush=True)
    title, description, body = write_article(
        client, topic_title, lang, research_text, voice_guide_txt
    )

    frontmatter  = build_frontmatter(title, description, today, lang, article_slug)
    article_text = frontmatter + '\n\n' + body + '\n'

    out_dir = BLOG_DIR / lang
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f'{article_slug}.md'
    out_path.write_text(article_text, encoding='utf-8')
    print(f'[{lang}] saved: {out_path.relative_to(REPO_ROOT)}', flush=True)
    return lang


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print('ERROR: ANTHROPIC_API_KEY is not set.', file=sys.stderr)
        sys.exit(1)

    client          = anthropic.Anthropic(api_key=api_key)
    voice_guide_txt = VOICE_GUIDE.read_text(encoding='utf-8')

    topics  = load_backlog()
    pending = next((t for t in topics if t.get('status') == 'pending'), None)
    if not pending:
        print('No pending topics in backlog. Nothing to do.')
        sys.exit(0)

    topic_id     = pending['id']
    topic_title  = pending['title_en']
    cluster      = pending['cluster']
    article_slug = slugify(topic_title)
    today        = datetime.date.today()

    print(f'Topic  : {topic_id} — {topic_title}')
    print(f'Slug   : {article_slug}')
    print(f'Cluster: {cluster}')

    # SVG cover — deterministic, no API call
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    svg_path = IMAGES_DIR / f'{article_slug}.svg'
    svg_path.write_text(generate_svg(topic_id, cluster), encoding='utf-8')
    print(f'SVG    : {svg_path.relative_to(REPO_ROOT)}')

    # Mark in_progress so a concurrent run skips this topic
    pending['status'] = 'in_progress'
    save_backlog(topics)

    # Process all 5 languages in parallel (each: Haiku research → Sonnet write)
    with ThreadPoolExecutor(max_workers=len(LANGUAGES)) as executor:
        futures = {
            executor.submit(
                process_language,
                lang, client, topic_title, voice_guide_txt, article_slug, today,
            ): lang
            for lang in LANGUAGES
        }
        errors = []
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as exc:
                errors.append((futures[future], exc))

    if errors:
        for lang, exc in errors:
            print(f'ERROR [{lang}]: {exc}', file=sys.stderr)
        sys.exit(1)

    # Mark drafted
    topics = load_backlog()
    topic  = next(t for t in topics if t['id'] == topic_id)
    topic['status'] = 'drafted'
    topic.setdefault('published', {})
    save_backlog(topics)

    # Export TOPIC_ID for the GitHub Actions commit message step
    gh_env = os.environ.get('GITHUB_ENV')
    if gh_env:
        with open(gh_env, 'a', encoding='utf-8') as f:
            f.write(f'TOPIC_ID={topic_id}\n')

    print(f'\nDone: {topic_id} drafted in {len(LANGUAGES)} languages.')


if __name__ == '__main__':
    main()
