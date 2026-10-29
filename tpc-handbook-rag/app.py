import html

import streamlit as st
from dotenv import load_dotenv

load_dotenv()
from src import rag

st.set_page_config(page_title="Campus Guide AI", page_icon="🎓", layout="wide")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"], .stApp {font-family:'Inter',system-ui,sans-serif;}
.stApp {background:#F8FAFC;color:#0F172A;}
[data-testid="stSidebar"] {background:#FFFFFF;border-right:1px solid #E2E8F0;}
#MainMenu, footer {visibility:hidden;}
.block-container {max-width:960px;padding-top:2rem;}
.brand {display:flex;align-items:center;gap:10px;font-weight:700;font-size:1.05rem;margin-bottom:6px;}
.brand i {width:34px;height:34px;border-radius:10px;background:#2563EB;color:#fff;display:grid;
  place-items:center;font-style:normal;}
.hb {border:1px solid #CBD5E1;border-radius:12px;padding:10px 12px;background:#F8FAFC;font-size:.85rem;margin:8px 0 14px;}
.hb b {display:block;color:#0F172A;} .hb span {color:#475569;}
.stButton>button {border-radius:10px;border:1px solid #CBD5E1;font-weight:500;}
.stButton>button[kind="primary"] {background:#2563EB;border-color:#2563EB;color:#fff;}
[data-testid="stSidebar"] .stButton>button {justify-content:flex-start;text-align:left;border:0;background:transparent;color:#475569;}
[data-testid="stSidebar"] .stButton>button[kind="primary"] {background:#EFF6FF;color:#1D4ED8;font-weight:600;}
.hero h1 {font-size:2rem;margin:0 0 4px;} .hero p {color:#475569;margin:0 0 18px;}
.cat {font-weight:600;color:#1D4ED8;font-size:.9rem;margin:6px 0 2px;}
.note {color:#475569;font-size:.8rem;margin-top:24px;}
.pill {display:inline-block;background:#CCFBF1;color:#0F766E;border-radius:99px;padding:2px 10px;
  font-size:.75rem;font-weight:600;}
.warn {background:#FFFBEB;border:1px solid #FDE68A;border-radius:12px;padding:12px 14px;color:#78350F;}
[data-testid="stChatMessage"] {background:#FFFFFF;border:1px solid #E2E8F0;border-radius:16px;padding:14px 16px;}
[data-testid="stForm"] {border:1px solid #CBD5E1;border-radius:16px;background:#fff;}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

CATEGORIES = [
    ("Attendance and Absences", "What is the maximum number of absences allowed?"),
    ("Academic Policies", "How do I add or drop a subject?"),
    ("Student Conduct", "What are the major offenses and their penalties?"),
    ("Grading and Examinations", "How is the GWA computed?"),
    ("Enrollment and Requirements", "What are the admission requirements for transferees?"),
    ("Student Services", "When can I consult the college physician?"),
]
FOLLOW_UPS = ["Can you explain that more simply?", "Are there any exceptions?"]

S = st.session_state
S.setdefault("page", "Home")
S.setdefault("messages", [])
S.setdefault("conversations", [])
S.setdefault("saved", [])
S.setdefault("needs_answer", False)
S.setdefault("feedback", {})


def go(page):
    S.page = page


def ask(q: str):
    S.messages.append({"role": "user", "content": q})
    S.needs_answer = True
    S.page = "Ask the handbook"


def archive_current():
    if S.messages:
        first = next((m["content"] for m in S.messages if m["role"] == "user"), "Conversation")
        S.conversations.insert(0, {"title": first[:70], "messages": S.messages})
    S.messages = []


# ------------------------------------------------------------------ sidebar
with st.sidebar:
    st.markdown('<div class="brand"><i>C</i>Campus Guide AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="hb"><b>TPC Student Handbook</b><span>Version 4.0 · Active source</span></div>',
                unsafe_allow_html=True)
    for label in ["Home", "Ask the handbook", "History & saved", "Help & support"]:
        st.button(label, key=f"nav_{label}", use_container_width=True,
                  type="primary" if S.page == label else "secondary",
                  on_click=go, args=(label,))
    if st.button("＋ New chat", use_container_width=True):
        archive_current()
        S.page = "Ask the handbook"
        st.rerun()
    st.divider()
    with st.expander("Search settings"):
        k = st.slider("Passages retrieved", 2, 8, 5)
        min_score = st.slider("Relevance threshold", 0.20, 0.70, 0.40, 0.01,
                              help="Passages scoring below this are ignored; if none remain the assistant declines.")
    smart_fu = st.checkbox("Smart follow-up suggestions", value=False,
                           help="Uses one extra API call per answer.")
    with st.expander("Admin: rebuild index"):
        ups = st.file_uploader("Upload handbook (PDF/DOCX/TXT/MD)", accept_multiple_files=True,
                               type=["pdf", "docx", "txt", "md"])
        if ups and st.button("Ingest uploaded files"):
            rag.DATA_DIR.mkdir(parents=True, exist_ok=True)
            paths = []
            for u in ups:
                p = rag.DATA_DIR / u.name
                p.write_bytes(u.getbuffer())
                paths.append(p)
            with st.spinner("Parsing, chunking, embedding..."):
                n = rag.build_index(paths)
            st.cache_resource.clear()
            st.success(f"Indexed {n} chunks.")
    st.caption("Free-tier API: if you see a limit message, wait a minute and retry.")


@st.cache_resource(show_spinner="Loading handbook index...")
def get_store():
    return rag.VectorStore()


if not rag.VectorStore.exists():
    st.warning("No index found. Put the handbook in `data/handbook/` and run `python ingest.py`, "
               "or upload it under *Admin: rebuild index* in the sidebar.")
    st.stop()
store = get_store()


# ------------------------------------------------------------------- pieces
def render_sources(sources, key):
    if not sources:
        return
    with st.expander(f"📎 Sources ({len(sources)})"):
        for i, h in enumerate(sources, 1):
            page = f" · Page {h['page']}" if h["page"] else ""
            st.markdown(f"**[{i}] {h['section'] or h['source']}**{page}")
            st.caption(f"{h['source']} · relevance {h['score']:.0%}")
            with st.expander("View source passage"):
                st.write(h["text"])


def render_message(i, m):
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if m["role"] != "assistant":
            return
        if m.get("error"):
            with st.expander("Technical details"):
                st.code(m["error"], language=None)
            return
        if not m.get("in_scope", True):
            st.markdown('<div class="warn">This may be outside the handbook. You can ask a staff member '
                        'for help.</div>', unsafe_allow_html=True)
            st.button("Get help from staff", key=f"help_{i}", on_click=go, args=("Help & support",))
            return
        render_sources(m.get("sources"), i)
        c1, c2, c3, c4 = st.columns([1, 1, 1, 3])
        if c1.button("🔖 Save", key=f"save_{i}"):
            q = S.messages[i - 1]["content"] if i else ""
            if not any(s["a"] == m["content"] for s in S.saved):
                S.saved.insert(0, {"q": q, "a": m["content"], "sources": m.get("sources", [])})
            st.toast("Saved to History & saved")
        if c2.button("👍", key=f"up_{i}"):
            S.feedback[i] = "up"; st.toast("Thanks for the feedback")
        if c3.button("👎", key=f"down_{i}"):
            S.feedback[i] = "down"; st.toast("Thanks, we'll use this to improve")
        with st.expander("Copy answer"):
            st.code(m["content"], language=None)


def answer_pending():
    q = S.messages[-1]["content"]
    history = [{"role": m["role"], "content": m["content"]} for m in S.messages[:-1]]
    with st.chat_message("assistant"):
        try:
            with st.spinner("Searching the handbook..."):
                res = rag.answer(q, history, store, k=k, min_score=min_score, followups=smart_fu)
            srcs = [{"source": h.source, "page": h.page, "score": h.score,
                     "text": h.text, "section": h.section} for h in res["sources"]]
            S.messages.append({"role": "assistant", "content": res["answer"],
                               "sources": srcs, "in_scope": res["in_scope"],
                               "followups": res.get("followups", [])})
        except Exception as e:
            msg = str(e).lower()
            if any(s in msg for s in ("not found", "404", "no longer available", "deprecated")):
                text = ("The configured Gemini model is not available. Set GEMINI_MODEL to a current model "
                        "(run `python scripts/check_setup.py` to list them).")
            elif any(s in msg for s in ("api key", "api_key", "permission", "403", "401", "invalid")) \
                    and "gemini_api_key" not in msg:
                text = "The Gemini API key was rejected. Check that GEMINI_API_KEY is correct."
            elif any(s in msg for s in ("rate", "429", "quota", "exhausted")):
                text = "The free-tier API limit was reached. Please wait a minute and try again."
            elif "gemini_api_key" in msg:
                text = "The app is missing its API key. Please contact the maintainer."
            else:
                text = "Something went wrong while answering. Please try again."
            S.messages.append({"role": "assistant", "content": text, "sources": [], "in_scope": True,
                               "error": f"{type(e).__name__}: {e}"[:600]})
    S.needs_answer = False
    st.rerun()


# -------------------------------------------------------------------- pages
if S.page == "Home":
    st.markdown('<div class="hero"><h1>Hello, student! How can I help you today?</h1>'
                '<p>Ask in your own words. Every answer cites the handbook passage it came from.</p></div>',
                unsafe_allow_html=True)
    with st.form("home_ask", clear_on_submit=True):
        c1, c2 = st.columns([6, 1])
        q = c1.text_input("Ask", label_visibility="collapsed",
                          placeholder="Ask anything about your student handbook...")
        if c2.form_submit_button("Ask", type="primary", use_container_width=True) and q.strip():
            ask(q.strip())
            st.rerun()
    st.markdown("#### Suggested questions")
    for row in range(0, len(CATEGORIES), 3):
        cols = st.columns(3)
        for col, (cat, q) in zip(cols, CATEGORIES[row:row + 3]):
            with col, st.container(border=True):
                st.markdown(f'<div class="cat">{cat}</div>', unsafe_allow_html=True)
                st.button(q, key=f"cat_{cat}", on_click=ask, args=(q,), use_container_width=True)
    st.markdown("#### Recent conversations")
    if S.conversations:
        for j, cv in enumerate(S.conversations[:3]):
            st.button(f"💬 {cv['title']}", key=f"rc_{j}", use_container_width=True,
                      on_click=lambda c=cv: (archive_current(), S.__setitem__("messages", c["messages"]),
                                             go("Ask the handbook")))
    else:
        st.caption("No conversations yet. Ask your first question above.")
    st.markdown('<div class="note">Answers are based on the official handbook sources available in this app. '
                'Always confirm important decisions with the college offices.</div>', unsafe_allow_html=True)

elif S.page == "Ask the handbook":
    st.subheader("Ask the handbook")
    if not S.messages:
        st.info("Ask a question below, or pick one on the Home page.")
    for i, m in enumerate(S.messages):
        render_message(i, m)
    if S.needs_answer:
        answer_pending()
    elif S.messages and S.messages[-1]["role"] == "assistant" and S.messages[-1].get("in_scope", True):
        fus = S.messages[-1].get("followups") or FOLLOW_UPS
        cols = st.columns(len(fus) + 1)
        for col, f in zip(cols, fus):
            col.button(f, key=f"fu_{len(S.messages)}_{f}", on_click=ask, args=(f,))
    if prompt := st.chat_input("Ask a follow-up or a new question..."):
        ask(prompt)
        st.rerun()

elif S.page == "History & saved":
    st.subheader("History & saved answers")
    tab1, tab2 = st.tabs(["Conversations", "Saved answers"])
    with tab1:
        term = st.text_input("Search conversations", placeholder="Search…", label_visibility="collapsed")
        items = [c for c in S.conversations if term.lower() in c["title"].lower()]
        if not items:
            st.info("No conversations yet. They appear here after you start a new chat.")
        for j, cv in enumerate(items):
            c1, c2 = st.columns([5, 1])
            c1.markdown(f"**{cv['title']}**  \n{len(cv['messages'])} messages")
            c2.button("Reopen", key=f"reopen_{j}", on_click=lambda c=cv: (
                archive_current(), S.__setitem__("messages", c["messages"]), go("Ask the handbook")))
    with tab2:
        if not S.saved:
            st.info("Nothing saved yet. Tap Save on any answer to keep it here.")
        for j, sv in enumerate(S.saved):
            with st.container(border=True):
                st.markdown(f"**{sv['q']}**")
                st.write(sv["a"])
                render_sources(sv["sources"], f"sv{j}")
                if st.button("Remove", key=f"rm_{j}"):
                    S.saved.pop(j)
                    st.rerun()
    st.caption("History and saved answers last for this browser session only.")

else:  # Help & support
    st.subheader("Help & student support")
    st.markdown("#### Frequently asked questions")
    for q, a in [
        ("How do I know an answer is reliable?",
         "Every answer lists the handbook passages it used. Open a source to read the original text."),
        ("What if the assistant can't find my answer?",
         "It will say so rather than guess. Contact the offices below for a confirmed answer."),
        ("Does the assistant replace the handbook?",
         "No. It helps you find information faster. The printed handbook and the college offices are the final authority."),
    ]:
        with st.expander(q):
            st.write(a)
    st.markdown("#### Who to contact")
    with st.container(border=True):
        st.markdown("**Office of Student Affairs and Services**  \nSan Isidro, Talibon, Bohol, Philippines  \n"
                    "📧 talibonpolytechniccollegetalib@gmail.com  \n📞 +63 953 672 9213")
        st.caption("Contact details taken from the Data Privacy section of the TPC Student Handbook.")
    with st.container(border=True):
        st.markdown("**When the assistant can't answer confidently**  \nIt will tell you and point you here. "
                    "Policies can have exceptions that only staff can confirm. For records and enrollment, "
                    "ask the Registrar's Office; for personal concerns, visit the Guidance and Counseling Center.")
