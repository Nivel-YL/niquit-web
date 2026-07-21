#!/usr/bin/env python3
"""Automated blog editor for niquit.app.

Architecture (per topic):
  1. ONE shared research call     -> universal numbered facts with sources + tiers,
                                      detects which langs need local context
  2. Targeted local searches      -> only for languages that actually need
                                      country-specific data
  3. 5 parallel write calls       -> each gets shared facts + its local addon
  4. 5 parallel audit calls       -> independent, search-backed fact + source audit
                                      per language file (see AUDIT_SYSTEM)
  5. Cross-language consistency   -> after all 5 languages exist, flag any fact
                                      whose named source disagrees across languages
  6. Self-correction + escalation -> up to 2 search-backed attempts to re-attribute
                                      (or remove) each flagged citation; unresolved
                                      Tier-3 findings open a GitHub Issue
"""

import datetime
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import anthropic
import yaml
from slugify import slugify

# -- paths --------------------------------------------------------------------

REPO_ROOT    = Path(__file__).parent.parent
BLOG_DIR     = REPO_ROOT / 'src' / 'content' / 'blog'
IMAGES_DIR   = REPO_ROOT / 'public' / 'images' / 'blog'
BACKLOG_PATH = REPO_ROOT / 'BLOG_TOPIC_BACKLOG.md'
VOICE_GUIDE  = REPO_ROOT / 'docs' / 'CONTENT_VOICE_GUIDE.md'
AUDIT_DIR    = REPO_ROOT / 'docs' / 'fact-audits'

# -- config ---------------------------------------------------------------------

RESEARCH_MODEL = 'claude-haiku-4-5'   # research + audit + fix: speed and cost
WRITE_MODEL    = 'claude-sonnet-5'    # article writing: quality matters

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

# -- blocked sources (Tier 3, hard block, never cite regardless of convenience) --
# Rule: never cite a site that sells nicotine products OR is a competing quit app.
# Source: AI_EDITOR_SOURCE_VETTING_SPEC.md
# This is a fast, free, pre-write filter. The independent post-write audit below
# (AUDIT_SYSTEM) is what actually catches names not on this fixed list.

BLOCKED_SOURCES: list[str] = [
    # Nicotine retailers
    'juicefly', 'juicefly.com',
    # Competing quit apps / products
    'quitwithjones', 'jones quit', 'jones quit app', 'quit with jones',
    'quitnic',        # competing app, not the 2021 Bonevski RCT in Nicotine & Tobacco Research
    'smoke free app', 'smokefreeglobal',
    'kwit app', 'kwit.app',
    'tobaccostopswithme', 'tobacco stops with me',  # nicotine sales / quit-product hybrid
    'the ex program', 'ex program',   # Truth Initiative's own cessation app, not the org itself
    'villa treatment center',         # for-profit rehab clinic, content written to attract clients
    'ethra',                          # harm-reduction advocacy group's own self-selected survey
    'charlie health',                 # for-profit telehealth mental-health treatment provider
    'quit smoking advisor',           # affiliate site monetizing quit-program comparisons
    'quit smoking community',         # The EX Program's own community page
    "allen carr's easyway", 'allen carr easyway', 'allen carr\'s easy way',  # paid quit-smoking program
]

# Human-readable names for the same entries (matched case-insensitively in research text).
BLOCKED_SOURCE_PATTERNS: list[str] = [s.lower() for s in BLOCKED_SOURCES]


def check_blocked_sources(text: str) -> list[str]:
    """Scan research text for blocked Tier-3 sources.
    Returns list of blocked names found; empty list = clean.
    """
    lower = text.lower()
    return [pat for pat in BLOCKED_SOURCE_PATTERNS if pat in lower]


