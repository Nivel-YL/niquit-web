#!/usr/bin/env python3
"""Retroactive steps 4-5 audit for the 16 articles written before the steps
4-6 pipeline existed (everything in the backlog except E-02). Does not
regenerate any content and does not run step 6: no auto-fix, no removal, no
GitHub Issue escalation, only flags findings in a report for manual review.

For each topic: one fresh research_shared() call, exactly as for a new
article, produces a real numbered fact list (F1, F2, ...); then the
standard, unmodified audit_article() runs per language against whatever
file is already on disk right now (current content, including any manual
fixes made earlier); then the standard, unmodified cross_language_consistency()
checks the resulting source tables against each other. All three functions
are imported from blog_editor.py unchanged, this script only orchestrates.

Caveat, stated up front rather than discovered afterward: the fresh research
pass is an independent new search over the topic, not a targeted
re-verification of this specific article's existing claims. A claim marked
UNVERIFIED in a report's PART 1 means this fresh pass did not happen to
re-surface a matching fact, not necessarily that the claim is false. Source
tier/UNK flags in PART 2 do not carry this caveat, those check the actual
cited source directly via web_search, independent of the research pass.
Locale-specific facts that originally came from a separate targeted
per-language research call (research_lang_specific) are not replicated here,
only the one shared call, so a legitimate local-only fact may also surface
as UNVERIFIED for that same reason, not because it is wrong.
"""

import datetime
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import anthropic
from slugify import slugify

from blog_editor import (
    AUDIT_DIR,
    BLOG_DIR,
    LANGUAGES,
    REPO_ROOT,
    audit_article,
    cross_language_consistency,
    load_backlog,
    research_shared,
)

# Requested order: live articles with unconfirmed deep cross-language checks
# first, then live articles already manually source-checked (run for the
# record), then unpublished drafts last.
RETRO_ORDER = [
    'B-01', 'B-02', 'B-04', 'C-01', 'C-02',
    'A-01', 'A-02', 'A-03', 'A-04', 'B-03',
    'C-03', 'C-04', 'D-01', 'D-02', 'D-03', 'E-01',
]


def _audit_one_lang(client: anthropic.Anthropic, lang: str, slug: str, shared_facts: str):
    path = BLOG_DIR / lang / f'{slug}.md'
    if not path.exists():
        return lang, None, f'file not found: {path.relative_to(REPO_ROOT)}'
    full_text = path.read_text(encoding='utf-8')
    audit_text, source_table = audit_article(client, full_text, shared_facts)
    return lang, {'audit_text': audit_text, 'source_table': source_table}, None


def retro_audit_topic(client: anthropic.Anthropic, topic: dict) -> dict:
    slug = slugify(topic['title_en'])
    print(f'\n=== {topic["id"]}: {topic["title_en"]} ===', flush=True)

    print('  researching (fresh, shared, same as for a new article)...', flush=True)
    shared_facts, _ = research_shared(client, topic['title_en'])

    lang_results: dict[str, dict] = {}
    errors: dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=len(LANGUAGES)) as executor:
        futures = {
            executor.submit(_audit_one_lang, client, lang, slug, shared_facts): lang
            for lang in LANGUAGES
        }
        for future in as_completed(futures):
            lang, result, error = future.result()
            if error:
                errors[lang] = error
                print(f'  [{lang}] SKIPPED: {error}', file=sys.stderr)
            else:
                lang_results[lang] = result
                flagged = [r for r in result['source_table'] if r.get('status', '').startswith('flag:')]
                print(f'  [{lang}] audited, {len(flagged)} flagged source(s)', flush=True)

    lang_tables = {lang: r['source_table'] for lang, r in lang_results.items()}
    cross_findings = cross_language_consistency(lang_tables)
    print(f'  cross-language mismatches: {len(cross_findings)}', flush=True)

    return {
        'topic_id': topic['id'],
        'title': topic['title_en'],
        'slug': slug,
        'lang_results': lang_results,
        'errors': errors,
        'cross_findings': cross_findings,
    }


