# Deployment Evidence (Checkpoint 4)
Fill in after deploying. Keep screenshots in `docs/evidence/`.

## 1. Public app
- Live URL: `<paste Streamlit URL>`
- Opened in an incognito window with no login: yes / no (date: ____)
- Screenshot: `docs/evidence/app_public.png`

## 2. Containerized run
```
docker build -t tpc-handbook-rag .
docker run --rm -p 8501:8501 -e GEMINI_API_KEY=<your key> tpc-handbook-rag
# or: docker compose up --build
```
- Screenshot of `docker build` finishing: `docs/evidence/docker_build.png`
- Screenshot of the container serving http://localhost:8501: `docs/evidence/docker_run.png`
- Image published to GitHub Container Registry by CI: `ghcr.io/<username>/tpc-handbook-rag:latest`

## 3. CI/CD
Workflow file: `.github/workflows/ci.yml`. On every push it compiles the code, runs `pytest`, builds the Docker image and (on `main`) pushes it to GHCR. Streamlit Community Cloud redeploys automatically on each push to `main`.
- Screenshot of a green Actions run: `docs/evidence/github_actions.png`

## 4. Secrets handling
- `GEMINI_API_KEY` is read from the environment (`.env` locally, Streamlit Secrets in the cloud, `-e` or `env_file` in Docker).
- `.env` and `.streamlit/secrets.toml` are in `.gitignore` and `.dockerignore`; the key is never copied into the image.
- `.env.example` lists variable names only.
- The container runs as a non-root user and exposes a health check.

## 5. Recorded run
Demo video link: `<paste link>`
