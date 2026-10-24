"""Similarity tests with fake credentials and mocked provider responses."""
import copy
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
        config.DATA_DIR = Path('unused-test-directory')
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
        record = {'id': 'a', 'prompts': {'base': 'A Singapore prompt for comparison'}}
        with patch.object(m, 'embed_prompt_openrouter', return_value=[1, 0]) as embed:
            m.upsert_prompt_embedding_for_record(record)
            m.upsert_prompt_embedding_for_record(record)
            self.assertEqual(embed.call_count, 1)
            self.assertEqual(self.index['items']['a']['state'], 'Singapore')
            self.assertEqual(m.find_similar_for_state('same meaning', None)[0]['similarity'], 1.0)
            self.assertEqual(m.find_similar_for_state('same meaning', None, exclude_annotation_id='a'), [])
            record['prompts']['base'] = 'Updated Singapore prompt'
            m.upsert_prompt_embedding_for_record(record)
            self.assertEqual(self.index['items']['a']['base_prompt'], record['prompts']['base'])

    def test_threshold_order_and_top_k(self):
        self.index['items'] = {
            'low': {'base_prompt': 'Unrelated', 'embedding': [0, 1]},
            'second': {'base_prompt': 'Related', 'embedding': [0.8, 0.6]},
            'best': {'base_prompt': 'Identical', 'embedding': [1, 0]},
        }
        with patch.object(self.module, 'embed_prompt_openrouter', return_value=[1, 0]):
            matches = self.module.find_similar_for_state('query', None, top_k=1)
        self.assertEqual([m['annotation_id'] for m in matches], ['best'])

    def test_empty_index_does_not_call_provider(self):
        with patch.object(self.module.requests, 'post', side_effect=AssertionError('No network')):
            self.assertEqual(self.module.find_similar_for_state('query', None), [])

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
