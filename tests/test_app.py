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


def test_task_is_created():
    client = app.test_client()

    class DummyThread:
        def __init__(self, target, daemon=None):
            self.target = target
        def start(self):
            self.target()

    with patch('requests.get') as mock_get, \
         patch('app.threading.Thread', DummyThread), \
         patch.object(app.client.images, 'edit') as mock_edit:
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = b'data'
        mock_edit.return_value.data = [type('obj', (object,), {'url': 'http://fake'})]
        resp = client.post('/typebot-webhook', json={'file': 'http://x/img.jpg', 'prompt': 'design'})
    assert resp.status_code == 202
    data = resp.get_json()
    assert 'task_id' in data
    task = app.tasks[data['task_id']]
    assert task['status'] == 'done'
    assert task['result']['image_url'] == 'http://fake'
