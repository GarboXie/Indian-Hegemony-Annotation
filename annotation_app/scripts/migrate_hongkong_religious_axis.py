"""Add Religious Hegemony columns to the Hong Kong sheet. Default: check only."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def migration_requests(worksheets, headers):
    added = [header for header in headers if header.endswith(('_religious', '_religious_impact'))]
    previous = [header for header in headers if header not in added]
    requests = []
    for worksheet in worksheets:
        actual = worksheet.row_values(1)
        if actual not in (previous, headers):
            raise ValueError(f'{worksheet.title}: unexpected headers; no changes made.')
        print(f'{worksheet.title}: {len(actual)} -> {len(headers)} columns')
        if actual == headers:
            continue

        # Insert from right to left so earlier column indices stay valid.
        for header in reversed(added[::2]):
            index = sum(item not in added for item in headers[:headers.index(header)])
            requests.append({'insertDimension': {'range': {
                'sheetId': worksheet.id, 'dimension': 'COLUMNS',
                'startIndex': index, 'endIndex': index + 2,
            }}})
        requests.append({'updateCells': {
            'start': {'sheetId': worksheet.id, 'rowIndex': 0, 'columnIndex': 0},
            'rows': [{'values': [{'userEnteredValue': {'stringValue': h}} for h in headers]}],
            'fields': 'userEnteredValue',
        }})
    return requests


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    from config import HEADERS
    from sheets import _open_study_sheet, MAIN_SHEET, BACKUP_SHEET

    spreadsheet = _open_study_sheet()
    worksheets = [spreadsheet.worksheet(name) for name in (MAIN_SHEET, BACKUP_SHEET)]
    requests = migration_requests(worksheets, HEADERS)
    if not args.apply:
        print('CHECK ONLY: no spreadsheet changes made.')
        return
    if requests:
        spreadsheet.batch_update({'requests': requests})
    for worksheet in worksheets:
        if worksheet.row_values(1) != HEADERS:
            raise RuntimeError(f'{worksheet.title}: header verification failed.')
    print('Verified both annotation worksheets; religious columns are ready.')


if __name__ == '__main__':
    main()