def write_topic_report(result: dict, today: datetime.date) -> Path:
    slug = result['slug']
    out_dir = AUDIT_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / '_retroactive_audit_report.md'

    lines = [
        f'# Retroactive steps 4-5 audit: {result["topic_id"]} — {result["title"]}',
        f'Generated: {today.isoformat()}',
        '',
        'This article was written before the steps 4-6 pipeline existed. This report '
        'uses one fresh research_shared() call (same as for a new article) checked '
        'against the article text already on disk, no regeneration, step 6 auto-fix '
        'was NOT run. A claim marked UNVERIFIED below means this fresh research pass '
        'did not happen to re-surface a matching fact, not necessarily that the claim '
        'is false; source tier/UNK flags do not carry that caveat, those check the '
        'cited source directly via web_search. All findings here are flags for manual '
        'review, nothing was changed in the article files.',
        '',
    ]

    if result['errors']:
        lines.append('Missing files: ' + ', '.join(f'{l} ({e})' for l, e in result['errors'].items()))
        lines.append('')

    lines.append(f'## Cross-language mismatches: {len(result["cross_findings"])}')
    if result['cross_findings']:
        for f in result['cross_findings']:
            names = {lang: row['source_name'] for lang, row in f['per_lang'].items()}
            lines.append(f'- {f["fact_id"]}: {names}')
    else:
        lines.append('(none)')
    lines.append('')

    for lang, r in result['lang_results'].items():
        flagged = [row for row in r['source_table'] if row.get('status', '').startswith('flag:')]
        lines.append(f'## [{lang}] {len(flagged)} flagged source(s)')
        if flagged:
            for row in flagged:
                lines.append(f'- tier {row.get("tier")}, {row.get("status")}: "{row.get("source_name")}"')
                lines.append(f'  > {row.get("quote")}')
        else:
            lines.append('(none)')
        lines.append('')
        lines.append(f'<details><summary>[{lang}] full audit output</summary>\n\n{r["audit_text"]}\n\n</details>')
        lines.append('')

    out_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'  report saved: {out_path.relative_to(REPO_ROOT)}', flush=True)
    return out_path


def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ['git', *args], cwd=REPO_ROOT, capture_output=True, text=True,
    )


def _configure_git_identity() -> None:
    _git('config', 'user.name', 'Retro Audit Bot')
    _git('config', 'user.email', 'jelissei.levin@gmail.com')


def commit_and_push(paths: list[str], message: str) -> bool:
    """Stage and commit exactly the given paths, then push, right after each
    topic finishes, not batched at the end. A failure here means the run may
    still be usable up to the last successful push (each topic pushes on its
    own), instead of losing every completed topic if a later one crashes,
    which is what happened the first time this script hit an API usage cap
    partway through B-04 and lost B-01 and B-02's already-finished results.
    Returns True if a commit was made and pushed (or there was nothing new to
    commit), False if git itself failed.
    """
    add = _git('add', *paths)
    if add.returncode != 0:
        print(f'  WARNING: git add failed: {add.stderr.strip()}', file=sys.stderr)
        return False

    diff = _git('diff', '--cached', '--quiet')
    if diff.returncode == 0:
        print('  (nothing new to commit)', flush=True)
        return True

    commit = _git('commit', '-m', message)
    if commit.returncode != 0:
        print(f'  WARNING: git commit failed: {commit.stderr.strip()}', file=sys.stderr)
        return False

    pull = _git('pull', '--rebase', 'origin', 'master')
    if pull.returncode != 0:
        print(f'  WARNING: git pull --rebase failed: {pull.stderr.strip()}', file=sys.stderr)
        return False

    push = _git('push')
    if push.returncode != 0:
        print(f'  WARNING: git push failed: {push.stderr.strip()}', file=sys.stderr)
        return False

    print(f'  committed and pushed: {message}', flush=True)
    return True


