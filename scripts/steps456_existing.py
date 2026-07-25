#!/usr/bin/env python3
"""Run steps 4-6 (audit, cross-language consistency, step-6 auto-fix/remove/
escalate) against articles ALREADY WRITTEN, without regenerating content.
Two distinct modes in one script, both needed right now for a real reason:

1. Targeted remediation (E-02, languages ru/de/es only): E-02's original
   steps 4-6 run completed successfully for EN and FR (already fixed:
   Quitsure removed, Neurolaunch and APC Birmingham reattributed), but its
   RU/DE/ES audits silently lost every finding to a max_tokens truncation
   bug (fixed in audit_article()). Those three languages still carry the
   exact same unfixed Quitsure/Neurolaunch/APC-Birmingham-equivalent
   citations live in the draft. This mode re-audits ONLY the given
   languages with the now-fixed pipeline and runs step 6 on whatever it
   finds. It writes a supplementary report and replaces the three
   languages' now-corrected raw audit dumps, it does not touch EN/FR's
   files, the main _source_verification_report.md, or the pilot-run log,
   this is a bug-fix remediation of an existing topic, not a fresh pilot
   candidate.

2. First-time full pipeline (C-03, C-04, D-01, D-02, D-03, E-01, all 5
   languages): these were drafted before the steps 4-6 pipeline existed and
   have never been audited in any form, not even the steps-4-5-only
   retroactive audit. Uses the standard, unmodified
   run_source_verification_pipeline() and write_source_verification_report(),
   exactly as a brand-new topic would, including pilot-run tracking, since
   these are genuinely going through the new pipeline for the first time.
"""

import datetime
import os
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
    _line_number_of,
    _reload_and_fix,
    audit_article,
    create_github_issue,
    cross_language_consistency,
    find_replacement_source_with_attempts,
    load_backlog,
    research_shared,
    run_source_verification_pipeline,
    with_retries,
    write_source_verification_report,
)
from retro_audit import commit_and_push, _configure_git_identity


def _save_audit_dump(slug: str, lang: str, audit_text: str, today: datetime.date) -> None:
    out_dir = AUDIT_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f'{lang}.md'
    out_path.write_text(
        f'# Fact Audit: {slug} ({lang})\nGenerated: {today.isoformat()}\n\n{audit_text}\n',
        encoding='utf-8',
    )


def _audit_one_lang(client: anthropic.Anthropic, lang: str, slug: str, shared_facts: str):
    path = BLOG_DIR / lang / f'{slug}.md'
    if not path.exists():
        return lang, None, f'file not found: {path.relative_to(REPO_ROOT)}'
    article_text = path.read_text(encoding='utf-8')
    audit_text, source_table = with_retries(audit_article, client, article_text, shared_facts)
    return lang, {'out_path': path, 'source_table': source_table, 'audit_text': audit_text}, None


