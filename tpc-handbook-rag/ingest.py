"""CLI: build the vector index from files in data/handbook/.  Usage: python ingest.py"""
from dotenv import load_dotenv
load_dotenv()
from src.rag import build_index, DATA_DIR

if __name__ == "__main__":
    n = build_index()
    print(f"Indexed {n} chunks from {DATA_DIR}. Saved to index/.")