# -- mechanical style rules (no AI, binary pass/fail) --------------------------
# These are checked by code after writing, before saving.
# Source: CONTENT_VOICE_GUIDE.md section 2 (em-dash) and section 4 (banned patterns).

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
    Em-dash is NOT checked here; it is auto-fixed before this call.
    Only banned phrases require flagging (they need a rewrite, not a simple sub).
    """
    lower = text.lower()
    return [
        f'banned phrase: "{phrase}"'
        for phrase in BANNED_PHRASES.get(lang, [])
        if phrase in lower
    ]


# Source: CONTENT_VOICE_GUIDE.md body-length requirement.
WORD_COUNT_MIN = 800
WORD_COUNT_MAX = 1200


def word_count_check(text: str) -> list[str]:
    """Code-only check (no AI, no cost). Flags drafts outside the required word range.
    Catches silent short-generation failures (e.g. a language coming back at a fraction
    of the required length) that would otherwise only surface on manual review.
    """
    count = len(text.split())
    if count < WORD_COUNT_MIN or count > WORD_COUNT_MAX:
        return [f'word count {count} outside required {WORD_COUNT_MIN}-{WORD_COUNT_MAX} range']
    return []


# -- backlog --------------------------------------------------------------------

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


# -- SVG cover --------------------------------------------------------------------

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


# -- retry helper -----------------------------------------------------------------

def with_retries(fn, *args, max_attempts: int = 3, **kwargs):
    """Call fn(*args, **kwargs) up to max_attempts times with exponential backoff."""
    for attempt in range(max_attempts):
        try:
            return fn(*args, **kwargs)
        except Exception as exc:
            if attempt < max_attempts - 1:
                wait = 2 ** attempt  # 1s, 2s
                print(f'  [retry {attempt + 1}/{max_attempts - 1}] {exc}, retrying in {wait}s', flush=True)
                time.sleep(wait)
            else:
                raise


# -- Claude calls -------------------------------------------------------------------

RESEARCH_SYSTEM = (
    'You are a content researcher for a health blog about quitting nicotine.\n\n'
    'SOURCE TIER RULES (apply before including any source):\n\n'
    'TIER 1, preferred, cite as primary:\n'
    '  Government health agencies: CDC, FDA, NIH, PubMed/PMC, WHO, NHS, gov.uk, EU equivalents.\n'
    '  Peer-reviewed journals directly: Nicotine & Tobacco Research, Addiction, JAMA, Cochrane, Lancet, BMJ.\n'
    '  Major academic medical centers: Cleveland Clinic, Mayo Clinic, Johns Hopkins, UCSF Health.\n\n'
    'TIER 2, usable as one of several voices, never as sole source for a key figure:\n'
    '  Mass health media with editorial oversight: WebMD, Healthline, Medical News Today.\n'
    '  Rehabilitation/treatment centers (their content is marketing copy, not research).\n'
    '  Science-pop sites summarising others\' studies.\n\n'
    'TIER 3, HARD BLOCK. Never cite, regardless of how convenient the fact:\n'
    '  ANY site that sells nicotine products (signs: shopping cart, buy button, product prices, '
    'age verification on purchase, delivery page).\n'
    '  ANY site that is itself a competing quit-nicotine app or product (signs: App Store/Google Play '
    'links, describes itself as "app to quit smoking/vaping/pouches").\n'
    '  Explicit block list: Juicefly, juicefly.com, Quit With Jones, quitwithjones.com, '
    'Jones Quit App, QuitNic app (not the Bonevski et al. 2021 RCT in Nicotine & Tobacco Research), '
    'Tobacco Stops With Me, Smoke Free app, Kwit app, The EX Program (Truth Initiative\'s own '
    'cessation app, note that the organization itself is Tier 1, this product is not), Villa '
    'Treatment Center, ETHRA (a harm-reduction advocacy group\'s own self-selected survey, not an '
    'independent source), Charlie Health, Quit Smoking Advisor, Quit Smoking Community, '
    'Allen Carr\'s Easyway.\n\n'
    'MANDATORY SOURCING RULES:\n'
    '- Every specific number must be verified by at least 2 independent TIER 1 or TIER 2 sources.\n'
    '- If sources disagree, report a range (e.g. "300,000-400,000"), not a single figure.\n'
    '- Format every fact as: [the fact] [Source: Name, Year | Tier: 1/2]\n'
    '- If a fact is only found on a Tier 3 source, search for it via a Tier 1 source instead. '
    'If not found, omit the fact entirely, absence of a figure is better than a bad source.\n'
    '- Legal/regulatory facts must include: [as of SOURCE_DATE], these change.\n\n'
    'Summarize in English regardless of target audience.'
)


def research_shared(client: anthropic.Anthropic, topic_title: str) -> tuple[str, list[str]]:
    """One web search call for universal facts across all languages.
    Returns (facts_with_sources, list_of_langs_needing_local_research).
    Facts are numbered (F1, F2, ...) so the post-write audit and the cross-language
    consistency check can both refer to "the same fact" by a stable id.
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
                'Format each fact as a numbered line, starting at F1 then F2, F3, and so on: '
                '"F1. [the fact]. [Source: Name, Year | Tier: 1/2]". '
                'Each fact must include source name, year, and tier.\n\n'
                'On the final line, write exactly:\n'
                'NEEDS_LOCAL_RESEARCH: [comma-separated list of language codes from en/ru/de/es/fr '
                'that need country-specific research, legal status, local stats, cultural context. '
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
    """Targeted additional search for country/region-specific context, only if needed."""
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


