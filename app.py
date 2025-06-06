from flask import Flask, request, jsonify
import openai
import os
import base64

app = Flask(__name__)

# Set your OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/typebot-webhook', methods=['POST'])
def typebot_webhook():
    """Receive image and prompt from Typebot and return a new image URL."""
    if 'prompt' not in request.form or 'file' not in request.files:
        return jsonify({'error': 'missing prompt or file'}), 400

    prompt = request.form['prompt']
    image_file = request.files['file']

    # Read image bytes
    img_bytes = image_file.read()

    # Prepare image for OpenAI API (assuming gptimage1 supports base64 images)
    image_base64 = base64.b64encode(img_bytes).decode('utf-8')

    try:
        response = openai.Image.create_edit(
            model="gptimage1",
            image=image_base64,
            prompt=prompt,
            n=1,
            size="1024x1024",
            response_format="url",
        )
        image_url = response['data'][0]['url']
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500

    # Respond with the generated image URL
    return jsonify({'image_url': image_url})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
