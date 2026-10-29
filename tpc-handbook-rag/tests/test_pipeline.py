import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src import rag

HB = rag.DATA_DIR / "TPC_Student_Handbook.txt"

def test_clean_entities_and_hyphens():
    assert rag._clean("A &amp; B") == "A & B"
    assert rag._clean("inter-\nnational") == "international"
    assert "  " not in rag._clean("a   b")

def test_clean_keeps_number_ranges():
    assert "1:005" not in rag._clean("every Tuesday 1:00-\n5:00PM")


def test_pages_parsed_with_numbers():
    pages = rag.load_file(HB)
    assert len(pages) > 150
    assert any(p["page"] == 33 for p in pages)

def test_chunks_have_metadata_and_size():
    chunks = rag.chunk_records(rag.load_file(HB))
    assert len(chunks) > 300
    assert all(len(c["text"]) <= rag.CHUNK_SIZE + 50 for c in chunks)
    assert all({"text", "source", "page", "section"} <= set(c) for c in chunks)

def test_attendance_rule_is_in_corpus():
    text = " ".join(c["text"] for c in rag.chunk_records(rag.load_file(HB)))
    assert "20%" in text and "Tuesday and Thursday" in text
