#!/usr/bin/env python3
"""Generates PIPELINE_STATUS.md: a human-readable snapshot of the blog pipeline,
framed as a production line (raw materials -> workshop -> QC -> finished goods
warehouse -> shipping), because each section maps to one real, already-existing
pipeline stage, not decoration on top of the same data.

Read-only over BLOG_TOPIC_BACKLOG.md and the docs/fact-audits/ logs. Does not
change anything in the steps 1-6 pipeline logic in blog_editor.py or the
publish logic in publisher.py; both simply call write_pipeline_status() once
at the end of their own run.
"""

import datetime
import json
import re
from pathlib import Path

import yaml
from slugify import slugify

REPO_ROOT        = Path(__file__).parent.parent
BACKLOG_PATH      = REPO_ROOT / 'BLOG_TOPIC_BACKLOG.md'
STATUS_PATH       = REPO_ROOT / 'PIPELINE_STATUS.md'
AUDIT_DIR         = REPO_ROOT / 'docs' / 'fact-audits'
PILOT_LOG_PATH    = AUDIT_DIR / '_pilot_runs_log.json'
PILOT_RUN_TARGET  = 3

BACKLOG_RE = re.compile(r'<!--BACKLOG\n(.*?)BACKLOG-->', re.DOTALL)

_WEEKDAY_NAMES_RU = [
    'понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота', 'воскресенье',
]


def load_backlog() -> list[dict]:
    content = BACKLOG_PATH.read_text(encoding='utf-8')
    m = BACKLOG_RE.search(content)
    if not m:
        raise RuntimeError(f'No <!--BACKLOG ... BACKLOG--> block in {BACKLOG_PATH}')
    return yaml.safe_load(m.group(1))['topics']


def _read_pilot_log() -> list[dict]:
    if not PILOT_LOG_PATH.exists():
        return []
    try:
        return json.loads(PILOT_LOG_PATH.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, ValueError):
        return []


def record_pilot_run(
    article_slug: str,
    today: datetime.date,
    counted: bool = True,
    note: str = '',
) -> int:
    """Append one entry to the pilot log (docs/fact-audits/_pilot_runs_log.json)
    and return the running count of entries with counted=True. A run only
    records counted=True at the time it happens, since the pipeline itself
    has no way to know in advance that a later code change will invalidate it;
    invalidating a past entry (as happened once already, see the log itself)
    is a deliberate, manual edit of this file, not something automated.
    """
    log = _read_pilot_log()
    log.append({
        'date': today.isoformat(),
        'slug': article_slug,
        'counted': counted,
        'note': note,
    })
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    PILOT_LOG_PATH.write_text(json.dumps(log, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return sum(1 for e in log if e.get('counted'))


def _next_weekly_utc(
    weekday: int, hour: int, minute: int, now: datetime.datetime,
) -> datetime.datetime:
    """Next occurrence of a given ISO weekday (Monday=0) at hour:minute UTC,
    strictly after `now`.
    """
    candidate = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    candidate += datetime.timedelta(days=(weekday - now.weekday()) % 7)
    if candidate <= now:
        candidate += datetime.timedelta(days=7)
    return candidate


def _fmt_utc(dt: datetime.datetime) -> str:
    return f'{_WEEKDAY_NAMES_RU[dt.weekday()]}, {dt.strftime("%Y-%m-%d %H:%M")} UTC'


def _latest_published_date(topic: dict) -> str:
    dates = [d for d in topic.get('published', {}).values() if d]
    return max(dates) if dates else ''


def write_pipeline_status() -> None:
    topics = load_backlog()
    now = datetime.datetime.utcnow()

    pending     = [t for t in topics if t.get('status') == 'pending']
    in_progress = [t for t in topics if t.get('status') == 'in_progress']
    drafted     = [t for t in topics if t.get('status') == 'drafted']
    approved    = [t for t in topics if t.get('status') == 'approved']
    published   = [t for t in topics if t.get('status') == 'published']

    lines: list[str] = []
    lines.append('# NiQuit Blog Pipeline: производственная линия')
    lines.append(f'Обновлено автоматически: {now.strftime("%Y-%m-%d %H:%M")} UTC')
    lines.append('')
    lines.append(
        'Склад сырья → Цех (research + написание, 5 языков) → ОТК (источники →\n'
        'между языками → автоисправление) → Склад готовой продукции (approved) →\n'
        'Отгрузка (публикация)'
    )
    lines.append('')

    lines.append(f'## Склад сырья: темы в резерве (pending), {len(pending)}')
    if pending:
        for t in pending:
            lines.append(f'- {t["id"]}: {t["title_en"]}')
    else:
        lines.append('(пусто)')
    lines.append('')

    in_work_total = len(drafted) + len(in_progress)
    lines.append(f'## Цех и ОТК: в работе, {in_work_total}')
    if in_work_total:
        for t in in_progress:
            lines.append(f'- {t["id"]}: {t["title_en"]} — в цехе, идёт генерация (in_progress)')
        for t in drafted:
            slug = slugify(t['title_en'])
            report_path = AUDIT_DIR / slug / '_source_verification_report.md'
            stage = (
                'прошла ОТК (аудит источников, шаги 4-6), см. отчёт'
                if report_path.exists()
                else 'черновик готов, написан до внедрения ОТК шагов 4-6 (отчёта нет)'
            )
            lines.append(f'- {t["id"]}: {t["title_en"]} — {stage}')
    else:
        lines.append('(пусто)')
    lines.append('')

    lines.append(f'## Склад готовой продукции: одобрено, в очереди (approved), {len(approved)}')
    if approved:
        for t in approved:
            lines.append(f'- {t["id"]}: {t["title_en"]}')
    else:
        lines.append('(пусто)')
    lines.append('')

    if published:
        last_topic = max(published, key=_latest_published_date)
        last_date = _latest_published_date(last_topic)
        lines.append(f'## Отгружено всего: {len(published)}, последняя отгрузка {last_date} ({last_topic["id"]})')
    else:
        lines.append('## Отгружено всего: 0')
    lines.append('')

    next_editor  = _next_weekly_utc(0, 9, 0, now)  # blog-editor.yml: Mon 09:00 UTC
    next_pub_tue = _next_weekly_utc(1, 8, 0, now)  # publisher.yml:   Tue 08:00 UTC
    next_pub_fri = _next_weekly_utc(4, 8, 0, now)  # publisher.yml:   Fri 08:00 UTC
    next_pub = min(next_pub_tue, next_pub_fri)

    lines.append('## Следующая смена по расписанию')
    lines.append(f'- Генерация (blog-editor): {_fmt_utc(next_editor)}')
    lines.append(f'- Отгрузка (publisher): {_fmt_utc(next_pub)}')
    lines.append('')

    pilot_log = _read_pilot_log()
    counted_so_far = sum(1 for e in pilot_log if e.get('counted'))
    lines.append(
        f'## Приёмка новой линии (пилотный счётчик): '
        f'{min(counted_so_far, PILOT_RUN_TARGET)} из {PILOT_RUN_TARGET} чистых прогонов'
    )
    if pilot_log:
        for e in pilot_log:
            status = 'засчитан' if e.get('counted') else 'НЕ засчитан'
            note = f' — {e["note"]}' if e.get('note') else ''
            lines.append(f'- {e["date"]} ({e["slug"]}): {status}{note}')
    else:
        lines.append('(пока нет ни одной попытки)')

    STATUS_PATH.write_text('\n'.join(lines) + '\n', encoding='utf-8')


if __name__ == '__main__':
    write_pipeline_status()
    print(f'Wrote {STATUS_PATH.relative_to(REPO_ROOT)}')
