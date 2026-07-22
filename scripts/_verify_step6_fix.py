#!/usr/bin/env python3
"""One-off verification, not part of the normal pipeline.

Re-runs the exact 9 real flagged citations that corrupted the E-02 pilot
draft on 2026-07-22 (workflow run 29910219492) through the fixed
find_replacement_source_with_attempts, against the real Anthropic API, and
confirms the result is always either the literal string REMOVE or a
validated single clean sentence, never a reasoning trace. Read-only: does
not write to any article file.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import anthropic

import blog_editor as be

REPO_ROOT = Path(__file__).parent.parent

EN_ARTICLE = (
    REPO_ROOT / 'src/content/blog/en/does-smoking-actually-reduce-stress-the-real-science.md'
).read_text(encoding='utf-8')
FR_ARTICLE = (
    REPO_ROOT / 'src/content/blog/fr/does-smoking-actually-reduce-stress-the-real-science.md'
).read_text(encoding='utf-8')

CASES = [
    ('en', 'Quitsure',
     'About an hour after smoking, nicotine levels drop enough to trigger the early stages of '
     'withdrawal, irritability, restlessness, trouble concentrating, a low hum of tension, '
     'according to health education platform Quitsure', EN_ARTICLE),
    ('en', 'Neurolaunch',
     'Neurolaunch, a health research platform, describes it plainly', EN_ARTICLE),
    ('en', 'NHS via APC Birmingham',
     'In the UK, the NHS goes further, stating that for some people, quitting smoking can be as '
     'effective as antidepressants at easing feelings of sadness, hopelessness, and isolation, '
     'according to reporting from APC Birmingham in 2022', EN_ARTICLE),
    ('en', 'University of Wisconsin Center for Tobacco Research',
     'Research from the University of Wisconsin Center for Tobacco Research, published in the '
     'journal Addiction in 2010', EN_ARTICLE),
    ('en', 'University of Wisconsin Center for Tobacco Research',
     'That same study found people with anxiety diagnoses were significantly less likely to quit '
     'successfully', EN_ARTICLE),
    ('fr', 'Quitsure', "d'après la plateforme Quitsure", FR_ARTICLE),
    ('fr', 'NHS',
     'Le NHS britannique va même plus loin : arrêter de fumer peut être aussi efficace que '
     "certains antidépresseurs pour réduire la tristesse, le sentiment d'isolement et la perte "
     "d'espoir, comme le rapporte APC Birmingham en 2022.", FR_ARTICLE),
    ('fr', 'University of Wisconsin',
     "Une étude du Center for Tobacco Research de l'université du Wisconsin, publiée dans la "
     'revue Addiction en 2010', FR_ARTICLE),
    ('fr', 'University of Wisconsin', 'La même étude montre', FR_ARTICLE),
]


def main() -> None:
    client = anthropic.Anthropic()
    passed = 0
    failed = 0

    for i, (lang, source_name, quote, article_text) in enumerate(CASES, start=1):
        print(f'\n=== Case {i}/9: [{lang}] "{source_name}" ===', flush=True)
        result, malformed = be.find_replacement_source_with_attempts(
            client, lang, quote, source_name, article_text, max_attempts=2,
        )
        is_remove = result.strip().upper() == 'REMOVE'
        is_clean = be._looks_like_clean_sentence(result.strip())
        ok = is_remove or is_clean
        print(f'  malformed_seen={malformed}', flush=True)
        print(f'  result ({len(result)} chars): {result!r}', flush=True)
        print(f'  {"PASS" if ok else "FAIL: result is neither REMOVE nor a validated clean sentence"}', flush=True)
        if ok:
            passed += 1
        else:
            failed += 1

    print(f'\n=== SUMMARY: {passed}/9 passed, {failed}/9 failed ===', flush=True)
    if failed:
        sys.exit(1)


if __name__ == '__main__':
    main()
