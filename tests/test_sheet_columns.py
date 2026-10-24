"""Test actual serialization and migration code without credentials or network."""
import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'annotation_app'


def definitions(filename, names, scope):
    tree = ast.parse((ROOT / filename).read_text(encoding='utf-8'))
    nodes = [n for n in tree.body if (
        isinstance(n, ast.FunctionDef) and n.name in names
        or isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id in names for t in n.targets)
    )]
    exec(compile(ast.Module(body=nodes, type_ignores=[]), filename, 'exec'), scope)


class SheetColumns(unittest.TestCase):
    def setUp(self):
        self.s = {}
        definitions('config.py', {'HEGEMONY_AXES', 'MODEL_COLUMN_KEYS', 'NEUTRAL_MODEL_COLUMN_KEYS',
                                'LEGACY_HEADERS', 'NEUTRAL_HEADERS', 'HEADERS'}, self.s)
        definitions('sheets.py', {'LEGACY_REVIEW_HEADERS', 'REVIEW_HEADERS', '_normalize_yes_no',
                                '_row_map_to_record', '_ensure_sheet_headers'}, self.s)
        definitions('storage.py', {'json_to_row'}, self.s)
        definitions('scripts/migrate_singapore_sheet.py', {'migration_requests'}, self.s)

    def record(self):
        s = self.s
        old_row = {'id': 'test', 'timestamp': 'test-time', 'annotator_name': 'tester',
                   'region': 'Singapore', 'state': 'Singapore',
                   'base_prompt': 'Base', 'identity_prompt': 'Identity'}
        for model in s['MODEL_COLUMN_KEYS']:
            for kind in ['base', 'identity']:
                prefix = f'{model}_{kind}'
                old_row[prefix + '_output'] = prefix + ' response'
                old_row[prefix + '_hallucination'] = 'yes'
                for axis in s['HEGEMONY_AXES']:
                    old_row[prefix + '_' + axis] = 'yes'
                    old_row[prefix + '_' + axis + '_impact'] = prefix + axis
        for h in ['ground_truth', 'references', 'expert_reviews', 'isAccept', 'annotator_addressed']:
            old_row[h] = h + ' value'
        return old_row, s['_row_map_to_record'](old_row)

    def test_three_schema_roundtrips(self):
        s = self.s
        old_row, expected = self.record()
        serialized = s['json_to_row'](expected)
        self.assertEqual(len(serialized), 122)
        self.assertEqual(len(set(s['HEADERS'])), 122)
        self.assertEqual(s['HEADERS'][3:5], ['base_prompt', 'identity_prompt'])
        for prefix in ['qwen_3_8_27b', 'gpt_oss_120b', 'llama_4_maverick', 'deepseek_v3_2']:
            self.assertIn(prefix + '_base_output', s['HEADERS'])
            self.assertIn(prefix + '_identity_ethnic_impact', s['HEADERS'])
        for headers in [s['HEADERS'], s['REVIEW_HEADERS']]:
            self.assertNotIn('region', headers)
            self.assertNotIn('state', headers)
        new_row = dict(zip(s['HEADERS'], serialized))
        neutral_row = dict(zip(s['NEUTRAL_HEADERS'], [old_row.get(h, '') for h in s['LEGACY_HEADERS']]))
        for row in [old_row, neutral_row, new_row]:
            self.assertEqual(s['_row_map_to_record'](row), expected)

    def test_atomic_requests_preserve_cells(self):
        s = self.s
        for old, new in [(s['LEGACY_HEADERS'], s['HEADERS']),
                         (s['NEUTRAL_HEADERS'], s['HEADERS']),
                         (s['LEGACY_REVIEW_HEADERS'], s['REVIEW_HEADERS'])]:
            data = [f'value-{i}' for i in range(len(old))]
            rows = [list(old), list(data), ['short'] + [''] * (len(old) - 1)]
            for request in s['migration_requests'](123, old, new):
                if 'deleteDimension' in request:
                    dimension = request['deleteDimension']['range']
                    self.assertEqual(dimension['sheetId'], 123)
                    for row in rows:
                        del row[dimension['startIndex']:dimension['endIndex']]
                else:
                    update = request['updateCells']
                    self.assertEqual(update['fields'], 'userEnteredValue')
                    self.assertEqual(update['start']['rowIndex'], 0)
                    rows[0] = [cell['userEnteredValue']['stringValue'] for cell in update['rows'][0]['values']]
            self.assertEqual(rows[0], new)
            self.assertEqual(rows[1], [v for h, v in zip(old, data) if h not in {'state', 'region'}])
            self.assertEqual(rows[2], ['short'] + [''] * (len(new) - 1))

    def test_old_headers_require_explicit_migration(self):
        s = self.s
        class Sheet:
            def row_values(self, _): return s['NEUTRAL_HEADERS']
        with self.assertRaises(ValueError):
            s['_ensure_sheet_headers'](Sheet(), s['HEADERS'])


if __name__ == '__main__':
    unittest.main()
