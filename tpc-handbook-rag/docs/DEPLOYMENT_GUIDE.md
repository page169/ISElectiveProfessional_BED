# Deployment Guide: Campus Guide AI (TPC Handbook RAG)

This guide covers everything from a fresh Windows laptop to a public app, a Docker image, a CI/CD pipeline, the evidence files and the submission. Commands are for **PowerShell on Windows**. Mac/Linux notes are at the end.

## Order of work (overview)
1. Set up Python 3.12 and the project
2. Add your Gemini key and build the index
3. Run the app locally and generate the evidence files
4. Run the tests
5. Push to GitHub (public)
6. Deploy on Streamlit Community Cloud
7. Build and run with Docker (Checkpoint 4 requirement)
8. Check the CI/CD run on GitHub
9. Collect deployment evidence
10. Record the demo video and submit

---

## 1. Set up Python and the project
Check your Python versions:
```
py -0
```
If 3.12 is missing:
```
winget install -e --id Python.Python.3.12
```
Close and reopen PowerShell, then in the folder that contains `tpc-handbook-rag` (for example `TPC-Handbook System`):
```
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python --version
cd tpc-handbook-rag
pip install -r requirements-dev.txt
```
`python --version` must show 3.12.x. If activation is blocked, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once.

## 2. Add your Gemini key and build the index
1. Create a free key at https://aistudio.google.com/apikey.
2. Create your private settings file:
```
copy .env.example .env
notepad .env
```
Set `GEMINI_API_KEY=your_key`, save, close. Never commit `.env` (it is already in `.gitignore`).
3. Build the vector index (the first run downloads the embedding model, about 130 MB):
```
python ingest.py
```
Expected: `Indexed 410 chunks`. This creates `index/vectors.npy`, `index/chunks.json` and `index/handbook.faiss`. **Commit these three files** so the deployed app starts with a ready index.

## 3. Run locally and generate evidence
```
streamlit run app.py
```
Test: a policy question (sources should appear), a follow-up (memory), and "Who won the NBA finals?" (must refuse).
Then generate the evidence files (stop Streamlit with Ctrl+C first, or use a second PowerShell window with the venv activated):
```
python scripts/preprocess_demo.py
python scripts/embedding_demo.py
python scripts/compare_metrics.py
python scripts/evaluate.py
```
| Script | Output file | Checkpoint |
|---|---|---|
| `preprocess_demo.py` | `docs/preprocessing_report.md` | 1 |
| `embedding_demo.py` | `docs/embedding_demo_output.txt` | 1 |
| `compare_metrics.py` | `docs/distance_metric_report.md` | 2 |
| `evaluate.py` | `docs/evaluation_results.md` | 3 |

`evaluate.py` calls Gemini about 10 times with pauses; if it hits the free-tier limit, wait a minute and run it again. Copy its score into section 8 of `docs/06_final_technical_report.md`.

## 4. Run the tests
```
pytest -q
```
All 5 tests should pass. The same tests run in GitHub Actions.

## 5. Push to GitHub
1. Install Git if needed: `winget install -e --id Git.Git` (reopen PowerShell afterwards).
2. On github.com, create a **Public** repository named `tpc-handbook-rag` (do not add a README or .gitignore there).
3. From inside `tpc-handbook-rag`:
```
git init
git add .
git status
```
Check that `.env` is **not** listed, and that `index/vectors.npy`, `index/chunks.json`, `index/handbook.faiss` and `data/handbook/TPC_Student_Handbook.txt` are listed. Then:
```
git commit -m "Initial commit: TPC Handbook RAG"
git branch -M main
git remote add origin https://github.com/<your-username>/tpc-handbook-rag.git
git push -u origin main
```
GitHub will ask you to sign in the first time. For commit history that shows progress, make several smaller commits across the weeks (data, preprocessing, retrieval, interface, Docker, docs) rather than one upload.

## 6. Deploy on Streamlit Community Cloud
1. Go to https://share.streamlit.io and sign in with GitHub.
2. Click **Create app** and choose **Deploy a public app from GitHub**.
3. Repository `tpc-handbook-rag`, branch `main`, main file `app.py`.
4. **Advanced settings:** Python version **3.12**; in **Secrets** paste:
```
GEMINI_API_KEY = "your_key"
```
5. Click **Deploy**. The first build takes several minutes. You get a URL like `https://your-app.streamlit.app`.
6. Ask one question yourself so the embedding model is downloaded and warmed up.
7. Open the URL in an **incognito window**: it must load with no login.
8. Keep it alive until grades are released: visit every few days and use "Wake up" if it sleeps.

Every `git push` to `main` redeploys automatically; this is your simple CD step.

