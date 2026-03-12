# Prompt Slimmer Web App

Full-stack tool that shortens prompts before you send them to Lobster. Paste a prompt, tweak the summary ratio, and copy the lean output.

## Features

- Flask API (`/api/shorten`) that performs extractive summarization + optional shorthand
- Vanilla JS frontend with live controls, token stats, and clipboard copy
- Ready for GitHub deployment (frontend + backend folders)

## Local development

```bash
cd web/token-shortener/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py  # serves frontend + API on http://127.0.0.1:5050
```

Open <http://127.0.0.1:5050> in your browser.

## Deployment notes

- The backend is a single Flask file; you can deploy it to Render/Fly/Heroku/etc.
- For GitHub Pages or another static host, deploy `frontend/` and point it at a hosted API origin (set `API_BASE` in `app.js`).
- Once you share GitHub credentials, we can initialize a repo and push this project.
