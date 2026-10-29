# Project Proposal: Campus Guide AI (TPC Handbook Assistant)
**Course:** IS Professional Elective #4, Generative AI Systems · **Checkpoint 1**

## Problem statement
Students at Talibon Polytechnic College must follow rules on attendance, enrollment, grading, discipline and services that are spread across a 200-page handbook. Finding one rule (for example, how many absences lead to dropping) means scanning long documents, and students often ask the same questions of the offices. A plain chatbot would answer from general knowledge and could invent policies, which is unacceptable for school rules.

## Proposed solution
A Retrieval-Augmented Generation (RAG) assistant that answers only from the official TPC Student Handbook, cites the handbook article and page it used, remembers the conversation, and declines questions the handbook cannot answer.

## Target users
- Incoming and current TPC students (primary)
- Parents and guardians
- Faculty and office staff who answer repeated policy questions

## Theme and dataset
Theme: Document/Knowledge-Base Q&A Assistant.
Dataset: TPC Student Handbook v.04 (BOT Resolution No. 33, s. 2024), about 200 pages covering admissions, academic rules, student services, conduct and discipline, due process, off-campus activities and the curriculum prospectus. This exceeds the minimum of 20-30 pages. The file is stored at `data/handbook/TPC_Student_Handbook.txt`. It is the school's own document, supplied by the project owner.

## Success criteria (measurable)
| # | Criterion | Target |
|---|---|---|
| 1 | In-scope test questions answered correctly and grounded (`scripts/evaluate.py`) | at least 80% |
| 2 | Out-of-scope test questions correctly declined | 100% |
| 3 | Answers show at least one handbook citation with page number | 100% of in-scope answers |
| 4 | Follow-up questions resolved using conversation memory | works on the multi-turn test |
| 5 | Median response time on the deployed app | under 10 seconds |
| 6 | Public app opens with no login and stays online until grades are released | yes |

## Scope and limits
In scope: English-language Q&A over the handbook. Out of scope: other school documents, personal records, legal advice, real-time information such as schedules or announcements.

## Roles
Individual project. The owner is responsible for the data pipeline, embeddings and vector index, RAG orchestration, interface and deployment. (If done in a team, replace this section with each member's component.)

## Technology plan
Python, LangChain, FastEmbed (BAAI/bge-small-en-v1.5), FAISS, Google Gemini, Streamlit, Docker, GitHub Actions.

## Timeline
Prelim: proposal, data, preprocessing, embeddings. Midterm: prompts, API integration, FAISS index, metric comparison. Semi-final: ingestion pipeline, RAG app, memory, demo. Final: interface, Docker, deployment, report, defense.
