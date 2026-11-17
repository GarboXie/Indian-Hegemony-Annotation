#!/usr/bin/env python3
import os
import sys


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, APP_DIR)

from sheets import _worksheet
from prompt_similarity import load_prompt_index, upsert_prompt_embedding_for_record


def main():
    # Read only: unlike the app loader, do not initialize or replace sheet headers.
    values = _worksheet.get_all_values()
    if not values:
        print('Backfill complete. Added=0, Skipped=0, Failed=0')
        return
    headers = values[0]
    required_headers = ('id', 'state', 'base_prompt')
    if any(headers.count(header) != 1 for header in required_headers):
        raise RuntimeError('The Mainland sheet must contain one id, state, and base_prompt column each.')
    index_data = load_prompt_index()
    existing_items = index_data.get("items", {})

    added = 0
    skipped = 0
    failed = 0

    for row in values[1:]:
        if not any(cell.strip() for cell in row):
            continue
        cells = dict(zip(headers, row))
        annotation_id = cells.get('id', '').strip()
        state = cells.get('state', '').strip()
        base_prompt = cells.get('base_prompt', '')

        if not annotation_id or not state or not base_prompt.strip():
            skipped += 1
            continue

        record = {'id': annotation_id, 'state': state, 'prompts': {'base': base_prompt}}
        cached = existing_items.get(annotation_id, {})
        if (cached.get('base_prompt') == base_prompt
                and cached.get('state') == record.get('state', '')
                and isinstance(cached.get('embedding'), list) and cached['embedding']):
            skipped += 1
            continue

        try:
            upsert_prompt_embedding_for_record(record)
            added += 1
            print(f"Added embedding for: {annotation_id}")
        except Exception as e:
            failed += 1
            print(f"Failed embedding for {annotation_id}: {e}")

    print(f"Backfill complete. Added={added}, Skipped={skipped}, Failed={failed}")
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
