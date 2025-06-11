import os
from unittest.mock import patch
import requests

# Ensure OpenAI key is set so app can import
os.environ.setdefault("OPENAI_API_KEY", "test-key")

from app import app


def test_image_download_timeout():
    client = app.test_client()
    with patch('requests.get', side_effect=requests.exceptions.Timeout):
        resp = client.post('/typebot-webhook', json={'file': 'http://example.com/img.jpg', 'prompt': 'design'})
    assert resp.status_code == 504
    assert resp.is_json
    assert resp.get_json() == {'error': 'image download timed out'}
