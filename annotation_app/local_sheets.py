"""
Local development replacement for Google Sheets.
Annotations are still stored in a static/annotations.jsonl.
No data is sent to Googlr Sheets in local mode.
"""

from storage import load_records

def load_records_from_sheets():
    return load_records()

def append_row(row):
    print("LOCAL MODE: annotation saved in JSONL only")

def update_row_by_id(record_id, row):
    print(f"LOCAL MODE: annotation{record_id} updated in JSONL only")

def append_review_rows(rows):
    print("LOCAL MODE: review rows were not sent to Google Sheets")

def get_reviewed_annotation_ids_by_user(username):
    return set()

def get_completed_review_counts_by_annotation(rows_per_reviewer=9):
    return {}

def clear_sheet_data():
    print("LOCAL MODE: Google Sheet was not cleared")

def rebuild_sheet_from_records(records):
    print("LOCAL MODE: Google Sheet was not rebuilt")
