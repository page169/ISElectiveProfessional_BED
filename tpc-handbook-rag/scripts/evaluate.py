"""Checkpoint 3: demo queries + keyword-based evaluation. Needs GEMINI_API_KEY and a built index.
Run: python scripts/evaluate.py  -> writes docs/evaluation_results.md"""
import sys, time
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src import rag

# (question, keyword that a correct grounded answer/source must contain, in_scope?)
CASES = [
 ("How many absences are allowed per semester?", "20%", True),
 ("When can students consult the college physician?", "tuesday", True),
 ("What are the library hours?", "8:00", True),
 ("What is the penalty for a second major offense?", "twenty-one", True),
 ("What GWA is needed for Cum Laude?", "1.51", True),
 ("What documents do transferees need to submit?", "honorable dismissal", True),
 ("Who won the NBA finals last year?", "", False),
 ("What is the capital of France?", "", False),
]
store, history, rows, ok = rag.VectorStore(), [], [], 0
log = ["# Evaluation Results (Checkpoint 3)", "", f"Model: {rag.LLM_MODEL}; embeddings: {rag.EMBED_MODEL}; FAISS cosine index; top-5, threshold 0.40.", ""]
for q, kw, in_scope in CASES:
    res = rag.answer(q, [], store)
    text = (res["answer"] + " " + " ".join(h.text for h in res["sources"])).lower()
    passed = (res["in_scope"] and kw in text) if in_scope else (not res["in_scope"])
    ok += passed
    pages = ", ".join(f"p.{h.page}" for h in res["sources"][:3]) or "-"
    rows.append(f"| {q} | {'in-scope' if in_scope else 'out-of-scope'} | {'PASS' if passed else 'FAIL'} | {pages} |")
    log += [f"### {q}", res["answer"], f"*Sources:* {pages}", ""]
    time.sleep(4)                                   # stay under free-tier rate limits
# multi-turn memory check
h = [{"role": "user", "content": "What is the dress code?"}]
first = rag.answer(h[0]["content"], [], store); h.append({"role": "assistant", "content": first["answer"]})
follow = rag.answer("Are slippers allowed?", h, store)
log += ["### Multi-turn memory test", "Q1: What is the dress code?  Q2: Are slippers allowed?",
        f"Rewritten standalone query: `{follow['query']}`", follow["answer"], ""]
summary = ["| Question | Type | Result | Top pages |", "|---|---|---|---|"] + rows
summary += ["", f"**Score: {ok}/{len(CASES)}** ({ok/len(CASES):.0%})"]
Path("docs/evaluation_results.md").write_text("\n".join(log[:4] + summary + [""] + log[4:]), encoding="utf-8")
print(f"Score {ok}/{len(CASES)}; wrote docs/evaluation_results.md")
