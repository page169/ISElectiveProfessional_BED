# Preprocessing Report (Checkpoint 1)

Source: `TPC_Student_Handbook.txt` (TPC Student Handbook v.04, plain-text export).

## Pipeline
1. Split the raw text on its printed page headers and recover page numbers.
2. Track the current Article/Chapter heading for each page (section metadata).
3. Clean: remove soft hyphens and carriage returns, decode HTML entities, re-join hyphenated words, collapse whitespace.
4. Chunk with `RecursiveCharacterTextSplitter` (800 characters, 120 overlap).
5. Tokenize (regex word/punctuation tokens shown below; the embedding model uses its own WordPiece tokenizer).

## Dataset statistics
| Measure | Value |
|---|---|
| Pages parsed | 202 |
| Characters before cleaning | 244,151 |
| Characters after cleaning | 237,766 |
| Regex tokens before / after | 46,056 / 44,643 |
| Chunks | 410 |
| Chunk length min / mean / max | 43 / 630 / 800 |

## Before and after examples
### HTML-entity noise (&amp;)
**Before**
```
)
3. (Transferee/s) Transfer of Credentials
(Hon. Dismissal &amp; TOR) (Original)
4. PSA Birth Certificate (Original)
5. Duly accomplished Student’s ID Form
6. 1 Long brown envelope
7. 1 Long white folder
8. 1 pc 2x2 picture (with name & amp;

TPC STUDENT HANDBOOK v.04
47
course indicated at the back)
Step 3. DEAN/PROG
```
**After**
```
)
3. (Transferee/s) Transfer of Credentials
(Hon. Dismissal & TOR) (Original)
4. PSA Birth Certificate (Original)
5. Duly accomplished Student’s ID Form
6. 1 Long brown envelope
7. 1 Long white folder
8. 1 pc 2x2 picture (with name &

TPC STUDENT HANDBOOK v.04
47
course indicated at the back)
Step 3. DEAN/PROG
```

### Hyphenated line breaks
**Before**
```
t through 
College Physician every Tuesday and Thursday, 1:00-
5:00PM.
Section 3. All students who wish to have dental 
consultation shall visit the Health Servies Unit every 
Monday 7:00AM-5:00PM. Students who received dental 
recommendation form the College Dentist will be scheduled 
based on the desired procedure.
S
```
**After**
```
t through 
College Physician every Tuesday and Thursday, 1:00-
5:00PM.
Section 3. All students who wish to have dental 
consultation shall visit the Health Servies Unit every 
Monday 7:00AM-5:00PM. Students who received dental 
recommendation form the College Dentist will be scheduled 
based on the desired procedure.
S
```

### Repeated page header and page number
**Before**
```
TPC STUDENT HANDBOOK v.04
20
spiritual values, develop moral character and 
personal discipline, critical and creative 
thinking;
4. To exert his/her utmost to 
```
**After**
```
(removed; page number stored as metadata -> page=20)
```

## Tokenization example
Sentence: `K. Attendance Section 1. In accordance with the CHED Policy, students  are allowed to be absent from their classes, excu`

Tokens: `['k', '.', 'attendance', 'section', '1', '.', 'in', 'accordance', 'with', 'the', 'ched', 'policy', ',', 'students', 'are', 'allowed', 'to', 'be', 'absent', 'from', 'their', 'classes', ',', 'excu']`

## Reflection: what was messy and how it was handled
- The handbook was exported to plain text, so the original PDF page structure was lost. I rebuilt pages from the repeated `TPC STUDENT HANDBOOK v.04` header and its page number.
- Headers and page numbers repeated on every page and would pollute embeddings. They were stripped and kept only as metadata for citations.
- HTML entities such as `&amp;`, hyphenated line breaks and irregular whitespace were normalised.
- Some pages contain OCR/export artifacts (for example digits embedded inside words on the OJT pages). These are rare and were left as-is rather than risk altering policy text.
- Tables (grading scale, prospectus) flatten into short lines; retrieval still works but table answers are the weakest case. A layout-aware PDF parser would help.
- Section labels come from the nearest Article/Chapter heading and can be off on a page where a new chapter starts partway down.