RESULTS_LOG_PATH = AUDIT_DIR / '_retroactive_audit_results.json'


def _read_results_log() -> dict:
    if not RESULTS_LOG_PATH.exists():
        return {}
    try:
        return json.loads(RESULTS_LOG_PATH.read_text(encoding='utf-8'))
    except (ValueError, OSError):
        return {}


def _record_result(result: dict, today: datetime.date) -> None:
    """Update the persistent results log with this one topic, then re-render
    the combined summary from the full accumulated log, not just this run's
    in-memory results. This is what makes resuming in separate batches
    (as requested: B-04/C-01/C-02 first, then A-01-04/B-03, then the 6
    drafts) actually work, each batch is a separate script invocation with
    its own empty `results` list, so the summary must read prior batches'
    entries back from disk rather than only knowing about the current one.
    """
    total_flagged = sum(
        len([row for row in lr['source_table'] if row.get('status', '').startswith('flag:')])
        for lr in result['lang_results'].values()
    )
    log = _read_results_log()
    log[result['topic_id']] = {
        'title': result['title'],
        'slug': result['slug'],
        'flagged': total_flagged,
        'cross_mismatches': len(result['cross_findings']),
        'date': today.isoformat(),
    }
    RESULTS_LOG_PATH.write_text(json.dumps(log, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    _write_summary_from_log(log, today)


def _write_summary_from_log(log: dict, today: datetime.date) -> Path:
    out_path = AUDIT_DIR / '_retroactive_audit_summary.md'
    lines = [
        '# Retroactive steps 4-5 audit: summary across all pre-steps-4-6 topics',
        f'Last updated: {today.isoformat()}',
        f'Progress: {len(log)}/{len(RETRO_ORDER)} topics audited so far.',
        '',
        'Order: B-01, B-02, B-04, C-01, C-02 (live, deep cross-language check not yet '
        'confirmed) first; then A-01, A-02, A-03, A-04, B-03 (live, already manually '
        'source-checked against primary sources earlier, run here for the record and a '
        'unified report); then C-03, C-04, D-01, D-02, D-03, E-01 (unpublished drafts) '
        'last. Step 6 was not run: findings below are flags for manual review, not '
        'applied fixes.',
        '',
    ]
    for topic_id in RETRO_ORDER:
        entry = log.get(topic_id)
        if not entry:
            lines.append(f'- **{topic_id}**: not yet audited')
            continue
        lines.append(
            f'- **{topic_id}** ({entry["title"]}): {entry["flagged"]} flagged source(s) across '
            f'languages, {entry["cross_mismatches"]} cross-language mismatch(es). '
            f'[Full report](./{entry["slug"]}/_retroactive_audit_report.md)'
        )
    out_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'  summary updated: {out_path.relative_to(REPO_ROOT)}', flush=True)
    return out_path


def main() -> None:
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print('ERROR: ANTHROPIC_API_KEY is not set.', file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    today = datetime.date.today()
    topics_by_id = {t['id']: t for t in load_backlog()}

    requested = os.environ.get('RETRO_TOPICS', '').strip()
    order = [t.strip() for t in requested.split(',') if t.strip()] if requested else RETRO_ORDER

    _configure_git_identity()

    done = 0
    for topic_id in order:
        topic = topics_by_id.get(topic_id)
        if not topic:
            print(f'WARNING: {topic_id} not found in backlog, skipping', file=sys.stderr)
            continue
        result = retro_audit_topic(client, topic)
        report_path = write_topic_report(result, today)
        _record_result(result, today)
        commit_and_push(
            [
                str(report_path.relative_to(REPO_ROOT)),
                str(RESULTS_LOG_PATH.relative_to(REPO_ROOT)),
                'docs/fact-audits/_retroactive_audit_summary.md',
            ],
            message=f'retro-audit: {topic_id}',
        )
        done += 1

    print(f'\nDone: retroactively audited {done}/{len(order)} topic(s).')


if __name__ == '__main__':
    main()