# -- step 4: independent, search-backed fact + source audit -----------------------

AUDIT_SYSTEM = (
    'You are an independent fact and source auditor for a health blog about quitting nicotine. '
    'You did not write this article, treat it with fresh scrutiny rather than confirming it.\n\n'
    'PART 1, fact accuracy: compare every specific number, percentage, statistic, and legal claim '
    'in the article against the research facts provided (each numbered F1, F2, and so on). '
    'For each claim: VERIFIED (matches, note the fact number), DISCREPANCY (article differs from '
    'research, show both), or UNVERIFIED (not present in the research facts at all).\n\n'
    'PART 2, source tier, for EVERY named source cited in the article, not just ones tied to a '
    'numbered fact:\n'
    'TIER 1: government health agencies (CDC, FDA, NIH, PubMed/PMC, WHO, NHS, gov.uk, EU equivalents), '
    'peer-reviewed journals by name (Nicotine & Tobacco Research, Addiction, JAMA, Cochrane, Lancet, '
    'BMJ), major academic medical centers (Cleveland Clinic, Mayo Clinic, Johns Hopkins, UCSF Health).\n'
    'TIER 2: mass health media with editorial oversight (WebMD, Healthline, Medical News Today), '
    'named explicitly as one voice among several, never the sole source of a key figure.\n'
    'TIER 3, hard block: any site that sells nicotine products (cart, buy button, price, age '
    'verification, delivery page) or is itself a competing quit-nicotine app or product (App Store, '
    'Google Play links, self-describes as an app or program to quit smoking, vaping, or pouches). '
    'Known examples: Juicefly, Quit With Jones, QuitNic app, Tobacco Stops With Me, Smoke Free app, '
    'Kwit app, The EX Program, Villa Treatment Center, ETHRA, Charlie Health, Quit Smoking Advisor, '
    'Quit Smoking Community, Allen Carr\'s Easyway.\n\n'
    'If a cited source is not obviously one of the well-known Tier 1 examples above, a government '
    'agency, a named peer-reviewed journal, or a named major academic medical center, you MUST use '
    'web_search to check it before classifying: does this domain or organization actually exist, is '
    'it genuinely related to nicotine, health, or addiction rather than an unrelated business, and '
    'does it show retailer or competing-product signals as described above. Do not classify an '
    'unfamiliar source from memory alone. If a source cannot be confirmed to exist, or turns out to '
    'be unrelated to the topic, mark its tier as UNK and flag it. This is a distinct problem from '
    'Tier 3, it is not necessarily a competitor, it may simply not be real or not relevant, but it '
    'must be flagged the same way.\n\n'
    'Output BOTH of the following, in this order.\n\n'
    'First, a compact markdown table for a human to skim, columns: '
    '| Claim in article | Status | Source Tier | Source / Note |. '
    'Flag any Tier 3 or UNK source with a BLOCKED note.\n\n'
    'Second, a machine-readable block, exactly in this format, one line per sentence in the article '
    'that names a source (whether or not it is tied to a numbered fact):\n'
    '===SOURCE_TABLE===\n'
    'fact_id|source_name|tier|status|exact_quote\n'
    '===END_SOURCE_TABLE===\n\n'
    'Where fact_id is the F-number this claim traces back to in the research facts, or NONE if the '
    'claim is not tied to a numbered fact; tier is 1, 2, 3, or UNK; status is exactly "ok" if there '
    'is no issue, or "flag:short-reason-no-spaces" if tier is 3 or UNK; and exact_quote is the '
    'verbatim sentence from the article containing the citation, copied exactly, not paraphrased '
    '(this is used to locate and fix the sentence programmatically). Use the literal pipe character '
    '| as the field separator and do not use it inside any field.'
)

