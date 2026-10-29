"""Checkpoint 1: text preprocessing demo with before/after evidence.
Run: python scripts/preprocess_demo.py   -> writes docs/preprocessing_report.md"""
import re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src import rag

RAW = rag.DATA_DIR / "TPC_Student_Handbook.txt"
raw = RAW.read_text(encoding="utf-8", errors="ignore")
pages = rag.load_file(RAW)
chunks = rag.chunk_records(pages)
tok = lambda s: re.findall(r"\w+|[^\w\s]", s.lower())

def snippet(pattern, width=260):
    m = re.search(pattern, raw)
    if not m: return None
    s = raw[max(0, m.start() - 60): m.start() + width]
    return s, rag._clean(s)

ex = {
    "HTML-entity noise (&amp;)": snippet(r"&amp;|& amp;"),
    "Hyphenated line breaks": snippet(r"\w-\r?\n\w"),
    "Windows line endings and uneven spacing": snippet(r"[ \t]{2,}\S"),
}
hdr = rag._PAGE_RE.search(raw, 20000)
ex["Repeated page header and page number"] = (raw[hdr.start(): hdr.start() + 160],
    "(removed; page number stored as metadata -> page=%s)" % (hdr.group(2) or hdr.group(1)))

raw_tokens, clean_tokens = tok(raw), tok(" ".join(p["text"] for p in pages))
sizes = [len(c["text"]) for c in chunks]
sample = next(c for c in chunks if c["page"] == 33)
out = ["# Preprocessing Report (Checkpoint 1)", "",
 f"Source: `{RAW.name}` (TPC Student Handbook v.04, plain-text export).", "",
 "## Pipeline", "1. Split the raw text on its printed page headers and recover page numbers.",
 "2. Track the current Article/Chapter heading for each page (section metadata).",
 "3. Clean: remove soft hyphens and carriage returns, decode HTML entities, re-join hyphenated words, collapse whitespace.",
 f"4. Chunk with `RecursiveCharacterTextSplitter` ({rag.CHUNK_SIZE} characters, {rag.CHUNK_OVERLAP} overlap).",
 "5. Tokenize (regex word/punctuation tokens shown below; the embedding model uses its own WordPiece tokenizer).", "",
 "## Dataset statistics", "| Measure | Value |", "|---|---|",
 f"| Pages parsed | {len(pages)} |", f"| Characters before cleaning | {len(raw):,} |",
 f"| Characters after cleaning | {sum(len(p['text']) for p in pages):,} |",
 f"| Regex tokens before / after | {len(raw_tokens):,} / {len(clean_tokens):,} |",
 f"| Chunks | {len(chunks)} |", f"| Chunk length min / mean / max | {min(sizes)} / {sum(sizes)//len(sizes)} / {max(sizes)} |", "",
 "## Before and after examples"]
for name, pair in ex.items():
    if not pair: continue
    b, a = pair
    out += [f"### {name}", "**Before**", "```", b.replace("\r", "\\r"), "```", "**After**", "```", a, "```", ""]
out += ["## Tokenization example", f"Sentence: `{sample['text'][:120].replace(chr(10), ' ')}`", "",
        f"Tokens: `{tok(sample['text'][:120])}`", "",
 "## Reflection: what was messy and how it was handled",
 "- The handbook was exported to plain text, so the original PDF page structure was lost. I rebuilt pages from the repeated `TPC STUDENT HANDBOOK v.04` header and its page number.",
 "- Headers and page numbers repeated on every page and would pollute embeddings. They were stripped and kept only as metadata for citations.",
 "- HTML entities such as `&amp;`, hyphenated line breaks and irregular whitespace were normalised.",
 "- Some pages contain OCR/export artifacts (for example digits embedded inside words on the OJT pages). These are rare and were left as-is rather than risk altering policy text.",
 "- Tables (grading scale, prospectus) flatten into short lines; retrieval still works but table answers are the weakest case. A layout-aware PDF parser would help.",
 "- Section labels come from the nearest Article/Chapter heading and can be off on a page where a new chapter starts partway down."]
Path("docs/preprocessing_report.md").write_text("\n".join(out), encoding="utf-8")
print("Wrote docs/preprocessing_report.md;", len(pages), "pages,", len(chunks), "chunks")
