from django.core.management.base import BaseCommand
from django.conf import settings
import requests
import json
import os

class Command(BaseCommand):
    help = 'Check Gemini (GEMINI_API_URL and GEMINI_API_KEY) connectivity from this machine.'

    def handle(self, *args, **options):
        api_key = getattr(settings, 'GEMINI_API_KEY', None)
        api_url = getattr(settings, 'GEMINI_API_URL', None)

        # If settings didn't pick up .env (common in some dev setups), try loading .env
        if not api_key or not api_url:
            try:
                # prefer BASE_DIR from settings if available
                from dotenv import load_dotenv
                env_path = None
                if hasattr(settings, 'BASE_DIR') and settings.BASE_DIR:
                    env_path = os.path.join(str(settings.BASE_DIR), '.env')
                else:
                    # fallback: attempt to find project root relative to this file
                    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env'))
                load_dotenv(env_path)
                # re-read after loading
                api_key = api_key or os.environ.get('GEMINI_API_KEY')
                api_url = api_url or os.environ.get('GEMINI_API_URL')
                if api_key and api_url:
                    self.stdout.write(f'Loaded .env from: {env_path}')
            except Exception:
                # ignore errors here; we'll show the original message below
                pass

        if not api_key or not api_url:
            self.stdout.write(self.style.ERROR('GEMINI_API_KEY or GEMINI_API_URL not set.'))
            return

        headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
        body = {"contents": [{"role": "user", "parts": [{"text": "Ping from check_gemini command"}]}]}
        self.stdout.write('Pinging %s ...' % api_url)
        try:
            resp = requests.post(api_url, headers=headers, json=body, timeout=10)
        except Exception as e:
            self.stdout.write(self.style.ERROR('Request failed: %s' % e))
            return

        self.stdout.write('Status code: %s' % resp.status_code)
        try:
            j = resp.json()
            self.stdout.write(self.style.SUCCESS('Response JSON received (truncated):'))
            self.stdout.write(json.dumps(j, indent=2)[:2000])
            # If we got an authentication error, try Application Default Credentials (ADC) if available
            if resp.status_code == 401:
                try:
                    # Attempt ADC: get a token and retry without the ?key= param
                    try:
                        import google.auth
                        import google.auth.transport.requests
                    except Exception:
                        self.stdout.write('google-auth not available; skip ADC retry. To enable ADC retry, install google-auth.')
                        raise

                    self.stdout.write('\nAttempting Application Default Credentials (ADC) retry...')
                    creds, project = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
                    auth_req = google.auth.transport.requests.Request()
                    creds.refresh(auth_req)
                    token = creds.token
                    if token:
                        # strip query params (key) from api_url if present
                        url_no_key = api_url.split('?', 1)[0]
                        hdrs = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
                        r2 = requests.post(url_no_key, headers=hdrs, json=body, timeout=10)
                        self.stdout.write('\nADC retry status: %s' % r2.status_code)
                        try:
                            self.stdout.write(json.dumps(r2.json(), indent=2)[:2000])
                        except Exception:
                            self.stdout.write(r2.text[:2000])
                        # if ADC retry succeeded (2xx), we can finish here
                        if 200 <= r2.status_code < 300:
                            return
                except Exception:
                    # Keep going to the ListModels diagnostics below
                    pass
            # If the API returned an authentication or model-not-found error, also call ListModels
            if resp.status_code in (401, 404):
                self.stdout.write('\nEncountered %s from generateContent — calling ListModels to show available models...' % resp.status_code)
                try:
                    key = api_key
                    for base in ('v1', 'v1beta'):
                        try:
                            lm_url = f'https://generativelanguage.googleapis.com/{base}/models'
                            r = requests.get(lm_url, params={'key': key}, timeout=10)
                            self.stdout.write('\nListModels %s status: %s' % (base, r.status_code))
                            try:
                                lj = r.json()
                                models = lj.get('models') or lj.get('model') or []
                                if isinstance(models, dict):
                                    models = [models]
                                if not models:
                                    self.stdout.write('  (no models returned or unexpected schema)')
                                else:
                                    for m in models[:50]:
                                        name = m.get('name') or m.get('model') or str(m)
                                        desc = m.get('description') or ''
                                        self.stdout.write('  - %s  %s' % (name, ('- ' + desc) if desc else ''))
                            except Exception:
                                self.stdout.write('  (non-json ListModels response)')
                        except Exception as e:
                            self.stdout.write('  ListModels request error for %s: %s' % (base, e))
                except Exception:
                    pass
        except Exception:
            self.stdout.write(self.style.WARNING('Non-JSON response (truncated):'))
            self.stdout.write(resp.text[:2000])
            # If we received a 401 or 404, attempt to call ListModels to help the user pick a valid model
            if resp.status_code in (401, 404):
                try:
                    self.stdout.write('\nEncountered %s from generateContent — calling ListModels to show available models...' % resp.status_code)
                    key = api_key
                    for base in ('v1', 'v1beta'):
                        try:
                            lm_url = f'https://generativelanguage.googleapis.com/{base}/models'
                            r = requests.get(lm_url, params={'key': key}, timeout=10)
                            self.stdout.write('\nListModels %s status: %s' % (base, r.status_code))
                            try:
                                j = r.json()
                                # Print a compact list of model names
                                models = j.get('models') or j.get('model') or []
                                if isinstance(models, dict):
                                    models = [models]
                                if not models:
                                    self.stdout.write('  (no models returned or unexpected schema)')
                                else:
                                    for m in models[:50]:
                                        name = m.get('name') or m.get('model') or str(m)
                                        # show possible supported methods if present
                                        desc = m.get('description') or ''
                                        self.stdout.write('  - %s  %s' % (name, ('- ' + desc) if desc else ''))
                            except Exception:
                                self.stdout.write('  (non-json ListModels response)')
                        except Exception as e:
                            self.stdout.write('  ListModels request error for %s: %s' % (base, e))
                except Exception:
                    pass