SOURCE_TABLE_RE = re.compile(
    r'===SOURCE_TABLE===\s*\n(.*?)\n===END_SOURCE_TABLE===',
    re.DOTALL,
)


def parse_source_table(audit_text: str) -> list[dict]:
    """Parse the machine-readable source table block from an audit response.
    Format per line: fact_id|source_name|tier|status|quote
    Returns [] if the block is missing or malformed; callers must treat that as
    "could not verify", not as "everything is fine".
    """
    m = SOURCE_TABLE_RE.search(audit_text)
    if not m:
        return []
    rows = []
    for line in m.group(1).splitlines():
        line = line.strip()
        if not line or line.startswith('fact_id') or line.startswith('#'):
            continue
        parts = line.split('|', 4)
        if len(parts) != 5:
            continue
        fact_id, source_name, tier, status, quote = (p.strip() for p in parts)
        rows.append({
            'fact_id': fact_id,
            'source_name': source_name,
            'tier': tier,
            'status': status,
            'quote': quote.strip('"'),
        })
    return rows


def audit_article(
    client: anthropic.Anthropic,
    article_text: str,
    research_facts: str,
) -> tuple[str, list[dict]]:
    """Independent fact + source audit, with real web search access. Unlike a purely
    memory-based self-check, this can actually verify whether an unfamiliar source
    exists and what kind of site it is.
    Returns (human_readable_report, parsed_source_table).
    """
    resp = client.messages.create(
        model=RESEARCH_MODEL,
        max_tokens=2048,
        tools=[{
            'type': 'web_search_20260209',
            'name': 'web_search',
            'max_uses': 6,
            'allowed_callers': ['direct'],
        }],
        system=AUDIT_SYSTEM,
        messages=[{
            'role': 'user',
            'content': (
                f'RESEARCH FACTS PROVIDED TO WRITER:\n{research_facts}\n\n'
                f'---\n\nARTICLE TEXT:\n{article_text}'
            ),
        }],
    )
    parts = [b.text for b in resp.content if hasattr(b, 'text') and b.text]
    full_text = '\n'.join(parts) if parts else '(Audit failed to produce output)'
    return full_text, parse_source_table(full_text)


# -- step 6: search-backed self-correction ------------------------------------------

FIX_SYSTEM = (
    'You are fixing a single flagged source citation in a nicotine-cessation blog article, '
    'written in {lang_name}. Find the primary source for the exact same factual claim, verified '
    'via web_search, not from memory. Prefer a source ALREADY cited elsewhere in the article below '
    'over introducing a new name, if it genuinely supports the same claim. The underlying fact '
    'itself must not change, only who it is attributed to.\n\n'
    'If you find a legitimate Tier 1 or Tier 2 source, per the standard tier rules for this '
    'project (government health agencies, named peer-reviewed journals, major academic medical '
    'centers, or mass health media as one of several voices) that actually supports this specific '
    'claim, respond with ONLY the corrected sentence, written in {lang_name}, ready to directly '
    'replace the flagged sentence in the article verbatim. No commentary, no quotation marks '
    'around it, just the sentence.\n\n'
    'If after searching you cannot find any legitimate primary source for this specific claim, '
    'respond with exactly: REMOVE\n'
    'and nothing else.'
)


