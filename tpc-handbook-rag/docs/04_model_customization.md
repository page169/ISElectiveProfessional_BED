# Model Customization Note: PEFT / LoRA / QLoRA (Checkpoint 4)

## Decision
I used the **instruction-tuned Gemini model as-is** (no fine-tuning). Instead, I improved the system through retrieval and prompting. No fine-tuning experiment was run.

## Why fine-tuning is not the right first tool here
- **Knowledge changes.** Handbook policies are revised (this is version 4.0 from 2024). Fine-tuning bakes facts into weights; updating needs retraining. RAG only needs `python ingest.py`.
- **Traceability.** Students need page citations. A fine-tuned model cannot point to the source of a fact; RAG can.
- **Hallucination risk.** Fine-tuned models can still state wrong fees or penalties confidently. Retrieval plus a refusal rule is safer for rules and penalties.
- **Cost and hardware.** Gemini is accessed through an API; its weights cannot be fine-tuned this way. Fine-tuning an open model needs a GPU.

## Where PEFT could help
| Goal | Approach |
|---|---|
| Answer style (short, friendly, Taglish/Bisaya replies) | LoRA on an open instruction model (for example Llama 3.1 8B or Qwen2.5 7B) using a few hundred question/answer pairs written from the handbook |
| Better retrieval | Fine-tune the **embedding model** (bge-small is only 33M parameters) with handbook question/passage pairs; cheaper than tuning an LLM |
| Offline or private deployment | Run a quantized open model locally and tune it with QLoRA |

## How LoRA and QLoRA work within memory limits
- **LoRA** freezes the base weights W and learns two small matrices A and B so the update is W + BA, with rank r (for example 8 or 16). Only about 0.1-1% of parameters are trained, so optimizer memory shrinks dramatically.
- **QLoRA** also stores the frozen base weights in 4-bit (NF4 with double quantization) and trains LoRA adapters in 16-bit, with paged optimizers to absorb memory spikes. A 7-8B model that needs about 16 GB in fp16 fits in roughly 5-6 GB of weights plus adapter and activation memory, which fits a free 16 GB Colab or Kaggle GPU.
- **Sketch of a run:** `transformers` + `peft` + `bitsandbytes` + `trl`; `load_in_4bit=True`, LoRA `r=16, alpha=32, dropout=0.05` on attention projection layers; sequence length 1024; batch size 1-2 with gradient accumulation; 1-3 epochs.

## Proposed experiment (future work)
1. Generate about 300 Q&A pairs from handbook chunks and review them by hand.
2. QLoRA-tune a 7-8B open model; compare with the RAG baseline on `scripts/evaluate.py` questions.
3. Keep the tuned model only if it improves correctness **with retrieval still on**.

## Conclusion
For a rule-based, frequently revised document, RAG with a strong instruction model is the better design. PEFT is most valuable for tone, language and domain-tuned embeddings, not for memorising policy text.
