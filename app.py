from flask import Flask, request, jsonify
import openai
import requests
import os

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

    # Log the request type and keys present
    if request.is_json:
        data = request.get_json(silent=True) or {}
        app.logger.info(
            "typebot_webhook: JSON request with keys: %s", list(data.keys())
        )
    else:
        app.logger.info(
            "typebot_webhook: form request with form keys=%s files keys=%s",
            list(request.form.keys()),
            list(request.files.keys()),
        )

    # First handle JSON bodies (e.g. Content-Type: application/json)
    if request.is_json:
        data = request.get_json(silent=True) or {}
        prompt = data.get("prompt")
        image_url = data.get("file")
        if not prompt or not image_url:
            return jsonify({'error': 'missing prompt or file'}), 400

        # Fetch the image from the provided URL
        try:
            resp = requests.get(image_url)
            resp.raise_for_status()
            img_bytes = resp.content
            app.logger.info("Downloaded image from %s successfully", image_url)
        except Exception as exc:
            app.logger.error("Failed to download image from %s: %s", image_url, exc)
            return jsonify({'error': f'failed to fetch image: {exc}'}), 400

    else:
        # Fallback: handle multipart form-data requests
        if 'prompt' not in request.form or 'file' not in request.files:
            return jsonify({'error': 'missing prompt or file'}), 400

        prompt = request.form['prompt']
        image_file = request.files['file']
        img_bytes = image_file.read()

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
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500

    # Respond with the generated image URL
    return jsonify({'image_url': image_url})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
