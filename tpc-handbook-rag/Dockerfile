# ---- Stage 1: build dependencies and pre-download the embedding model ----
FROM python:3.12-slim AS builder
ENV PIP_NO_CACHE_DIR=1 PYTHONDONTWRITEBYTECODE=1
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
WORKDIR /build
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN python -c "from fastembed import TextEmbedding; TextEmbedding('BAAI/bge-small-en-v1.5', cache_dir='/opt/models')"

# ---- Stage 2: slim runtime image ----
FROM python:3.12-slim
ENV PATH="/opt/venv/bin:$PATH" FASTEMBED_CACHE_PATH=/opt/models \
    PYTHONUNBUFFERED=1 STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
RUN useradd --create-home --uid 1000 app
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /opt/models /opt/models
WORKDIR /app
COPY --chown=app:app app.py ingest.py ./
COPY --chown=app:app src ./src
COPY --chown=app:app data ./data
COPY --chown=app:app index ./index
USER app
EXPOSE 8501
HEALTHCHECK --interval=30s --timeout=5s CMD python -c "import urllib.request;urllib.request.urlopen('http://localhost:8501/_stcore/health')"
# Build the index on first start if it was not committed; the API key comes from the environment.
CMD ["sh", "-c", "[ -f index/vectors.npy ] || python ingest.py; exec streamlit run app.py --server.port=8501 --server.address=0.0.0.0"]
