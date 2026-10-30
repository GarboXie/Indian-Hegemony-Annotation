"""Verify provider reasoning settings without credentials or network calls."""
import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import Mock, patch


class LLMReasoning(unittest.TestCase):
    def setUp(self):
        config = types.ModuleType('config')
        config.KEYS = {name: 'fake-key' for name in (
            'GROQ_QWEN_API_KEY', 'GROQ_GPT_OSS_API_KEY',
            'OPENROUTER_LLAMA_API_KEY', 'OPENROUTER_DEEPSEEK_API_KEY',
        )}
        path = Path(__file__).resolve().parents[1] / 'annotation_app' / 'llm.py'
        spec = importlib.util.spec_from_file_location('isolated_llm_reasoning', path)
        self.module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {'config': config}):
            spec.loader.exec_module(self.module)

    def assert_unchanged_constraints(self, kwargs):
        self.assertEqual(kwargs['messages'][0], {
            'role': 'system',
            'content': 'Answer in no more than 150 words in English.',
        })
        self.assertEqual(kwargs['messages'][1], {'role': 'user', 'content': 'Test prompt'})
        for name in ('temperature', 'max_tokens', 'max_completion_tokens'):
            self.assertNotIn(name, kwargs)

    def test_groq_models_reason_with_only_final_answer_returned(self):
        for function, model in (
            ('generate_qwen_output', 'qwen/qwen3.8-27b'),
            ('generate_gpt_oss_output', 'openai/gpt-oss-120b'),
        ):
            with self.subTest(model=model):
                client = Mock()
                client.chat.completions.create.return_value.choices = [
                    types.SimpleNamespace(finish_reason='stop', message=types.SimpleNamespace(
                        content='Final answer', reasoning='Private reasoning'))
                ]
                with patch.object(self.module, 'OpenAI', return_value=client):
                    self.assertEqual(getattr(self.module, function)('Test prompt'), 'Final answer')
                kwargs = client.chat.completions.create.call_args.kwargs
                self.assertEqual(kwargs['model'], model)
                self.assertEqual(kwargs['reasoning_effort'], 'medium')
                self.assertEqual(kwargs['extra_body'], {'include_reasoning': False})
                self.assert_unchanged_constraints(kwargs)

    def test_openrouter_reasoning_enabled_only_for_supported_model(self):
        for function, model, supported in (
            ('generate_llama_output', 'meta-llama/llama-4-maverick', False),
            ('generate_deepseek_output', 'deepseek/deepseek-v3.2', True),
        ):
            with self.subTest(model=model):
                response = Mock()
                response.json.return_value = {'choices': [{
                    'finish_reason': 'stop',
                    'message': {'content': 'Final answer', 'reasoning': 'Private reasoning'},
                }]}
                with patch.object(self.module.requests, 'post', return_value=response) as post:
                    self.assertEqual(getattr(self.module, function)('Test prompt'), 'Final answer')
                response.raise_for_status.assert_called_once()
                payload = post.call_args.kwargs['json']
                self.assertEqual(payload['model'], model)
                if supported:
                    self.assertEqual(payload['reasoning'], {'enabled': True})
                else:
                    self.assertNotIn('reasoning', payload)
                self.assert_unchanged_constraints(payload)


if __name__ == '__main__':
    unittest.main()
