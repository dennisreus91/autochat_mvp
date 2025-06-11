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

4. Configure your Typebot flow to send a `POST` request to the
   `/typebot-webhook` endpoint. You can either send multipart form-data with
  a file field named `file` and a text field named `prompt`, or send a JSON
  body with keys `file` (containing an image URL) and `prompt`. When using
  the JSON approach the server downloads the image with a 10‑second
  timeout. If the download does not finish in time, the API responds with a
  `504` error.

Flask's default logging writes to the console. Inspect these logs for
information about request handling and any image download errors when
troubleshooting.
