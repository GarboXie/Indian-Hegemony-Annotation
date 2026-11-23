"""Isolated integration checks; model calls are mocked, never sent externally."""
import os
import re
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
            self.assertNotIn('id="second_prompt_input"', html)
            self.assertNotIn('name="ground_truth_native"', html)
            self.assertEqual(len(re.findall(r'data-output-preview-for="\w+_llm_output_base"', html)), 4)
            self.assertNotIn('name="gemini_identity_output"', html)
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
            form = dict(annotator_name='test-user', base_prompt='Base test', native_prompt='本地語言提示', ground_truth='Ground truth', ground_truth_native='本地語言答案')
            for model, function in [('gemini','generate_qwen_output'), ('gpt','generate_gpt_oss_output'),
                                    ('llama','generate_llama_output'), ('deepseek','generate_deepseek_output')]:
                with patch.object(app, function, return_value='Mock response') as mocked:
                    for kind in ['base','identity']:
                        response = client.post('/generate/'+model, json={'prompt': kind+' test', 'native': kind == 'identity'})
                        self.assertEqual(response.json, {'text':'Mock response'})
                        form[f'{model}_{kind}_output'] = response.json['text']
                        for axis in config.HEGEMONY_AXES:
                            form[f'{model}_{kind}_{axis}_hegemony'] = 'yes'
                            form[f'{model}_{kind}_{axis}_impact'] = axis+' impact'
                    self.assertEqual(mocked.call_count, 2)
                    mocked.assert_called_with('identity test', native=True)
            saved = client.post('/save-annotation-draft', data=form)
            self.assertEqual(saved.status_code, 200)
            annotation_id = saved.json['annotation_id']
            self.assertEqual(len(storage.load_records()), 1)
            self.assertEqual(client.post('/', data={**form, 'ground_truth_native': ''}).status_code, 400)
            review = client.post('/', data=form)
            self.assertEqual(review.status_code, 200)
            self.assertIn('Native Prompt', review.get_data(as_text=True))
            self.assertIn('本地語言答案', review.get_data(as_text=True))
            self.assertEqual(client.post('/confirm').status_code, 302)
            self.assertEqual(len(storage.load_records()), 1)
            record = storage.load_records()[0]
            self.assertEqual(record['second_prompt_type'], 'native')
            self.assertEqual(record['prompts']['identity'], '本地語言提示')
            self.assertEqual(record['ground_truth_native'], '本地語言答案')
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

            # New English-only work can save an incomplete draft and then submit
            # with one prompt, four answers and one ground truth.
            client.get('/freshannotate')
            english_form = dict(
                annotator_name='test-user', base_prompt='English Singapore prompt',
                second_prompt_type='english_only', ground_truth='English ground truth',
            )
            for model in ['gemini', 'gpt', 'llama', 'deepseek']:
                english_form[f'{model}_base_output'] = f'English {model} answer'
            draft = client.post('/save-annotation-draft', data={
                **english_form, 'ground_truth': '',
            })
            self.assertEqual(draft.status_code, 200)
            english_id = draft.json['annotation_id']
            self.assertEqual(client.post('/', data={
                **english_form, 'ground_truth': '',
            }).status_code, 400)
            reviewed = client.post('/', data=english_form)
            self.assertEqual(reviewed.status_code, 200)
            review_html = reviewed.get_data(as_text=True)
            self.assertNotIn('Native Output', review_html)
            self.assertNotIn('Identity-Primed', review_html)
            self.assertNotIn('Ground Truth (Native)', review_html)
            self.assertEqual(client.post('/confirm').status_code, 302)
            english = next(r for r in storage.load_records() if r['id'] == english_id)
            self.assertTrue(app._is_annotation_completed(english))
            self.assertTrue(all(list(output) == ['base'] for output in english['outputs'].values()))
            self.assertEqual(len(storage.load_records()), 2)
            # Saved English-only drafts reload in the same one-prompt layout.
            self.assertEqual(client.post('/load-annotation', data={
                'annotation_id': english_id,
            }).status_code, 302)
            reloaded = client.get('/').get_data(as_text=True)
            self.assertNotIn('id="second_prompt_input"', reloaded)
            self.assertEqual(len(re.findall(r'data-output-preview-for="\w+_llm_output_base"', reloaded)), 4)
            # Public record views retain English answers and historical native text.
            listing = client.get('/records').get_data(as_text=True)
            self.assertIn('English gemini answer', listing)
            self.assertIn('本地語言提示', listing)
            examples = client.get('/examples').get_data(as_text=True)
            self.assertIn('English gemini answer', examples)
            admin_html = client.get('/admin').get_data(as_text=True)
            self.assertIn('English Singapore prompt', admin_html)
            # Peer reviews of English-only records require only four output ratings.
            review_form = {
                'prompt_q0': '4', 'prompt_q2': '4', 'prompt_q3': '4',
                'prompt_q2_comment': 'Relevant context', 'ground_truth_rating': '4',
                'overall_annotation_impact': '4',
                'overall_annotation_impact_comment': 'Good annotation',
                'reviewer_confidence': '4',
            }
            for model in ['gemini', 'gpt', 'llama', 'deepseek']:
                for question in ['q2', 'q3', 'q4']:
                    review_form[f'{model}_base_{question}'] = '4'
                    review_form[f'{model}_base_{question}_comment'] = 'Reviewed'
            with patch.object(app, '_reviewable_records_for_user', return_value=[english]), patch.object(
                app, '_is_iaa_approved_record', return_value=True
            ):
                peer_page = client.get('/review/' + english_id)
                self.assertEqual(peer_page.status_code, 200)
                self.assertNotIn('name="gemini_identity_q2"', peer_page.get_data(as_text=True))
                peer_saved = client.post('/submit_review', data={
                    **review_form, 'annotation_id': english_id,
                })
                self.assertEqual(peer_saved.status_code, 302)
            peer = iaa_store.fetch_iaa_review(english_id, 'test-admin')
            self.assertEqual(peer['model1_base_q1'], 4)
            self.assertIsNone(peer['model1_identity_q1'])
            # Earlier bilingual drafts still show their saved native fields.
            with client.session_transaction() as session:
                session['draft_id'] = draft_store.save_draft(record)
            legacy_page = client.get('/').get_data(as_text=True)
            self.assertIn('id="second_prompt_input"', legacy_page)
            self.assertIn('name="ground_truth_native"', legacy_page)
            self.assertIn('本地語言提示', legacy_page)


if __name__ == '__main__':
    unittest.main()
