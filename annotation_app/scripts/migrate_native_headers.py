"""Rename Identity headers in the configured Google spreadsheet."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def main():
    from sheets import (
        BACKUP_SHEET, HEADERS, MAIN_SHEET, REVIEW_HEADERS, REVIEW_SHEET,
        _ensure_sheet_headers, _worksheet,
    )

    spreadsheet = _worksheet.spreadsheet
    targets = [
        (spreadsheet.worksheet(name), headers)
        for name, headers in (
            (MAIN_SHEET, HEADERS), (BACKUP_SHEET, HEADERS), (REVIEW_SHEET, REVIEW_HEADERS)
        )
    ]
    for worksheet, headers in targets:
        _ensure_sheet_headers(worksheet, headers)
        if worksheet.row_values(1) != headers:
            raise RuntimeError(f"{worksheet.title}: header verification failed.")
        print(f"{worksheet.title}: verified {len(headers)} columns")


if __name__ == "__main__":
    main()