def find_replacement_source(
    client: anthropic.Anthropic,
    lang: str,
    flagged_quote: str,
    flagged_source: str,
    article_text: str,
) -> str:
    """Search-equipped fix attempt for a single flagged citation.
    Returns either a corrected sentence, or the literal string 'REMOVE'.
    """
    resp = client.messages.create(
        model=RESEARCH_MODEL,
        max_tokens=512,
        tools=[{
            'type': 'web_search_20260209',
            'name': 'web_search',
            'max_uses': 3,
            'allowed_callers': ['direct'],
        }],
        system=FIX_SYSTEM.format(lang_name=LANG_NAMES[lang]),
        messages=[{
            'role': 'user',
            'content': (
                f'Flagged sentence (exact quote): "{flagged_quote}"\n'
                f'Flagged source: {flagged_source}\n\n'
                f'Full article, for finding a source already used elsewhere in it:\n{article_text}'
            ),
        }],
    )
    parts = [b.text for b in resp.content if hasattr(b, 'text') and b.text]
    result = (parts[-1] if parts else '').strip()
    return result or 'REMOVE'


def find_replacement_source_with_attempts(
    client: anthropic.Anthropic,
    lang: str,
    flagged_quote: str,
    flagged_source: str,
    article_text: str,
    max_attempts: int = 2,
) -> str:
    """Up to max_attempts independent search-backed tries to find a real replacement
    source for the same fact. A single attempt answering REMOVE is not the final
    word, a second independent search may still turn up a legitimate source, only
    remove after every attempt agrees (or errors out).
    """
    last = 'REMOVE'
    for attempt in range(max_attempts):
        try:
            last = find_replacement_source(client, lang, flagged_quote, flagged_source, article_text)
        except Exception as exc:
            print(f'  [fix attempt {attempt + 1}/{max_attempts}] search failed: {exc}', flush=True)
            last = 'REMOVE'
            continue
        if last.strip().upper() != 'REMOVE':
            return last
    return last


def split_frontmatter(article_text: str) -> tuple[str, str]:
    """Split a saved draft file into (frontmatter_block_including_dashes, body)."""
    m = re.match(r'(---\n.*?\n---\n)\n*(.*)', article_text, re.DOTALL)
    if not m:
        return '', article_text
    return m.group(1), m.group(2)


def apply_quote_fix(body: str, old_quote: str, new_text: str) -> tuple[str, bool]:
    """Replace old_quote with new_text inside body (or delete it if new_text is REMOVE).
    Tries an exact match first, falls back to a whitespace/non-breaking-space-tolerant
    match, since quotes copied by a model can differ from the source file only in
    whitespace. Returns (new_body, applied).
    """
    replacement = '' if new_text.strip().upper() == 'REMOVE' else new_text

    if old_quote in body:
        return body.replace(old_quote, replacement, 1), True

    pattern = re.escape(old_quote)
    pattern = re.sub(r'(?:\\ )+', r'[\\s\\u00a0]+', pattern)
    m = re.search(pattern, body)
    if m:
        return body[:m.start()] + replacement + body[m.end():], True

    return body, False


def _reload_and_fix(out_path: Path, old_quote: str, new_text: str) -> bool:
    """Re-read the saved draft from disk (it may have been touched by an earlier fix
    in this same run), apply the fix to its body only, and write it back if applied.
    """
    current = out_path.read_text(encoding='utf-8')
    frontmatter, body = split_frontmatter(current)
    new_body, applied = apply_quote_fix(body, old_quote, new_text)
    if applied:
        out_path.write_text(frontmatter + '\n' + new_body.strip() + '\n', encoding='utf-8')
    return applied


def _line_number_of(text: str, needle: str) -> int | None:
    idx = text.find(needle)
    if idx == -1:
        return None
    return text.count('\n', 0, idx) + 1


# -- step 5: cross-language consistency --------------------------------------------

