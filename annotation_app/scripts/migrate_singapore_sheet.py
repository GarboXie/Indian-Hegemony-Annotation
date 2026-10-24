"""Explicit, backed-up migration of Singapore Sheet columns. Default: read only."""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def migration_requests(sheet_id, old_headers, new_headers):
    """Delete only geography columns, then rename remaining headers atomically."""
    removed = [i for i, header in enumerate(old_headers) if header in {"region", "state"}]
    if len(old_headers) - len(removed) != len(new_headers):
        raise ValueError("Unexpected column count; migration stopped.")
    requests = [
        {"deleteDimension": {"range": {
            "sheetId": sheet_id, "dimension": "COLUMNS",
            "startIndex": i, "endIndex": i + 1,
        }}}
        for i in reversed(removed)
    ]
    requests.append({"updateCells": {
        "start": {"sheetId": sheet_id, "rowIndex": 0, "columnIndex": 0},
        "rows": [{"values": [{"userEnteredValue": {"stringValue": h}} for h in new_headers]}],
        "fields": "userEnteredValue",
    }})
    return requests


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true', help='Back up and apply the migration.')
    args = parser.parse_args()
    from config import DATA_DIR, HEADERS, LEGACY_HEADERS, NEUTRAL_HEADERS
    from sheets import _open_study_sheet, REVIEW_HEADERS, LEGACY_REVIEW_HEADERS

    spreadsheet = _open_study_sheet()
    targets = [
        ('testing', HEADERS, (LEGACY_HEADERS, NEUTRAL_HEADERS, HEADERS)),
        ('testing2', HEADERS, (LEGACY_HEADERS, NEUTRAL_HEADERS, HEADERS)),
        ('testreview', REVIEW_HEADERS, (LEGACY_REVIEW_HEADERS, REVIEW_HEADERS)),
    ]
    snapshots, requests, expected_rows = {}, [], {}
    for name, target, allowed in targets:
        ws = spreadsheet.worksheet(name)
        values = ws.get_all_values()
        old = values[0] if values else []
        if old not in allowed:
            raise ValueError(f'{name}: unrecognized headers; no changes made.')
        if any(len(row) > len(old) for row in values):
            raise ValueError(f'{name}: extra populated columns; no changes made.')
        snapshots[name] = values
        keep = [i for i, h in enumerate(old) if h not in {'region', 'state'}]
        expected_rows[name] = [
            [(row[i] if i < len(row) else '') for i in keep]
            for row in values[1:]
        ]
        print(f'{name}: {len(old)} -> {len(target)} columns; {len(values) - 1} data rows')
        if old != target:
            requests.extend(migration_requests(ws.id, old, target))

    if not args.apply:
        print('CHECK ONLY: no spreadsheet changes made.')
        return
    if not requests:
        print('Already migrated; no changes needed.')
        return

    backup_dir = DATA_DIR / 'migration_backups'
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    backup = backup_dir / f'sheet_before_model_names_{stamp}.json'
    backup.touch(mode=0o600, exist_ok=False)
    backup.write_text(json.dumps({'spreadsheet_id': spreadsheet.id, 'worksheets': snapshots}, ensure_ascii=False), encoding='utf-8')
    # All three worksheets change in one Google Sheets atomic batch request.
    spreadsheet.batch_update({'requests': requests})
    for name, target, _ in targets:
        values = spreadsheet.worksheet(name).get_all_values()
        if not values or values[0] != target:
            raise RuntimeError(f'{name}: header verification failed. Backup: {backup}')
        actual = [row + [''] * (len(target) - len(row)) for row in values[1:]]
        if actual != expected_rows[name]:
            raise RuntimeError(f'{name}: data verification failed. Backup: {backup}')
    print(f'Backup saved privately: {backup}')
    print('Migration verified: model-name headers, no region/state columns, all other data preserved.')


if __name__ == '__main__':
    main()