## 7. Build and run with Docker
1. Install Docker Desktop: `winget install -e --id Docker.DockerDesktop`, restart the laptop, open Docker Desktop and wait until it says it is running (it uses WSL 2; accept the prompts to enable it).
2. In `tpc-handbook-rag` (with `.env` containing your key):
```
docker build -t tpc-handbook-rag .
docker run --rm -p 8501:8501 --env-file .env tpc-handbook-rag
```
or:
```
docker compose up --build
```
3. Open http://localhost:8501. The first build is slow because it downloads packages and the embedding model into the image; later builds are cached.
4. Stop with Ctrl+C.

What the Dockerfile does: **stage 1** installs dependencies and pre-downloads the embedding model; **stage 2** copies only the virtual environment, the model and the app into a slim image that runs as a non-root user with a health check. The API key is **not** in the image; it comes from `--env-file` or `-e GEMINI_API_KEY=...` at run time. If `index/` was not committed, the container builds the index on first start.

## 8. CI/CD on GitHub
The workflow `.github/workflows/ci.yml` runs on every push:
1. installs dependencies, compiles the code, runs `pytest`;
2. builds the Docker image;
3. on `main`, pushes it to GitHub Container Registry as `ghcr.io/<your-username>/tpc-handbook-rag:latest`.

Check it under the repository's **Actions** tab. A green check means success. If the image push is denied, open **Settings > Actions > General > Workflow permissions** and select **Read and write permissions**.

## 9. Collect deployment evidence (Checkpoint 4)
Create `docs/evidence/` and save screenshots, then fill in `docs/05_deployment_evidence.md`:
| Screenshot | File name |
|---|---|
| Public Streamlit app in an incognito window (URL visible) | `app_public.png` |
| `docker build` finishing | `docker_build.png` |
| Container running at localhost:8501 | `docker_run.png` |
| Green GitHub Actions run | `github_actions.png` |
Then commit and push them.

## 10. Demo video and submission
Use `docs/demo_script.md`. Record 5-8 minutes covering: the problem and source; the architecture (bge-small embeddings, FAISS, Gemini, LangChain); a live walkthrough of the **public** app; at least 3 questions including one the handbook cannot answer; and what you would improve. Upload to Google Drive or YouTube (unlisted), set sharing to **Anyone with the link**, and test in incognito.

Fill the placeholders in `README.md` (live app link, video link, data source), then submit **the repo URL, the live app URL and the video link** together in Google Classroom before the deadline.

## Final checklist
- [ ] Repository is Public; `.env` is not in it; `.env.example` is
- [ ] `index/` files and the handbook file are committed
- [ ] App opens in incognito with no login; out-of-scope question is refused
- [ ] `pytest -q` passes; GitHub Actions is green
- [ ] Docker image builds and runs; screenshots saved
- [ ] All `docs/` files complete; results filled in the final report
- [ ] README placeholders replaced
- [ ] Video plays in incognito
- [ ] Three links submitted before the deadline

## Troubleshooting
| Problem | Fix |
|---|---|
| `python --version` shows 3.14 | Re-create the venv with `py -3.12 -m venv .venv` and activate it |
| `pip install` fails on a package | Make sure the venv is active and Python is 3.12; run `python -m pip install --upgrade pip` and retry |
| "No index found" in the app | Run `python ingest.py`; on Streamlit Cloud, commit the `index/` files |
| "Missing API key" | Check `.env` (local), Streamlit Secrets (cloud) or `--env-file` (Docker); the name must be `GEMINI_API_KEY` |
| "Something went wrong" / model error | Open **Technical details** under the message. If it says the model was not found, run `python scripts/check_setup.py` and set `GEMINI_MODEL` in `.env` (and in Streamlit Secrets). Gemini 2.5 models were shut down in Oct 2026 |
| Rate-limit message | Free-tier quota; wait a minute and retry. Mention the limit in the README and video |
| Streamlit build fails | In Advanced settings choose Python 3.12 and redeploy |
| Bot refuses valid questions | Lower the Relevance threshold slider (try 0.35) |
| Bot answers off-topic questions | Raise the threshold (try 0.45) |
| `docker` not recognized | Start Docker Desktop and open a new PowerShell |
| Docker build very slow | Normal on the first run (model download); later builds use the cache |
| Key committed by mistake | Revoke it at aistudio.google.com/apikey, create a new one, update your secrets (-5 points otherwise) |
| Handbook updated | Replace the file in `data/handbook/`, run `python ingest.py`, commit `index/`, push |

## Mac/Linux notes
Use `python3.12 -m venv .venv` and `source .venv/bin/activate`, and `copy` becomes `cp .env.example .env`. Install Git and Docker with your package manager or Docker Desktop.