def cross_language_consistency(lang_tables: dict[str, list[dict]]) -> list[dict]:
    """Flag facts where 2+ languages each cite a NAMED source for the same fact_id, but
    the names do not all match, either in count or in the specific name at equal count.
    Does not flag a language simply not citing a fact at all; that is a coverage
    difference, out of scope here, only disagreement among languages that DO name a
    source for the same fact is flagged. This rule was checked against every real
    incident found in this project's audit history before being adopted: the dominant
    real pattern is one differing name per language at equal count (e.g. "Quit Smoking
    Advisor" in one language, "Quit Smoking Community" in another, for the same claim),
    not a difference in how many sources are named.
    """
    by_fact: dict[str, dict[str, dict]] = {}
    for lang, rows in lang_tables.items():
        for row in rows:
            fact_id = row.get('fact_id', 'NONE')
            if not fact_id or fact_id.upper() == 'NONE':
                continue
            by_fact.setdefault(fact_id, {})[lang] = row

    findings = []
    for fact_id, per_lang in by_fact.items():
        if len(per_lang) < 2:
            continue
        names = {row['source_name'].strip().lower() for row in per_lang.values()}
        if len(names) > 1:
            findings.append({
                'fact_id': fact_id,
                'per_lang': per_lang,  # {lang: row}
            })
    return findings


# -- step 6: escalation ------------------------------------------------------------

def create_github_issue(title: str, body: str) -> str | None:
    """Create a GitHub issue via the REST API using the Actions-provided GITHUB_TOKEN.
    Never raises, a failed escalation should not crash the whole run, it is only logged.
    Returns the issue URL, or None if it could not be created.
    """
    token = os.environ.get('GITHUB_TOKEN')
    repo  = os.environ.get('GITHUB_REPOSITORY')
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


# -- pilot-run tracking -------------------------------------------------------------
# The first few topics to go through steps 4-6 are marked as pilot runs in their
# report so a human can manually spot-check correctness and actual added API cost
# before trusting this fully, per the operator's explicit request.

PILOT_COUNTER_PATH = AUDIT_DIR / '_pilot_runs_completed.txt'
PILOT_RUN_TARGET   = 3


def _read_pilot_count() -> int:
    try:
        return int(PILOT_COUNTER_PATH.read_text(encoding='utf-8').strip())
    except (FileNotFoundError, ValueError):
        return 0


def _increment_pilot_count() -> int:
    count = _read_pilot_count() + 1
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    PILOT_COUNTER_PATH.write_text(str(count), encoding='utf-8')
    return count


# -- steps 4-6 orchestration --------------------------------------------------------

def run_source_verification_pipeline(
    client: anthropic.Anthropic,
    article_slug: str,
    lang_results: dict[str, dict],
) -> dict:
    """Steps 4-6: cross-language consistency check, then up to 2 search-backed fix
    attempts per flagged citation, then GitHub Issue escalation for any Tier-3 finding
    still unresolved. Returns a summary dict used to build the report file.
    """
    lang_tables = {lang: r['source_table'] for lang, r in lang_results.items()}
    cross_findings = cross_language_consistency(lang_tables)
    cross_fact_ids = {f['fact_id'] for f in cross_findings}

    # Build the worklist: (lang, row) for every row needing a look.
    worklist: list[tuple[str, dict]] = []
    seen: set[tuple[str, str]] = set()

    def _add(lang: str, row: dict) -> None:
        key = (lang, row['quote'])
        if key not in seen:
            seen.add(key)
            worklist.append((lang, row))

    for lang, rows in lang_tables.items():
        for row in rows:
            if row.get('status', '').startswith('flag:'):
                _add(lang, row)
            elif row.get('fact_id') in cross_fact_ids:
                # Not independently flagged by its own language's audit, but involved
                # in a real cross-language disagreement, a per-language audit call can
                # be fooled into rubber-stamping a bad source (this is exactly how
                # QuitNic got VERIFIED earlier in this project's history), so every
                # participant in a confirmed disagreement gets a second, search-backed
                # look too, not only the ones already self-flagged.
                _add(lang, row)

    fixed: list[dict] = []
    unresolved: list[dict] = []

    for lang, row in worklist:
        out_path = lang_results[lang]['out_path']
        article_text = out_path.read_text(encoding='utf-8')

        result = find_replacement_source_with_attempts(
            client, lang, row['quote'], row['source_name'], article_text,
            max_attempts=2,
        )
        applied = _reload_and_fix(out_path, row['quote'], result)

        record = {
            'lang': lang,
            'fact_id': row.get('fact_id'),
            'source_name': row['source_name'],
            'tier': row.get('tier'),
            'quote': row['quote'],
        }
        if applied:
            record['resolution'] = (
                'removed' if result.strip().upper() == 'REMOVE' else f'reattributed: {result.strip()}'
            )
            fixed.append(record)
            print(f'[{lang}] fixed flagged source "{row["source_name"]}": {record["resolution"]}', flush=True)
        else:
            record['error'] = 'could not locate the flagged sentence in the saved file'
            unresolved.append(record)
            print(f'[{lang}] COULD NOT FIX flagged source "{row["source_name"]}": {record["error"]}', flush=True)

    # Escalate only unresolved Tier-3 (hard block) findings. Unresolved Tier-2/UNK
    # findings are still recorded in the report below for a human to see on manual
    # review, but do not open an issue.
    escalated: list[str] = []
    for record in unresolved:
        if record.get('tier') != '3':
            continue
        out_path = lang_results[record['lang']]['out_path']
        current_text = out_path.read_text(encoding='utf-8')
        line_no = _line_number_of(current_text, record['quote'])
        title = f'[blog-pipeline] Unresolved Tier-3 source in {article_slug} ({record["lang"]})'
        body = (
            f'Article: `{out_path.relative_to(REPO_ROOT)}`\n'
            f'Line: {line_no if line_no else "not found, the quote may no longer match the file exactly"}\n\n'
            f'Flagged source: **{record["source_name"]}** (Tier 3, hard block)\n\n'
            f'Flagged sentence:\n> {record["quote"]}\n\n'
            f'What was already tried: an automated, search-backed fix attempt was made and did '
            f'not resolve cleanly ({record["error"]}). This needs a manual edit.\n'
        )
        issue_url = create_github_issue(title, body)
        if issue_url:
            escalated.append(issue_url)
            print(f'Escalated to {issue_url}', flush=True)

    pilot_count = _increment_pilot_count()
    return {
        'cross_language_findings': cross_findings,
        'fixed': fixed,
        'unresolved': unresolved,
        'escalated_issues': escalated,
        'pilot_run_number': pilot_count if pilot_count <= PILOT_RUN_TARGET else None,
    }


