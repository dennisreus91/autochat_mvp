# autochat_mvp

This repository contains a minimal Flask backend that can receive an
uploaded photo of a room and a textual prompt describing the desired
renovation.  The request is forwarded to OpenAI's API using the
`dall-e-2` model to generate a new design image.

## Running locally

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Set your OpenAI API key in the environment:

   ```bash
   export OPENAI_API_KEY=sk-...
   ```

3. Start the server:

   ```bash
   python app.py
   ```

4. Configure your Typebot flow to send a `POST` request with a file field
   named `file` and a text field named `prompt` to the `/typebot-webhook`
   endpoint.
