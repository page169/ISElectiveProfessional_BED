"""Checkpoint 1: embedding generation demo. Run: python scripts/embedding_demo.py"""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src import rag

pages = rag.load_file(rag.DATA_DIR / "TPC_Student_Handbook.txt")
chunks = rag.chunk_records(pages)
sample = chunks[100:105]
vecs = rag.embed_documents([c["text"] for c in sample])
lines = [f"Model: {rag.EMBED_MODEL}", f"Embedding dimension: {vecs.shape[1]}",
         f"Vector L2 norms (should be 1.0 after normalisation): {np.round(np.linalg.norm(vecs, axis=1), 3).tolist()}", ""]
for q in ["How many absences are allowed?", "What is the dress code?", "How is GWA computed?"]:
    qv = rag.embed_query(q); sims = vecs @ qv
    lines.append(f"Query: {q}\n  cosine to 5 sample chunks: {np.round(sims, 3).tolist()}")
lines.append("\nFirst 8 values of chunk 0 vector: " + str(np.round(vecs[0][:8], 4).tolist()))
Path("docs/embedding_demo_output.txt").write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))
