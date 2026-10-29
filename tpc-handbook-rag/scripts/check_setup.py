"""Diagnose the Gemini key, available models and embeddings.  Run: python scripts/check_setup.py"""
import json, os, sys, urllib.error, urllib.request
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
print("1. API key found:", bool(key))
if not key:
    sys.exit("   Put GEMINI_API_KEY=... in your .env file.")

def call(url, body=None):
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body else None,
                                 headers={"Content-Type": "application/json", "x-goog-api-key": key})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.read().decode()[:300]}"}

base = "https://generativelanguage.googleapis.com/v1beta"
models = call(f"{base}/models?pageSize=200")
if "error" in models:
    sys.exit("2. Could not list models -> " + models["error"])
names = [m["name"].split("/")[-1] for m in models.get("models", [])
         if "generateContent" in m.get("supportedGenerationMethods", [])]
flash = [n for n in names if "flash" in n and "image" not in n and "tts" not in n and "live" not in n]
print("2. Models your key can use (Flash family):", ", ".join(flash) or "none found")
configured = os.getenv("GEMINI_MODEL", "gemini-flash-latest")
print("3. Configured model:", configured, "->", "available" if configured in names else "NOT in your list")
test = configured if configured in names else (flash[0] if flash else None)
if test:
    r = call(f"{base}/models/{test}:generateContent", {"contents": [{"parts": [{"text": "Reply with the word OK."}]}]})
    print("4. Test call to", test, "->", r.get("error") or r["candidates"][0]["content"]["parts"][0]["text"].strip())
    if test != configured:
        print(f"   Fix: add GEMINI_MODEL={test} to your .env (and to Streamlit Secrets).")
try:
    from src import rag
    v = rag.embed_query("test")
    print("5. Embedding model OK, dimension", v.shape[0])
except Exception as e:
    print("5. Embedding model problem:", e)
print("6. Index built:", rag.VectorStore.exists())