def write_source_verification_report(article_slug: str, report: dict, today: datetime.date) -> None:
    lines = [f'# Source verification report: {article_slug}', f'Generated: {today.isoformat()}', '']

    if report['pilot_run_number']:
        lines += [
            f'PILOT RUN {report["pilot_run_number"]}/{PILOT_RUN_TARGET}: this topic went through '
             'the new independent source-verification and self-correction pipeline for the first '
             f'{PILOT_RUN_TARGET} times since it was deployed. Please manually spot-check this '
             'article\'s sources and compare the actual added API cost in the console before '
             'relying on this fully.',
            '',
        ]

    lines.append(f'Cross-language mismatches found: {len(report["cross_language_findings"])}')
    for f in report['cross_language_findings']:
        names = {lang: row['source_name'] for lang, row in f['per_lang'].items()}
        lines.append(f'- {f["fact_id"]}: {names}')
    lines.append('')

    lines.append(f'Fixed automatically: {len(report["fixed"])}')
    for r in report['fixed']:
        lines.append(f'- [{r["lang"]}] "{r["source_name"]}" -> {r["resolution"]}')
    lines.append('')

    lines.append(f'Unresolved: {len(report["unresolved"])}')
    for r in report['unresolved']:
        lines.append(f'- [{r["lang"]}] "{r["source_name"]}" (tier {r["tier"]}): {r["error"]}')
    lines.append('')

    if report['escalated_issues']:
        lines.append('Escalated to GitHub Issues:')
        for url in report['escalated_issues']:
            lines.append(f'- {url}')

    out = AUDIT_DIR / article_slug / '_source_verification_report.md'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'Source verification report saved: {out.relative_to(REPO_ROOT)}', flush=True)


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
    facts_section = f'## Universal research facts (use ONLY these, do not add others):\n{shared_facts}'
    if lang_specific_facts:
        facts_section += f'\n\n## Additional {LANG_NAMES[lang]}-specific facts:\n{lang_specific_facts}'

    links_context = ''
    if published_articles:
        links_list = '\n'.join(f'- {a["title_en"]} (slug: {a["slug"]})' for a in published_articles)
        links_context = (
            f'\n\nALREADY PUBLISHED ARTICLES, link to these naturally where relevant:\n{links_list}'
        )

    dedup_context = ''
    if cluster_prior_articles:
        prior_list = '\n'.join(f'- {t}' for t in cluster_prior_articles)
        dedup_context = (
            f'\n\nARTICLES ALREADY WRITTEN IN THIS CLUSTER, '
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

    text_blocks = [b.text for b in resp.content if b.type == 'text']
    if not text_blocks:
        raise RuntimeError(f'API returned no text block for [{lang}] write call')
    text = text_blocks[0].strip()

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


# -- frontmatter --------------------------------------------------------------------

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
        lines.append(f'style_check: "failed, {issues}"')
    lines.append('---')
    return '\n'.join(lines)


# -- per-language pipeline (runs in parallel) ---------------------------------------

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
) -> dict:
    lang_specific_facts = lang_specific.get(lang, '')

    print(f'[{lang}] writing...', flush=True)
    title, description, body = with_retries(
        write_article,
        client, topic_title, lang, shared_facts, lang_specific_facts,
        voice_guide_txt, published_articles, cluster_prior_articles,
    )

    # Auto-fix em-dashes (no judgment needed).
    body, dash_count = fix_em_dashes(body)
    if dash_count:
        print(f'[{lang}] auto-fixed {dash_count} em-dash(es).', flush=True)

    # Mechanical style check (banned phrases + word count), code only, no AI, no extra cost.
    violations = style_check(body, lang) + word_count_check(body)
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

    # Step 4: independent, search-backed fact + source audit.
    print(f'[{lang}] auditing facts and sources...', flush=True)
    research_for_audit = shared_facts
    if lang_specific_facts:
        research_for_audit += f'\n\n{lang_specific_facts}'

    audit_report, source_table = with_retries(audit_article, client, article_text, research_for_audit)

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

    return {
        'lang': lang,
        'out_path': out_path,
        'source_table': source_table,
    }


