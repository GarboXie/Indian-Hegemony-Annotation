"""Check real sheet helpers without importing credentials or calling Google."""
import ast
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1] / "annotation_app"


def definitions(filename, names, scope):
    tree = ast.parse((ROOT / filename).read_text(encoding="utf-8"))
    nodes = [n for n in tree.body if (
        isinstance(n, ast.FunctionDef) and n.name in names
        or isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id in names for t in n.targets)
    )]
    exec(compile(ast.Module(body=nodes, type_ignores=[]), filename, 'exec'), scope)


class SheetColumns(unittest.TestCase):
    def setUp(self):
        self.scope = {}
        definitions('config.py', {'HEGEMONY_AXES', 'MODEL_COLUMN_KEYS', 'LEGACY_HEADERS', 'HEADERS'}, self.scope)
        self.scope['gspread'] = SimpleNamespace(utils=SimpleNamespace(rowcol_to_a1=lambda r, c: 'DT1'))
        definitions('sheets.py', {'_normalize_yes_no', '_row_map_to_record', '_ensure_sheet_headers'}, self.scope)

    def test_roundtrip_and_aliases(self):
        s = self.scope
        self.assertEqual(len(s['HEADERS']), 124)
        self.assertEqual(len(set(s['HEADERS'])), 124)
        for old, new in zip(s['LEGACY_HEADERS'], s['HEADERS']):
            expected = old
            for internal, neutral in s['MODEL_COLUMN_KEYS'].items():
                if old.startswith(internal + '_'):
                    expected = neutral + old[len(internal):]
            self.assertEqual(new, expected)
        old_row = {'id': 'test', 'state': 'Singapore'}
        for model in s['MODEL_COLUMN_KEYS']:
            for kind in ['base', 'identity']:
                prefix = f'{model}_{kind}'
                old_row[prefix + '_output'] = prefix + ' response'
                old_row[prefix + '_hallucination'] = 'yes'
                for axis in s['HEGEMONY_AXES']:
                    old_row[prefix + '_' + axis] = 'yes'
                    old_row[prefix + '_' + axis + '_impact'] = prefix + axis
        new_row = dict(zip(s['HEADERS'], [old_row.get(h, '') for h in s['LEGACY_HEADERS']]))
        old_record = s['_row_map_to_record'](old_row)
        new_record = s['_row_map_to_record'](new_row)
        self.assertEqual(new_record['outputs'], old_record['outputs'])
        for model in s['MODEL_COLUMN_KEYS']:
            for kind in ['base', 'identity']:
                self.assertEqual(new_record['outputs'][model][kind]['text'], f'{model}_{kind} response')

    def test_migration_changes_only_header(self):
        s = self.scope

        class Sheet:
            col_count = 124
            rows = [list(s['LEGACY_HEADERS']), ['existing-data'] * 124]

            def row_values(self, row): return self.rows[row - 1]
            def resize(self, **kwargs): pass
            def update(self, cell_range, values, **kwargs):
                assert cell_range == 'A1:DT1'
                self.rows[0] = values[0]

        sheet = Sheet()
        original = list(sheet.rows[1])
        s['_ensure_sheet_headers'](sheet, s['HEADERS'])
        self.assertEqual(sheet.rows[0], s['HEADERS'])
        self.assertEqual(sheet.rows[1], original)
        sheet.rows[0] = ['unexpected', 'schema']
        with self.assertRaises(ValueError):
            s['_ensure_sheet_headers'](sheet, s['HEADERS'])


if __name__ == '__main__':
    unittest.main()
