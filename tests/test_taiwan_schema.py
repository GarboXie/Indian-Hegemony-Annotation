"""Taiwan's five-axis schema and safe new-sheet setup, without credentials."""
import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'annotation_app'


def selected_definitions(path, names, scope):
    nodes = []
    for node in ast.parse(path.read_text(encoding='utf-8')).body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id in names for t in node.targets):
            nodes.append(node)
        elif isinstance(node, ast.For) and isinstance(node.target, ast.Name) and node.target.id == '_model':
            nodes.append(node)
        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute) and isinstance(node.value.func.value, ast.Name) and node.value.func.value.id == 'HEADERS':
            nodes.append(node)
        elif isinstance(node, ast.FunctionDef) and node.name in names:
            nodes.append(node)
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), 'exec'), scope)


class Sheet:
    def __init__(self, title, rows=None, cols=1):
        self.title, self.rows, self.col_count = title, rows or [], cols
    def get_all_values(self): return self.rows
    def row_values(self, _): return self.rows[0] if self.rows else []
    def resize(self, cols): self.col_count = cols
    def update(self, range_name, values, **kwargs):
        assert range_name == 'A1'
        self.rows = [values[0]] + self.rows[1:]


class Spreadsheet:
    def __init__(self, sheets=None): self.sheets = sheets or []
    def worksheets(self): return self.sheets
    def add_worksheet(self, title, rows, cols):
        sheet = Sheet(title, cols=cols)
        self.sheets.append(sheet)
        return sheet


class TaiwanSchema(unittest.TestCase):
    def setUp(self):
        self.s = {}
        selected_definitions(ROOT / 'config.py', {'HEGEMONY_AXES', 'AXIS_DESCRIPTIONS', 'MODEL_COLUMN_KEYS',
                            'NEUTRAL_MODEL_COLUMN_KEYS', 'HEADERS', 'REVIEW_HEADERS'}, self.s)
        selected_definitions(ROOT / 'storage.py', {'json_to_row'}, self.s)
        selected_definitions(ROOT / 'sheets.py', {'_row_map_to_record', '_normalize_yes_no'}, self.s)
        selected_definitions(ROOT / 'scripts/initialize_taiwan_sheet.py', {'initialize_worksheets'}, self.s)

    def test_five_axes_and_eight_outputs_roundtrip(self):
        s = self.s
        self.assertEqual(s['HEGEMONY_AXES'], ['social', 'economic', 'gender', 'linguistic', 'ethnic'])
        self.assertEqual(list(s['AXIS_DESCRIPTIONS']), s['HEGEMONY_AXES'])
        self.assertEqual(len(s['HEADERS']), 106)
        self.assertEqual(len(set(s['HEADERS'])), 106)
        self.assertEqual(len(s['REVIEW_HEADERS']), 15)
        self.assertFalse({'region', 'state'} & set(s['HEADERS']))
        self.assertFalse(any('religious' in h for h in s['HEADERS']))
        row = {h: 'test' for h in s['HEADERS']}
        for model in ['qwen', 'gpt_oss', 'llama', 'deepseek']:
            for kind in ['base', 'identity']:
                for axis in s['HEGEMONY_AXES']:
                    row[f'{model}_{kind}_{axis}'] = 'yes'
        record = s['_row_map_to_record'](row)
        self.assertEqual(record['state'], 'Taiwan')
        self.assertEqual(record['region'], 'Taiwan')
        serialized = s['json_to_row'](record)
        again = s['_row_map_to_record'](dict(zip(s['HEADERS'], serialized)))
        self.assertEqual(again, record)
        self.assertEqual(len(serialized), 106)
        for output in again['outputs'].values():
            for variant in output.values():
                self.assertEqual(list(variant['hegemony']), s['HEGEMONY_AXES'])

    def test_initializer_creates_and_is_idempotent(self):
        sheet = Spreadsheet()
        init = self.s['initialize_worksheets']
        init(sheet, self.s['HEADERS'], self.s['REVIEW_HEADERS'])
        self.assertEqual([len(ws.rows[0]) for ws in sheet.sheets], [106, 106, 15])
        sheet.sheets[0].rows.append(['existing-taiwan-id'])
        init(sheet, self.s['HEADERS'], self.s['REVIEW_HEADERS'])
        self.assertEqual(sheet.sheets[0].rows[1], ['existing-taiwan-id'])
        self.assertEqual(len(sheet.sheets), 3)

    def test_initializer_refuses_other_campaign_before_writing(self):
        sheet = Spreadsheet([Sheet('testing'), Sheet('testing2', [['wrong', 'headers']])])
        with self.assertRaises(ValueError):
            self.s['initialize_worksheets'](sheet, self.s['HEADERS'], self.s['REVIEW_HEADERS'])
        self.assertEqual(sheet.sheets[0].rows, [])
        self.assertEqual(len(sheet.sheets), 2)


if __name__ == '__main__':
    unittest.main()