# -- main -----------------------------------------------------------------------------

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

    print(f'Topic  : {topic_id}, {topic_title}')
    print(f'Slug   : {article_slug}')
    print(f'Cluster: {cluster}')

    # Context for internal links + cluster dedup
    published_articles     = get_published_articles(topics)
    cluster_prior_articles = get_cluster_prior_articles(topics, cluster, topic_id)
    if cluster_prior_articles:
        print(f'Cluster prior articles: {cluster_prior_articles}')

    # SVG cover, deterministic, no API call
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    svg_path = IMAGES_DIR / f'{article_slug}.svg'
    svg_path.write_text(generate_svg(topic_id, cluster), encoding='utf-8')
    print(f'SVG    : {svg_path.relative_to(REPO_ROOT)}')

    # 1. ONE shared research call (not per-language)
    print('\nResearching (shared, 1 call)...', flush=True)
    shared_facts, langs_for_local = research_shared(client, topic_title)
    print(f'Shared research done. Local research needed: {langs_for_local or ["none"]}', flush=True)

    # Deterministic Tier-3 source check, blocks before any article is written.
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

    # 2. Targeted local searches, only for languages that need it
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
    lang_results: dict[str, dict] = {}
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
            lang = futures[future]
            try:
                lang_results[lang] = future.result()
            except Exception as exc:
                errors.append((lang, exc))

    if errors:
        for lang, exc in errors:
            print(f'ERROR [{lang}]: {exc}', file=sys.stderr)
        topics = load_backlog()
        t = next((t for t in topics if t['id'] == topic_id), None)
        if t:
            t['status'] = 'pending'
            save_backlog(topics)
        raise RuntimeError(f'Failed to draft {topic_id}')

    # 5-6. Cross-language consistency, self-correction, escalation.
    print('\nRunning cross-language consistency check and self-correction...', flush=True)
    report = run_source_verification_pipeline(client, article_slug, lang_results)
    write_source_verification_report(article_slug, report, today)

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
        print(f'\n-- Batch {i + 1}/{BATCH_SIZE} --------------------------------')
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
