"""Similarity tests with fake credentials and mocked provider responses."""
import copy
import ast
import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import Mock, patch


class PromptSimilarity(unittest.TestCase):
    def setUp(self):
        config = types.ModuleType('config')
        config.KEYS = {'OPENROUTER_LLAMA_API_KEY': 'fake-key-never-transmitted'}
        config.BASE_DIR = Path('unused-test-directory')
        path = Path(__file__).resolve().parents[1] / 'annotation_app' / 'prompt_similarity.py'
        spec = importlib.util.spec_from_file_location('isolated_similarity', path)
        self.module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {'config': config}):
            spec.loader.exec_module(self.module)
        self.index = {'version': 1, 'items': {}}
        self.load = patch.object(self.module, 'load_prompt_index', side_effect=lambda: copy.deepcopy(self.index))
        self.save = patch.object(self.module, 'save_prompt_index', side_effect=self.save_index)
        self.load.start()
        self.save.start()
        self.addCleanup(self.load.stop)
        self.addCleanup(self.save.stop)

    def save_index(self, data):
        self.index = copy.deepcopy(data)

    def test_reuses_openrouter_key_and_normalizes_embedding(self):
        self.module.KEYS['OPENAI_API_KEY'] = 'legacy-key-must-not-override-current-key'
        response = Mock(ok=True)
        response.json.return_value = {'data': [{'embedding': [3, 4]}]}
        with patch.object(self.module.requests, 'post', return_value=response) as post:
            self.assertEqual(self.module.embed_prompt_openrouter('test'), [0.6, 0.8])
        call = post.call_args.kwargs
        self.assertEqual(call['headers']['Authorization'], 'Bearer fake-key-never-transmitted')
        self.assertEqual(call['json']['model'], self.module.OPENROUTER_EMBEDDING_MODEL)
        self.assertEqual(call['json']['input'], 'test')

    def test_explicit_key_precedence(self):
        self.module.KEYS['OPENROUTER_EMBEDDING_API_KEY'] = 'explicit-fake-key'
        response = Mock(ok=True)
        response.json.return_value = {'data': [{'embedding': [1, 0]}]}
        with patch.object(self.module.requests, 'post', return_value=response) as post:
            self.module.embed_prompt_openrouter('test')
        self.assertEqual(post.call_args.kwargs['headers']['Authorization'], 'Bearer explicit-fake-key')

    def test_saved_prompt_match_self_exclusion_and_update(self):
        m = self.module
        record = {'id': 'a', 'state': 'Beijing', 'prompts': {'base': 'A Mainland China prompt for comparison'}}
        with patch.object(m, 'embed_prompt_openrouter', return_value=[1, 0]) as embed:
            m.upsert_prompt_embedding_for_record(record)
            m.upsert_prompt_embedding_for_record(record)
            self.assertEqual(embed.call_count, 1)
            self.assertEqual(self.index['items']['a']['state'], 'Beijing')
            self.assertEqual(m.find_similar_for_state('same meaning', 'Beijing')[0]['similarity'], 1.0)
            self.assertEqual(m.find_similar_for_state('same meaning', 'Beijing', exclude_annotation_id='a'), [])
            record['prompts']['base'] = 'Updated Mainland China prompt'
            m.upsert_prompt_embedding_for_record(record)
            self.assertEqual(self.index['items']['a']['base_prompt'], record['prompts']['base'])

    def test_threshold_order_and_top_k(self):
        self.index['items'] = {
            'low': {'state': 'Beijing', 'base_prompt': 'Unrelated', 'embedding': [0, 1]},
            'second': {'state': 'Beijing', 'base_prompt': 'Related', 'embedding': [0.8, 0.6]},
            'best': {'state': 'Beijing', 'base_prompt': 'Identical', 'embedding': [1, 0]},
        }
        with patch.object(self.module, 'embed_prompt_openrouter', return_value=[1, 0]):
            matches = self.module.find_similar_for_state('query', 'Beijing', top_k=1)
        self.assertEqual([m['annotation_id'] for m in matches], ['best'])

    def test_empty_index_does_not_call_provider(self):
        with patch.object(self.module.requests, 'post', side_effect=AssertionError('No network')):
            self.assertEqual(self.module.find_similar_for_state('query', None), [])

    def test_province_filtering_and_private_index(self):
        m = self.module
        self.assertEqual(Path(m.PROMPT_EMBEDDING_INDEX_PATH).parts[-3:],
                         ('data', 'mainland', 'prompt_embeddings.json'))
        self.index['items'] = {
            'beijing': {'state': 'Beijing', 'base_prompt': 'Beijing prompt', 'embedding': [1, 0]},
            'shanghai': {'state': 'Shanghai', 'base_prompt': 'Shanghai prompt', 'embedding': [1, 0]},
        }
        with patch.object(m, 'embed_prompt_openrouter', return_value=[1, 0]):
            matches = m.find_similar_for_state('query', ' beijing ')
        self.assertEqual([item['annotation_id'] for item in matches], ['beijing'])
        with patch.object(m, 'embed_prompt_openrouter', side_effect=AssertionError('No API call needed')):
            self.assertEqual(m.find_similar_for_state('query', 'Guangdong'), [])

    def test_real_route_authentication_scope_and_empty_index(self):
        from flask import Flask, jsonify, request, redirect, session, url_for
        from functools import wraps
        m = self.module
        app = Flask(__name__)
        app.secret_key = 'temporary-test-secret'
        tree = ast.parse((Path(__file__).resolve().parents[1] / 'annotation_app/app.py').read_text(encoding='utf-8'))
        definitions = [n for n in tree.body if isinstance(n, ast.FunctionDef)
                       and n.name in {'login_required', 'check_prompt_similarity'}]
        scope = dict(app=app, request=request, jsonify=jsonify, redirect=redirect,
                     session=session, url_for=url_for, wraps=wraps,
                     PROMPT_SIM_THRESHOLD=m.PROMPT_SIM_THRESHOLD,
                     PROMPT_SIM_TOP_K=m.PROMPT_SIM_TOP_K,
                     PROMPT_SIM_MIN_CHARS=m.PROMPT_SIM_MIN_CHARS,
                     PROMPT_SIM_NEAR_DUP_THRESHOLD=m.PROMPT_SIM_NEAR_DUP_THRESHOLD,
                     load_prompt_index=m.load_prompt_index, find_similar_for_state=m.find_similar_for_state)
        exec(compile(ast.Module(body=definitions, type_ignores=[]), 'app.py', 'exec'), scope)
        app.add_url_rule('/login', 'auth.login', lambda: 'Login')
        client = app.test_client()
        query = 'A long Mainland China Base prompt to check for semantic duplication.'
        endpoint = '/check-prompt-similarity'
        self.assertEqual(client.post(endpoint, json={'prompt': query, 'state': 'Beijing'}).status_code, 302)
        with client.session_transaction() as sess:
            sess['user'] = {'username': 'test', 'state': 'Beijing', 'role': 'annotator'}
        self.assertEqual(client.post(endpoint, json={'prompt': query}).status_code, 400)
        empty = client.post(endpoint, json={'prompt': query, 'state': 'Beijing'})
        self.assertEqual(empty.status_code, 200)
        self.assertEqual(empty.json['indexed_prompt_count'], 0)
        self.assertIn('No indexed prompts', empty.json['message'])
        short = client.post(endpoint, json={'prompt': 'short', 'state': 'Beijing'})
        self.assertIn('at least 40', short.json['message'])
        self.index['items'] = {
            'self': {'state': 'Beijing', 'base_prompt': query, 'embedding': [1, 0]},
            'other': {'state': 'Beijing', 'base_prompt': query, 'embedding': [1, 0]},
            'wrong-province': {'state': 'Shanghai', 'base_prompt': query, 'embedding': [1, 0]},
        }
        with patch.object(m, 'embed_prompt_openrouter', return_value=[1, 0]):
            checked = client.post(endpoint, json={'prompt': query, 'state': 'Beijing', 'current_annotation_id': 'self'})
        self.assertEqual(checked.json['indexed_prompt_count'], 1)
        self.assertTrue(checked.json['near_duplicate'])
        self.assertEqual([item['annotation_id'] for item in checked.json['matches']], ['other'])

    def test_mainland_guide_link_and_no_schema_changes(self):
        root = Path(__file__).resolve().parents[1] / 'annotation_app'
        html = (root / 'templates/layout/base.html').read_text(encoding='utf-8')
        self.assertIn('https://docs.google.com/document/d/17EtWI0OkBxWrDFY1UxTHaMIC1Hh9qsSeblP3D2n6Qys/edit?tab=t.0', html)
        self.assertNotIn('1Kuw8nA1v3RSPoc0Eog0Wt1zrc3fD_MYr', html)

    def test_missing_key_and_provider_errors_hide_response(self):
        response = Mock(ok=False, status_code=403, text='private-provider-detail')
        with patch.object(self.module.requests, 'post', return_value=response):
            with self.assertRaisesRegex(RuntimeError, 'embedding access was denied') as error:
                self.module.embed_prompt_openrouter('test')
        self.assertNotIn('private-provider-detail', str(error.exception))
        self.module.KEYS.clear()
        with self.assertRaisesRegex(RuntimeError, 'No OpenRouter key'):
            self.module.embed_prompt_openrouter('test')


if __name__ == '__main__':
    unittest.main()
