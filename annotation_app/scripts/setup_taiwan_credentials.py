"""Run interactively on the Taiwan server; secrets are never printed."""
import json
import secrets
from getpass import getpass
from pathlib import Path
from werkzeug.security import generate_password_hash


def required(label, confirm=False):
    while True:
        value = getpass(label).strip()
        if not value:
            print('A value is required.')
        elif confirm and value != getpass('Confirm: ').strip():
            print('Values did not match; try again.')
        else:
            return value


def main():
    folder = Path(__file__).resolve().parents[1] / 'accounts' / 'taiwan'
    folder.mkdir(parents=True, exist_ok=True, mode=0o700)
    path = folder / 'apikeys.json'
    text = path.read_text(encoding='utf-8').strip() if path.exists() else ''
    config = json.loads(text) if text else {}
    config.setdefault('ADMIN_USERNAME', 'admin')
    if not config.get('FLASK_SECRET_KEY'):
        config['FLASK_SECRET_KEY'] = secrets.token_hex(32)
    for name, label in [
        ('ADMIN_PASSWORD_HASH', 'Set Taiwan admin password: '),
        ('ANNOTATOR_PASSWORD_HASH', 'Set Taiwan signup invitation code: '),
    ]:
        if not config.get(name):
            config[name] = generate_password_hash(required(label, confirm=True))
    for name in ['GROQ_QWEN_API_KEY', 'GROQ_GPT_OSS_API_KEY',
                 'OPENROUTER_LLAMA_API_KEY', 'OPENROUTER_DEEPSEEK_API_KEY']:
        if not str(config.get(name) or '').strip():
            config[name] = required(name + ': ')
    temp = path.with_suffix('.json.tmp')
    temp.touch(mode=0o600, exist_ok=True)
    temp.chmod(0o600)
    temp.write_text(json.dumps(config, indent=2), encoding='utf-8')
    temp.replace(path)
    path.chmod(0o600)
    print('Taiwan private settings saved. Existing configured values were preserved.')


if __name__ == '__main__':
    main()