def remediate_langs(client: anthropic.Anthropic, topic: dict, langs: list[str], today: datetime.date) -> dict:
    """Targeted re-audit + step 6 for specific languages of a topic whose
    original audit was lost to the truncation bug. Does not touch the
    existing _source_verification_report.md or the pilot-run log.
    """
    slug = slugify(topic['title_en'])
    print(f'\n=== {topic["id"]} remediation: {topic["title_en"]} (langs: {", ".join(langs)}) ===', flush=True)

    print('  researching (fresh, shared across the languages being fixed)...', flush=True)
    shared_facts, _ = research_shared(client, topic['title_en'])

    lang_results: dict[str, dict] = {}
    for lang in langs:
        path = BLOG_DIR / lang / f'{slug}.md'
        article_text = path.read_text(encoding='utf-8')
        audit_text, source_table = with_retries(audit_article, client, article_text, shared_facts)
        flagged = [r for r in source_table if r.get('status', '').startswith('flag:')]
        print(f'  [{lang}] audited, {len(flagged)} flagged source(s)', flush=True)
        lang_results[lang] = {'out_path': path, 'source_table': source_table}
        _save_audit_dump(slug, lang, audit_text, today)

    lang_tables = {lang: r['source_table'] for lang, r in lang_results.items()}
    cross_findings = cross_language_consistency(lang_tables)
    print(f'  cross-language mismatches among {langs}: {len(cross_findings)}', flush=True)

    cross_fact_ids = {f['fact_id'] for f in cross_findings}
    worklist: list[tuple[str, dict]] = []
    seen: set[tuple[str, str]] = set()
    for lang, rows in lang_tables.items():
        for row in rows:
            key = (lang, row['quote'])
            if key in seen:
                continue
            if row.get('status', '').startswith('flag:') or row.get('fact_id') in cross_fact_ids:
                seen.add(key)
                worklist.append((lang, row))

    fixed: list[dict] = []
    unresolved: list[dict] = []
    for lang, row in worklist:
        out_path = lang_results[lang]['out_path']
        article_text = out_path.read_text(encoding='utf-8')
        result, malformed = find_replacement_source_with_attempts(
            client, lang, row['quote'], row['source_name'], article_text, max_attempts=2,
        )
        applied = _reload_and_fix(out_path, row['quote'], result)
        record = {'lang': lang, 'source_name': row['source_name'], 'tier': row.get('tier'), 'quote': row['quote']}
        if applied:
            record['resolution'] = 'removed' if result.strip().upper() == 'REMOVE' else f'reattributed: {result.strip()}'
            fixed.append(record)
            print(f'  [{lang}] fixed "{row["source_name"]}": {record["resolution"]}', flush=True)
        else:
            record['error'] = 'could not locate the flagged sentence in the saved file'
            unresolved.append(record)
            print(f'  [{lang}] COULD NOT FIX "{row["source_name"]}": {record["error"]}', flush=True)

    escalated: list[str] = []
    for record in unresolved:
        if record.get('tier') not in ('3', 'UNK'):
            continue
        out_path = lang_results[record['lang']]['out_path']
        line_no = _line_number_of(out_path.read_text(encoding='utf-8'), record['quote'])
        title = f'[blog-pipeline] Unresolved {record["tier"]} source in {slug} ({record["lang"]}) [remediation]'
        body = (
            f'Article: `{out_path.relative_to(REPO_ROOT)}`\n'
            f'Line: {line_no if line_no else "not found"}\n\n'
            f'Flagged source: **{record["source_name"]}** (tier {record["tier"]})\n\n'
            f'Flagged sentence:\n> {record["quote"]}\n\n'
            f'Context: targeted remediation of {slug} for {", ".join(langs)} after the audit-'
            f'truncation bug was fixed. Automated fix attempt did not resolve cleanly '
            f'({record["error"]}). Needs manual edit.\n'
        )
        issue_url = create_github_issue(title, body)
        if issue_url:
            escalated.append(issue_url)
            print(f'  Escalated to {issue_url}', flush=True)

    report_path = AUDIT_DIR / slug / '_remediation_ru_de_es_report.md'
    lines = [
        f'# Targeted remediation: {slug} ({", ".join(langs)})',
        f'Generated: {today.isoformat()}',
        '',
        f'The original steps 4-6 run truncated its audit for {", ".join(langs)} (max_tokens bug, '
        'now fixed), so step 6 found nothing to act on in those languages even though they carried '
        'the same Quitsure/Neurolaunch/APC-Birmingham-equivalent issues already fixed in EN/FR. '
        'This report covers only the re-audit and fix of the languages named above; '
        '_source_verification_report.md documents the original EN/FR results, unchanged.',
        '',
        f'## Cross-language mismatches among {", ".join(langs)}: {len(cross_findings)}',
    ]
    for f in cross_findings:
        names = {lang: row['source_name'] for lang, row in f['per_lang'].items()}
        lines.append(f'- {f["fact_id"]}: {names}')
    lines.append('')
    lines.append(f'## Fixed: {len(fixed)}')
    for r in fixed:
        lines.append(f'- [{r["lang"]}] "{r["source_name"]}" -> {r["resolution"]}')
    lines.append('')
    lines.append(f'## Unresolved: {len(unresolved)}')
    for r in unresolved:
        lines.append(f'- [{r["lang"]}] "{r["source_name"]}" (tier {r["tier"]}): {r["error"]}')
    if escalated:
        lines.append('')
        lines.append('## Escalated to GitHub Issues:')
        for url in escalated:
            lines.append(f'- {url}')
    report_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'  remediation report saved: {report_path.relative_to(REPO_ROOT)}', flush=True)

    return {'fixed': fixed, 'unresolved': unresolved, 'escalated': escalated, 'cross_findings': cross_findings}


def run_full_pipeline_on_existing(client: anthropic.Anthropic, topic: dict, today: datetime.date) -> dict:
    """Full steps 4-6 against an already-written article, all 5 languages,
    for a topic that has never been audited in any form before.
    """
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
                _save_audit_dump(slug, lang, result['audit_text'], today)

    print('  running cross-language consistency + step 6 (auto-fix/remove)...', flush=True)
    report = run_source_verification_pipeline(client, slug, lang_results, today)
    write_source_verification_report(slug, report, today)
    return {'slug': slug, 'report': report, 'errors': errors}


def main() -> None:
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print('ERROR: ANTHROPIC_API_KEY is not set.', file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    today = datetime.date.today()
    topics_by_id = {t['id']: t for t in load_backlog()}

    _configure_git_identity()

    # 1. Targeted remediation: E-02, ru/de/es only.
    e02 = topics_by_id['E-02']
    slug = slugify(e02['title_en'])
    remediate_langs(client, e02, ['ru', 'de', 'es'], today)
    commit_and_push(
        [
            f'src/content/blog/ru/{slug}.md',
            f'src/content/blog/de/{slug}.md',
            f'src/content/blog/es/{slug}.md',
            f'docs/fact-audits/{slug}/ru.md',
            f'docs/fact-audits/{slug}/de.md',
            f'docs/fact-audits/{slug}/es.md',
            f'docs/fact-audits/{slug}/_remediation_ru_de_es_report.md',
        ],
        message='steps4-6: E-02 remediation (ru/de/es)',
    )

    # 2. First-time full steps 4-6 for the 6 never-audited drafts.
    for topic_id in ['C-03', 'C-04', 'D-01', 'D-02', 'D-03', 'E-01']:
        topic = topics_by_id[topic_id]
        result = run_full_pipeline_on_existing(client, topic, today)
        topic_slug = result['slug']
        paths = [f'src/content/blog/{lang}/{topic_slug}.md' for lang in LANGUAGES]
        paths += [f'docs/fact-audits/{topic_slug}/{lang}.md' for lang in LANGUAGES]
        paths += [
            f'docs/fact-audits/{topic_slug}/_source_verification_report.md',
            'docs/fact-audits/_pilot_runs_log.json',
        ]
        commit_and_push(paths, message=f'steps4-6: {topic_id} (first full audit)')

    print('\nDone.')


if __name__ == '__main__':
    main()
