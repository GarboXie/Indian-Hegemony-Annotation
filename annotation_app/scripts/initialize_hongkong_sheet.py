"""Initialize a new Hong Kong spreadsheet without relabeling existing data."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def initialize_worksheets(spreadsheet, annotation_headers, review_headers):
    targets = {'testing': annotation_headers, 'testing2': annotation_headers, 'testreview': review_headers}
    existing = {ws.title: ws for ws in spreadsheet.worksheets()}
    # Preflight every existing target before creating or updating anything.
    for name, headers in targets.items():
        if name not in existing:
            continue
        values = existing[name].get_all_values()
        has_content = any(any(str(cell).strip() for cell in row) for row in values)
        if has_content and values[0] != headers:
            raise ValueError(f'{name}: unexpected data or headers; no worksheets changed.')
    for name, headers in targets.items():
        ws = existing.get(name)
        if ws is None:
            ws = spreadsheet.add_worksheet(title=name, rows=2000, cols=len(headers))
        if ws.row_values(1) != headers:
            ws.resize(cols=max(ws.col_count, len(headers)))
            ws.update(range_name='A1', values=[headers], value_input_option='RAW')
        if ws.row_values(1) != headers:
            raise RuntimeError(f'{name}: header verification failed.')
        print(f'{name}: verified {len(headers)} columns')


def main():
    import gspread
    from config import GOOGLE_CREDS_PATH, SHEET_ID, SHEET_NAME, HEADERS, REVIEW_HEADERS
    if not SHEET_ID:
        raise RuntimeError('Set HONGKONG_SHEET_ID to the new Hong Kong spreadsheet ID.')
    spreadsheet = gspread.service_account(filename=str(GOOGLE_CREDS_PATH)).open_by_key(SHEET_ID)
    if spreadsheet.title != SHEET_NAME:
        raise RuntimeError(f'The dedicated Hong Kong sheet must be named {SHEET_NAME}.')
    initialize_worksheets(spreadsheet, HEADERS, REVIEW_HEADERS)


if __name__ == '__main__':
    main()
