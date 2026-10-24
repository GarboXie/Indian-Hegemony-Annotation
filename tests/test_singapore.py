"""Isolated integration checks; model calls are mocked, never sent externally."""
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.dont_write_bytecode = True
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "annotation_app"))


class SingaporeFlow(unittest.TestCase):
    def test_complete_flow(self):
        from werkzeug.security import generate_password_hash
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {
            "LOCAL_DEMO": "1", "SINGAPORE_DATA_ROOT": tmp,
            "SINGAPORE_FLASK_SECRET_KEY": "temporary-test-session-key",
            "SINGAPORE_ANNOTATOR_PASSWORD_HASH": generate_password_hash("test-code"),
            "SINGAPORE_ADMIN_USERNAME": "test-admin",
            "SINGAPORE_ADMIN_PASSWORD_HASH": generate_password_hash("test-admin-password"),
        }), patch("requests.sessions.Session.request", side_effect=AssertionError("Network disabled")):
            import config, app, storage, auth, draft_store, notes_store, iaa_store, prompt_similarity
            app.app.config.update(TESTING=True)
            app._safe_upsert_prompt_embedding = lambda record: None
            client = app.app.test_client()
            for path in [config.DATA_FILE, config.ANNOTATORS_FILE, draft_store.DRAFT_DIR,
                         notes_store.NOTES_DIR, iaa_store.IAA_DB_PATH,
                         prompt_similarity.PROMPT_EMBEDDING_INDEX_PATH,
                         app._iar_assignments_file_path()]:
                self.assertTrue(Path(path).is_relative_to(config.DATA_DIR), path)
            self.assertEqual(app.app.config['SESSION_COOKIE_NAME'], 'singapore_portal_session')
            self.assertEqual(client.get('/').status_code, 302)
            self.assertEqual(client.post('/access-code', data={'secret_code':'test-code'}).status_code, 302)
            signup = dict(username='test-user', password='test-password', state='Other',
                          age_group='25–34', gender='Other', education_level='PhD',
                          field_of_study='Research', social_theory_training='Yes',
                          llm_experience_level='Advanced', urban_rural_background='Urban')
            self.assertEqual(client.post('/signup', data=signup).status_code, 302)
            self.assertEqual(auth.load_annotators()[0]['state'], 'Singapore')
            html = client.get('/').get_data(as_text=True)
            self.assertIn('Singapore', html)
            self.assertNotIn('qwen/qwen', html)
            # Similarity requires no geographic field and distinguishes an empty index.
            query = 'A sufficiently long Singapore prompt to test semantic similarity.'
            with patch.object(app, 'load_prompt_index', return_value={'items': {}}), patch.object(app, 'find_similar_for_state', return_value=[]):
                checked = client.post('/check-prompt-similarity', json={'prompt': query})
                self.assertEqual(checked.status_code, 200)
                self.assertEqual(checked.json['indexed_prompt_count'], 0)
                self.assertIn('No indexed prompts', checked.json['message'])
            match = {'annotation_id': 'other', 'prompt': query, 'similarity': 1.0}
            with patch.object(app, 'load_prompt_index', return_value={'items': {'other': {'base_prompt': query, 'embedding': [1, 0]}}}), patch.object(app, 'find_similar_for_state', return_value=[match]) as finder:
                checked = client.post('/check-prompt-similarity', json={'prompt': query, 'current_annotation_id': 'self'})
                self.assertEqual(checked.status_code, 200)
                self.assertTrue(checked.json['near_duplicate'])
                self.assertEqual(finder.call_args.kwargs['state'], 'Singapore')
                self.assertEqual(finder.call_args.kwargs['exclude_annotation_id'], 'self')
            form = dict(annotator_name='test-user', base_prompt='Base test', identity_primed_prompt='Identity test', ground_truth='Ground truth')
            for model, function in [('gemini','generate_qwen_output'), ('gpt','generate_gpt_oss_output'),
                                    ('llama','generate_llama_output'), ('deepseek','generate_deepseek_output')]:
                with patch.object(app, function, return_value='Mock response') as mocked:
                    for kind in ['base','identity']:
                        response = client.post('/generate/'+model, json={'prompt':kind+' test'})
                        self.assertEqual(response.json, {'text':'Mock response'})
                        form[f'{model}_{kind}_output'] = response.json['text']
                        for axis in config.HEGEMONY_AXES:
                            form[f'{model}_{kind}_{axis}_hegemony'] = 'yes'
                            form[f'{model}_{kind}_{axis}_impact'] = axis+' impact'
                    self.assertEqual(mocked.call_count, 2)
            saved = client.post('/save-annotation-draft', data=form)
            self.assertEqual(saved.status_code, 200)
            annotation_id = saved.json['annotation_id']
            self.assertEqual(len(storage.load_records()), 1)
            self.assertEqual(client.post('/', data=form).status_code, 200)
            self.assertEqual(client.post('/confirm').status_code, 302)
            self.assertEqual(len(storage.load_records()), 1)
            record = storage.load_records()[0]
            self.assertEqual(len(storage.json_to_row(record)), len(config.HEADERS))
            self.assertEqual(record['state'], 'Singapore')
            notes_store.save_note('test-user', 'Test note', 'Singapore')
            self.assertEqual(len(notes_store.list_notes('test-user')), 1)
            iaa_store.save_iaa_review(dict(annotation_id=annotation_id, reviewer_name='peer', reviewer_state='Singapore', annotation_creator='test-user', review_timestamp='2026-10-24T00:00:00', editable=0, completed=1))
            self.assertIsNotNone(iaa_store.fetch_iaa_review(annotation_id, 'peer'))
            client.get('/logout')
            self.assertEqual(client.post('/login', data={'username':'test-user','password':'test-password'}).status_code, 302)
            client.get('/logout')
            self.assertEqual(client.post('/login', data={'username':'test-admin','password':'test-admin-password'}).status_code, 302)
            self.assertEqual(client.get('/admin/load/'+annotation_id).status_code, 200)
            self.assertEqual(client.post('/admin/load/'+annotation_id, data={'isAccept':'yes', 'expert_reviews':'Reviewed'}).status_code, 302)
            exported = client.get('/admin/annotations.csv')
            self.assertEqual(exported.status_code, 200)
            self.assertIn('religious', exported.get_data(as_text=True))
            self.assertIn('ethnic', exported.get_data(as_text=True))
            self.assertIn('qwen_base_output', exported.get_data(as_text=True))
            self.assertNotIn('region', exported.get_data(as_text=True).splitlines()[0].split(','))
            self.assertNotIn('state', exported.get_data(as_text=True).splitlines()[0].split(','))


if __name__ == '__main__':
    unittest.main()
