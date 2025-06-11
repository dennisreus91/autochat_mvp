from flask import Flask, request, jsonify
import openai
import requests
import os
import uuid
import threading


tasks = {}

app = Flask(__name__)

# Set your OpenAI API key from environment variable
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise RuntimeError("OPENAI_API_KEY environment variable not set")

# Create OpenAI client
client = openai.OpenAI(api_key=openai_api_key)

@app.route('/typebot-webhook', methods=['POST'])
def typebot_webhook():
    """Receive image and prompt from Typebot and return a new image URL."""
    img_bytes = None
    prompt = None

    # First handle JSON bodies (e.g. Content-Type: application/json)
    if request.is_json:
        data = request.get_json(silent=True) or {}
        prompt = data.get("prompt")
        image_url = data.get("file")
        if not prompt or not image_url:
            return jsonify({'error': 'missing prompt or file'}), 400

        # Fetch the image from the provided URL with a timeout
        try:
            resp = requests.get(image_url, timeout=10)
            resp.raise_for_status()
            img_bytes = resp.content
        except requests.exceptions.Timeout:
            return jsonify({'error': 'image download timed out'}), 504
        except Exception as exc:
            return jsonify({'error': f'failed to fetch image: {exc}'}), 400

    else:
        # Fallback: handle multipart form-data requests
        if 'prompt' not in request.form or 'file' not in request.files:
            return jsonify({'error': 'missing prompt or file'}), 400

        prompt = request.form['prompt']
        image_file = request.files['file']
        img_bytes = image_file.read()

    task_id = str(uuid.uuid4())
    tasks[task_id] = {'status': 'pending', 'result': None}

    def run_openai():
        try:
            response = client.images.edit(
                model="dall-e-2",
                image=img_bytes,
                prompt=prompt,
                n=1,
                size="1024x1024",
                response_format="url",
            )
            image_url = response.data[0].url
            tasks[task_id] = {
                'status': 'done',
                'result': {'image_url': image_url}
            }
        except Exception as exc:
            tasks[task_id] = {
                'status': 'error',
                'result': {'error': str(exc)}
            }

    threading.Thread(target=run_openai, daemon=True).start()

    return jsonify({'task_id': task_id}), 202


@app.route('/task/<task_id>', methods=['GET'])
def get_task(task_id):
    task = tasks.get(task_id)
    if not task:
        return jsonify({'error': 'invalid task id'}), 404
    if task['status'] == 'pending':
        return jsonify({'status': 'pending'}), 202
    return jsonify(task['result'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
