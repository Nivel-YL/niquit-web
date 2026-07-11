#!/usr/bin/env python3
"""Automated blog editor for niquit.app.

Architecture (per topic):
  1. ONE shared research call  → universal facts with sources + detect which langs need local context
  2. Targeted local searches   → only for languages that actually need country-specific data
  3. 5 parallel write calls    → each gets shared facts + its local addon
  4. 5 parallel audit calls    → cheap Haiku call, no search, compares article vs research facts
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
AUDIT_DIR    = REPO_ROOT / 'docs' / 'fact-audits'

# ── config ───────────────────────────────────────────────────────────────────

RESEARCH_MODEL = 'claude-haiku-4-5'   # research + audit — speed + cost
WRITE_MODEL    = 'claude-sonnet-5'    # article writing — quality matters

BATCH_SIZE = int(os.environ.get('BATCH_SIZE', '3'))  # topics per run

LANGUAGES = ['en', 'ru', 'de', 'es', 'fr']

LANG_LABELS = {
    'en': 'English-speaking audience (global)',
    'ru': 'Russian-speaking audience (Russia)',
    'de': 'German-speaking audience (Germany, Austria, Switzerland)',
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
    'A': '\U0001f343',
    'B': '\U0001f4a8',
    'C': '\U0001f6ac',
    'D': '\U0001f3af',
    'E': '\U0001f9e0',
    'F': '❤️',
    'G': '⚡',
    'H': '\U0001f52e',
}

NAVY  = '#0A1A33'
PANEL = '#0F2244'
CORAL = '#FF6B5C'

# ── blocked sources (Tier 3 — hard block, never cite regardless of convenience) ──
# Rule: never cite a site that sells nicotine products OR is a competing quit app.
# Source: AI_EDITOR_SOURCE_VETTING_SPEC.md

BLOCKED_SOURCES: list[str] = [
    # Nicotine retailers
    'juicefly', 'juicefly.com',
    # Competing quit apps / products
    'quitwithjones', 'jones quit', 'jones quit app', 'quit with jones',
    'quitnic',        # competing app — not the 2021 Bonevski RCT in Nicotine & Tobacco Research
    'smoke free app', 'smokefreeglobal',
    'kwit app', 'kwit.app',
    'tobaccostopswithme', 'tobacco stops with me',  # nicotine sales / quit-product hybrid
]

# Human-readable names for the same entries (matched case-insensitively in research text).
BLOCKED_SOURCE_PATTERNS: list[str] = [s.lower() for s in BLOCKED_SOURCES]


def check_blocked_sources(text: str) -> list[str]:
    """Scan research text for blocked Tier-3 sources.
    Returns list of blocked names found; empty list = clean.
    """
    lower = text.lower()
    return [pat for pat in BLOCKED_SOURCE_PATTERNS if pat in lower]


# ── mechanical style rules (no AI, binary pass/fail) ─────────────────────────
# These are checked by code after writing, before saving.
# Source: CONTENT_VOICE_GUIDE.md §2 (em-dash) and §4 (banned patterns).

EM_DASH_RE = re.compile(r'\s*—\s*')  # always auto-fixed, never flagged

BANNED_PHRASES: dict[str, list[str]] = {
    'en': [
        "in today's world",
        "in this article, we will",
        "in this article we will",
        "let's dive into",
        "let's explore",
        "on one hand",
        "so remember:",
        "it is worth noting",
        "it's worth noting",
    ],
    'ru': [
        "в современном мире",
        "в этой статье мы рассмотрим",
        "в данной статье",
        "давайте разберёмся",
        "давайте рассмотрим",
        "с одной стороны",
        "таким образом,",   # as filler; trailing comma avoids false positives
    ],
    'de': [
        "heutzutage",
        "in diesem artikel",
        "in diesem artikel werden wir",
        "auf der einen seite",
        "zusammenfassend lässt sich sagen",
    ],
    'es': [
        "en el mundo actual",
        "en este artículo",
        "en este artículo vamos a",
        "por un lado",
        "en resumen,",
    ],
    'fr': [
        "de nos jours",
        "dans cet article",
        "d'un côté",
        "en conclusion,",
        "pour conclure,",
    ],
}


def fix_em_dashes(text: str) -> tuple[str, int]:
    """Auto-replace em-dashes with commas. Returns (fixed_text, count_replaced)."""
    fixed, n = EM_DASH_RE.subn(', ', text)
    return fixed, n


def style_check(text: str, lang: str) -> list[str]:
    """Code-only check (no AI, no cost). Returns list of violations; empty = passed.
    Em-dash is NOT checked here — it is auto-fixed before this call.
    Only banned phrases require flagging (they need a rewrite, not a simple sub).
    """
    lower = text.lower()
    return [
        f'banned phrase: "{phrase}"'
        for phrase in BANNED_PHRASES.get(lang, [])
        if phrase in lower
    ]


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


def get_published_articles(topics: list[dict]) -> list[dict]:
    """Return list of published articles for internal linking."""
    return [
        {'title_en': t['title_en'], 'slug': slugify(t['title_en'])}
        for t in topics if t.get('status') == 'published'
    ]


def get_cluster_prior_articles(topics: list[dict], cluster: str, current_id: str) -> list[str]:
    """Return titles of already-drafted/published articles in the same cluster."""
    return [
        t['title_en']
        for t in topics
        if t.get('cluster') == cluster
        and t.get('status') in ('drafted', 'published')
        and t['id'] != current_id
    ]


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

RESEARCH_SYSTEM = (
    'You are a content researcher for a health blog about quitting nicotine.\n\n'
    'SOURCE TIER RULES (apply before including any source):\n\n'
    'TIER 1 — preferred, cite as primary:\n'
    '  Government health agencies: CDC, FDA, NIH, PubMed/PMC, WHO, NHS, gov.uk, EU equivalents.\n'
    '  Peer-reviewed journals directly: Nicotine & Tobacco Research, Addiction, JAMA, Cochrane, Lancet, BMJ.\n'
    '  Major academic medical centers: Cleveland Clinic, Mayo Clinic, Johns Hopkins, UCSF Health.\n\n'
    'TIER 2 — usable as one of several voices, never as sole source for a key figure:\n'
    '  Mass health media with editorial oversight: WebMD, Healthline, Medical News Today.\n'
    '  Rehabilitation/treatment centers (their content is marketing copy, not research).\n'
    '  Science-pop sites summarising others\' studies.\n\n'
    'TIER 3 — HARD BLOCK. Never cite, regardless of how convenient the fact:\n'
    '  ANY site that sells nicotine products (signs: shopping cart, buy button, product prices, '
    'age verification on purchase, delivery page).\n'
    '  ANY site that is itself a competing quit-nicotine app or product (signs: App Store/Google Play '
    'links, describes itself as "app to quit smoking/vaping/pouches").\n'
    '  Explicit block list: Juicefly, juicefly.com, Quit With Jones, quitwithjones.com, '
    'Jones Quit App, QuitNic app (≠ Bonevski et al. 2021 RCT in Nicotine & Tobacco Research), '
    'Tobacco Stops With Me, Smoke Free app, Kwit app.\n\n'
    'MANDATORY SOURCING RULES:\n'
    '- Every specific number must be verified by at least 2 independent TIER 1 or TIER 2 sources.\n'
    '- If sources disagree, report a range (e.g. "300,000–400,000"), not a single figure.\n'
    '- Format every fact as: [the fact] [Source: Name, Year | Tier: 1/2]\n'
    '- If a fact is only found on a Tier 3 source, search for it via a Tier 1 source instead. '
    'If not found, omit the fact entirely — absence of a figure is better than a bad source.\n'
    '- Legal/regulatory facts must include: [as of SOURCE_DATE] — these change.\n\n'
    'Summarize in English regardless of target audience.'
)


def research_shared(client: anthropic.Anthropic, topic_title: str) -> tuple[str, list[str]]:
    """One web search call for universal facts across all languages.
    Returns (facts_with_sources, list_of_langs_needing_local_research).
    """
    resp = client.messages.create(
        model=RESEARCH_MODEL,
        max_tokens=2048,
        tools=[{
            'type': 'web_search_20260209',
            'name': 'web_search',
            'max_uses': 3,
            'allowed_callers': ['direct'],
        }],
        system=RESEARCH_SYSTEM,
        messages=[{
            'role': 'user',
            'content': (
                f'Research universal facts for a blog article on: {topic_title}\n\n'
                'Gather statistics, mechanisms, scientific findings, and current data '
                'useful for someone wanting to quit nicotine. '
                'Each fact must include source name and year.\n\n'
                'On the final line, write exactly:\n'
                'NEEDS_LOCAL_RESEARCH: [comma-separated list of language codes from en/ru/de/es/fr '
                'that need country-specific research — legal status, local stats, cultural context. '
                'Write "none" if no language needs it.]'
            ),
        }],
    )
    parts = [b.text for b in resp.content if hasattr(b, 'text') and b.text]
    full_text = '\n\n'.join(parts) if parts else '(No research returned)'

    langs_for_local: list[str] = []
    for line in full_text.split('\n'):
        if line.strip().startswith('NEEDS_LOCAL_RESEARCH:'):
            codes = line.split(':', 1)[1].strip()
            if codes.lower() != 'none':
                langs_for_local = [c.strip() for c in codes.split(',') if c.strip() in LANGUAGES]
    return full_text, langs_for_local


def research_lang_specific(
    client: anthropic.Anthropic,
    topic_title: str,
    lang: str,
    shared_facts: str,
) -> str:
    """Targeted additional search for country/region-specific context — only if needed."""
    resp = client.messages.create(
        model=RESEARCH_MODEL,
        max_tokens=1024,
        tools=[{
            'type': 'web_search_20260209',
            'name': 'web_search',
            'max_uses': 2,
            'allowed_callers': ['direct'],
        }],
        system=RESEARCH_SYSTEM,
        messages=[{
            'role': 'user',
            'content': (
                f'Topic: {topic_title}\n'
                f'Target audience: {LANG_LABELS[lang]}\n\n'
                f'Universal facts already gathered:\n{shared_facts[:600]}...\n\n'
                f'Find ONLY what is specific to the {LANG_NAMES[lang]} audience and '
                'NOT covered above: local legal/regulatory status, local statistics that '
                'differ meaningfully from global numbers, cultural context. '
                'Each fact with source name and year. Skip what is already in the universal facts.'
            ),
        }],
    )
    parts = [b.text for b in resp.content if hasattr(b, 'text') and b.text]
    return '\n\n'.join(parts) if parts else ''


def audit_article(
    client: anthropic.Anthropic,
    article_text: str,
    research_facts: str,
) -> str:
    """Compare specific claims in the article against the research facts.
    Returns a markdown table: VERIFIED / DISCREPANCY / UNVERIFIED for each claim.
    No web search — cheap Haiku call.
    """
    resp = client.messages.create(
        model=RESEARCH_MODEL,
        max_tokens=1024,
        system=(
            'You are a fact-checker. Compare every specific number, percentage, '
            'statistic, and legal claim in the article against the research facts provided.\n\n'
            'For each claim found in the article:\n'
            '- VERIFIED — matches the research facts (note the source)\n'
            '- DISCREPANCY — article number differs from research (show both)\n'
            '- UNVERIFIED — not present in the research facts at all\n\n'
            'Also classify each source cited in the article by tier:\n'
            '- Tier 1: government agencies (CDC/FDA/NIH/WHO/NHS), peer-reviewed journals, '
            'major academic medical centers (Cleveland Clinic, Mayo Clinic, etc.)\n'
            '- Tier 2: health media (WebMD, Healthline), rehab centers, science-pop sites\n'
            '- Tier 3 (BLOCKED): nicotine retailers, competing quit apps — flag immediately\n\n'
            'Return a compact markdown table with columns: '
            '| Claim in article | Status | Source Tier | Source / Note |\n'
            'Quote exact text from the article. Be precise. '
            'Flag any Tier 3 source with ⚠️ BLOCKED.'
        ),
        messages=[{
            'role': 'user',
            'content': (
                f'RESEARCH FACTS PROVIDED TO WRITER:\n{research_facts}\n\n'
                f'---\n\nARTICLE TEXT:\n{article_text}'
            ),
        }],
    )
    parts = [b.text for b in resp.content if hasattr(b, 'text') and b.text]
    return '\n'.join(parts) if parts else '(Audit failed to produce output)'


def write_article(
    client: anthropic.Anthropic,
    topic_title: str,
    lang: str,
    shared_facts: str,
    lang_specific_facts: str,
    voice_guide_text: str,
    published_articles: list[dict],
    cluster_prior_articles: list[str],
) -> tuple[str, str, str]:
    facts_section = f'## Universal research facts (use ONLY these — do not add others):\n{shared_facts}'
    if lang_specific_facts:
        facts_section += f'\n\n## Additional {LANG_NAMES[lang]}-specific facts:\n{lang_specific_facts}'

    links_context = ''
    if published_articles:
        links_list = '\n'.join(f'- {a["title_en"]} (slug: {a["slug"]})' for a in published_articles)
        links_context = (
            f'\n\nALREADY PUBLISHED ARTICLES — link to these naturally where relevant:\n{links_list}'
        )

    dedup_context = ''
    if cluster_prior_articles:
        prior_list = '\n'.join(f'- {t}' for t in cluster_prior_articles)
        dedup_context = (
            f'\n\nARTICLES ALREADY WRITTEN IN THIS CLUSTER — '
            f'do NOT re-explain the same basics; link to them instead:\n{prior_list}'
        )

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
                f'{facts_section}'
                f'{links_context}'
                f'{dedup_context}\n\n'
                'Output format (exactly):\n'
                '1. Line 1: # [Article title in target language]\n'
                '2. Line 2: > [SEO meta description, 120-155 chars, in target language]\n'
                '3. Blank line, then full article body (800-1200 words)\n\n'
                f'Write natively in {LANG_NAMES[lang]}. Not a translation. '
                'Apply all rules from the system prompt. '
                'CRITICAL: Only use statistics from the research facts above. '
                'Every number you include must come from those facts with its source.'
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

def build_frontmatter(
    title: str,
    description: str,
    today: datetime.date,
    lang: str,
    slug: str,
    style_violations: list[str] | None = None,
) -> str:
    t = title.replace('"', '\\"')
    d = description.replace('"', '\\"')
    lines = [
        '---',
        f'title: "{t}"',
        f'description: "{d}"',
        f'publishDate: {today.isoformat()}',
        f'lang: {lang}',
        'draft: true',
        f'heroImage: /images/blog/{slug}.svg',
    ]
    if style_violations:
        issues = '; '.join(style_violations)
        lines.append(f'style_check: "failed — {issues}"')
    lines.append('---')
    return '\n'.join(lines)


# ── per-language pipeline (runs in parallel) ──────────────────────────────────

def process_language(
    lang: str,
    client: anthropic.Anthropic,
    topic_title: str,
    shared_facts: str,
    lang_specific: dict[str, str],
    voice_guide_txt: str,
    article_slug: str,
    today: datetime.date,
    published_articles: list[dict],
    cluster_prior_articles: list[str],
) -> str:
    lang_specific_facts = lang_specific.get(lang, '')

    print(f'[{lang}] writing...', flush=True)
    title, description, body = write_article(
        client, topic_title, lang, shared_facts, lang_specific_facts,
        voice_guide_txt, published_articles, cluster_prior_articles,
    )

    # Auto-fix em-dashes (no judgment needed).
    body, dash_count = fix_em_dashes(body)
    if dash_count:
        print(f'[{lang}] auto-fixed {dash_count} em-dash(es).', flush=True)

    # Mechanical style check (banned phrases only) — code only, no AI, no extra cost.
    violations = style_check(body, lang)
    if violations:
        print(f'[{lang}] STYLE CHECK FAILED: {violations}', flush=True)
    else:
        print(f'[{lang}] style check passed.', flush=True)

    frontmatter  = build_frontmatter(title, description, today, lang, article_slug, violations or None)
    article_text = frontmatter + '\n\n' + body + '\n'

    out_dir = BLOG_DIR / lang
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f'{article_slug}.md'
    out_path.write_text(article_text, encoding='utf-8')
    print(f'[{lang}] saved: {out_path.relative_to(REPO_ROOT)}', flush=True)

    # Fact audit (cheap, no search)
    print(f'[{lang}] auditing facts...', flush=True)
    research_for_audit = shared_facts
    if lang_specific_facts:
        research_for_audit += f'\n\n{lang_specific_facts}'

    audit_report = audit_article(client, article_text, research_for_audit)

    audit_dir = AUDIT_DIR / article_slug
    audit_dir.mkdir(parents=True, exist_ok=True)
    audit_path = audit_dir / f'{lang}.md'
    audit_path.write_text(
        f'# Fact Audit: {article_slug} ({lang.upper()})\n'
        f'Generated: {today.isoformat()}\n\n'
        f'{audit_report}\n',
        encoding='utf-8',
    )
    print(f'[{lang}] audit saved: {audit_path.relative_to(REPO_ROOT)}', flush=True)
    return lang


# ── main ──────────────────────────────────────────────────────────────────────

def draft_one(
    client: anthropic.Anthropic,
    voice_guide_txt: str,
    today: datetime.date,
) -> str | None:
    """Draft the next pending topic. Returns topic_id or None if nothing to do."""
    topics  = load_backlog()
    pending = next((t for t in topics if t.get('status') == 'pending'), None)
    if not pending:
        return None

    topic_id     = pending['id']
    topic_title  = pending['title_en']
    cluster      = pending['cluster']
    article_slug = slugify(topic_title)

    print(f'Topic  : {topic_id} — {topic_title}')
    print(f'Slug   : {article_slug}')
    print(f'Cluster: {cluster}')

    # Context for internal links + cluster dedup
    published_articles     = get_published_articles(topics)
    cluster_prior_articles = get_cluster_prior_articles(topics, cluster, topic_id)
    if cluster_prior_articles:
        print(f'Cluster prior articles: {cluster_prior_articles}')

    # SVG cover — deterministic, no API call
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    svg_path = IMAGES_DIR / f'{article_slug}.svg'
    svg_path.write_text(generate_svg(topic_id, cluster), encoding='utf-8')
    print(f'SVG    : {svg_path.relative_to(REPO_ROOT)}')

    # 1. ONE shared research call (not per-language)
    print('\nResearching (shared, 1 call)...', flush=True)
    shared_facts, langs_for_local = research_shared(client, topic_title)
    print(f'Shared research done. Local research needed: {langs_for_local or ["none"]}', flush=True)

    # Deterministic Tier-3 source check — block before any article is written.
    blocked_found = check_blocked_sources(shared_facts)
    if blocked_found:
        print(
            f'WARNING: Tier-3 (blocked) sources detected in research: {blocked_found}\n'
            'These will NOT be passed to the writer. Stripping mentions from research text.',
            flush=True,
        )
        for pat in blocked_found:
            # Remove sentences containing the blocked source so the writer never sees them.
            sentences = shared_facts.split('. ')
            shared_facts = '. '.join(
                s for s in sentences if pat not in s.lower()
            )

    # 2. Targeted local searches — only for languages that need it
    lang_specific: dict[str, str] = {}
    for lang in langs_for_local:
        print(f'Researching local context [{lang}]...', flush=True)
        extra = research_lang_specific(client, topic_title, lang, shared_facts)
        if extra:
            lang_specific[lang] = extra
            print(f'Local context [{lang}] done.', flush=True)

    # Mark in_progress so concurrent runs skip this topic
    pending['status'] = 'in_progress'
    save_backlog(topics)

    # 3. Write + audit all 5 languages in parallel
    with ThreadPoolExecutor(max_workers=len(LANGUAGES)) as executor:
        futures = {
            executor.submit(
                process_language,
                lang, client, topic_title, shared_facts, lang_specific,
                voice_guide_txt, article_slug, today, published_articles, cluster_prior_articles,
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
        topics = load_backlog()
        t = next((t for t in topics if t['id'] == topic_id), None)
        if t:
            t['status'] = 'pending'
            save_backlog(topics)
        raise RuntimeError(f'Failed to draft {topic_id}')

    # Mark drafted
    topics = load_backlog()
    topic  = next(t for t in topics if t['id'] == topic_id)
    topic['status'] = 'drafted'
    topic.setdefault('published', {})
    save_backlog(topics)

    print(f'Done   : {topic_id} drafted in {len(LANGUAGES)} languages.')
    return topic_id


def main() -> None:
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print('ERROR: ANTHROPIC_API_KEY is not set.', file=sys.stderr)
        sys.exit(1)

    client          = anthropic.Anthropic(api_key=api_key)
    voice_guide_txt = VOICE_GUIDE.read_text(encoding='utf-8')
    today           = datetime.date.today()

    drafted_ids: list[str] = []
    for i in range(BATCH_SIZE):
        print(f'\n── Batch {i + 1}/{BATCH_SIZE} ──────────────────────────────')
        try:
            topic_id = draft_one(client, voice_guide_txt, today)
        except RuntimeError as exc:
            print(f'ERROR: {exc}', file=sys.stderr)
            sys.exit(1)
        if topic_id is None:
            print('No pending topics remaining.')
            break
        drafted_ids.append(topic_id)

    if not drafted_ids:
        print('Nothing drafted. Exiting.')
        sys.exit(0)

    gh_env = os.environ.get('GITHUB_ENV')
    if gh_env:
        with open(gh_env, 'a', encoding='utf-8') as f:
            f.write(f'DRAFTED_IDS={",".join(drafted_ids)}\n')

    print(f'\nTotal drafted: {len(drafted_ids)} topic(s): {", ".join(drafted_ids)}')


if __name__ == '__main__':
    main()
