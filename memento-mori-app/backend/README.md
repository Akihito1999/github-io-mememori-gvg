# Backend (FastAPI)

A thin proxy with in-memory caching for https://api.mentemori.icu .

## Run locally

python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

## Docker

docker build -t memento-backend ./backend

# Run
# Allow only your Pages origin in production, e.g. https://USERNAME.github.io
# docker run -p 8000:8000 -e ALLOWED_ORIGIN=https://<username>.github.io -e CACHE_TTL=60 memento-backend