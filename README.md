# 🌱 Greenwashing Radar

**Prompt-engineered detection of misleading sustainability claims from product text and packaging images, using the OpenAI API.**

**▶ [Try the live interactive demo](https://viraj-vataria.github.io/Greenwashing-Radar/)** — pick a product, flip the packaging image on and off, and watch the risk score change.

Greenwashing making a product look more environmentally friendly than it really is is hard to catch at scale. Vague phrases like *"eco-friendly"* or *"planet-conscious"*, green colour schemes, and leafy imagery can imply sustainability without any real evidence behind them. Traditional keyword filters miss this because greenwashing lives in *context*, not just words.

**Greenwashing Radar** uses a multimodal Large Language Model to read both the **text** and the **packaging image** of a product, then returns a structured, explainable assessment: what claims were made, how specific they are, and a **greenwashing risk score (0–5)** with a written justification and the exact evidence it relied on.

> Built as the final project for **COM2019 – Programming for Prompt Engineering** (University of Exeter). Awarded **82 / 100 (First class)**.

---

## What it does

For each product, the system produces a structured JSON verdict, for example:

```json
{
  "claim_detected": true,
  "claim_modalities": ["text", "image"],
  "claim_types": ["organic_or_natural", "certification_or_label", "recyclable"],
  "specificity": "mixed",
  "evidence_strength": "moderate",
  "risk_score": 3,
  "risk_label": "medium",
  "evidence": [
    {"modality": "image", "snippet": "Von Natur Aus", "explanation": "Implies natural sourcing but is vague."}
  ],
  "reasoning_summary": "Recognised vegan certification plus vague 'natural' cues; medium risk due to unquantified claims.",
  "needs_human_check": ["Verify scope of the certification label"]
}
```

The design deliberately outputs a **risk indicator, not a verdict of deception** — the model flags where a human should look, rather than accusing a brand.

---

## How it works

The pipeline compares **three methods** on the same products so their behaviour can be measured against each other:

| Method | Description |
|---|---|
| **Heuristic baseline** | Rule/keyword-based detector — a simple, transparent comparison point. |
| **Text-only LLM** | OpenAI model reading only the product description. |
| **Multimodal LLM** | OpenAI model reading the description **and** the packaging image. |

**Key engineering features**
- 📦 **Data collection** from the [Open Food Facts](https://world.openfoodfacts.org) open API, with local caching so runs are reproducible and don't re-hit the API.
- 🖼️ **Text + image pairing** per product for true multimodal prompting.
- 🧾 **Structured JSON outputs** via a fixed schema, so results are machine-readable and comparable.
- 🔁 **Robustness**: retries, error handling, and response caching.
- ⚖️ **LLM-as-judge evaluation** scoring each output for *groundedness*, *conservatism*, and *explanation quality*.
- ✅ **Human gold set**: 24 products hand-annotated to benchmark the models against human judgement.

---

## Results (headline)

- On the 24-item human-annotated set, the LLM judge rated multimodal outputs highly for **conservatism (4.83 / 5)** and **groundedness (4.62 / 5)** — i.e. the model largely avoided over-claiming and stayed tied to visible evidence.
- Adding the **image** changed the risk assessment on a meaningful share of products versus text-only, showing packaging cues carry real signal.
- The simple heuristic was competitive on raw claim *detection*, but the LLMs were far stronger on **specificity** and **explanation** — which is exactly where greenwashing detection actually lives.

> ⚠️ **Honest limitation:** the gold set is small (24 items) and packaging images vary in quality. This is a proof-of-concept, not a production auditing tool. Stronger conclusions would need more products, more annotators, and fuller packaging photos.

Figures in `project_results/figures/` show the risk-score distribution and the judge-score breakdown.

---

## Repo structure

```
Greenwashing_Radar_Final.ipynb     # Main notebook: data -> prompting -> evaluation -> plots
project_data/                      # Sampled products + cached Open Food Facts responses
project_results/                   # Model outputs, comparison tables, case studies, figures
```

---

## Run it yourself

1. Clone the repo and open the notebook (Jupyter / VS Code / Google Colab).
2. Install requirements: `pip install openai pandas matplotlib requests`
3. Add your OpenAI API key where the code reads `API_key_here` (or set the `OPENAI_API_KEY` environment variable). **Never commit your real key.**
4. Run the notebook top to bottom.

---

## Ethics & legal

The project explicitly discusses fairness and bias, data privacy, the UK **Green Claims Code**, Open Food Facts **licensing**, **copyright** of packaging images, model **explainability**, and the need for **human review** — because a tool that labels brands' honesty must be careful, transparent, and never the final word.

---

## Tech

`Python` · `OpenAI API` · `Multimodal prompting` · `Structured JSON outputs` · `Open Food Facts API` · `Prompt engineering` · `LLM-as-a-judge evaluation`

---

*Author: Viraj Vataria*
