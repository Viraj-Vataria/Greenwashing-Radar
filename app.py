"""
Greenwashing Radar — live demo
A small Streamlit app mirroring the COM2019 project pipeline.

It takes product marketing text + a packaging image (URL or upload) and returns
a structured, evidence-linked greenwashing-risk assessment using the OpenAI
Responses API with Structured Outputs.

Cost-safe by design: the demo runs ONLY when a viewer pastes in their own
OpenAI API key, so hosting it publicly never bills you.

Run locally:   pip install streamlit openai   &&   streamlit run app.py
Deploy free:   push to GitHub, then Hugging Face Spaces (SDK: Streamlit)
               or Streamlit Community Cloud.
"""

import base64
import json
import streamlit as st
from openai import OpenAI

# ----------------------------- Page setup ---------------------------------
st.set_page_config(page_title="Greenwashing Radar", page_icon="🌱", layout="centered")
st.title("🌱 Greenwashing Radar")
st.caption(
    "Prompt-engineered, multimodal screening of sustainability claims from "
    "product text + packaging images. Built for COM2019, University of Exeter."
)
st.info(
    "This is a **screening aid**, not a legal verdict. It returns a conservative "
    "risk indicator with visible evidence for human review.",
    icon="ℹ️",
)

# ----------------------------- Sidebar / key ------------------------------
with st.sidebar:
    st.header("Setup")
    api_key = st.text_input(
        "Your OpenAI API key", type="password",
        help="Your key is used only for this request and is never stored.",
    )
    model = st.selectbox("Model", ["gpt-4.1-mini", "gpt-4.1", "gpt-4o"], index=0)
    st.markdown(
        "[Get a key](https://platform.openai.com/api-keys) · "
        "[Project on GitHub](https://github.com/Viraj-Vataria/COM2019-Programming-for-Prompt-Engineering)"
    )

# ----------------------------- Inputs -------------------------------------
product_text = st.text_area(
    "Product description / marketing text",
    height=140,
    placeholder="e.g. Organic almond drink. 100% recyclable carton. Plant-based, "
                "kind to the planet...",
)

col1, col2 = st.tabs(["Image URL", "Upload image"])
with col1:
    image_url = st.text_input("Front-of-pack image URL", placeholder="https://...")
with col2:
    uploaded = st.file_uploader("Packaging image", type=["jpg", "jpeg", "png", "webp"])

# ----------------------------- Prompt (mirrors the notebook) --------------
SYSTEM_PROMPT = (
    "You are a careful sustainability-marketing auditor. Be precise, professional "
    "and skeptical. Only assess what is visible in the text and image. Do NOT invent "
    "labels, certifications or claims, and do NOT accuse firms of deception. Increase "
    "risk only when visible environmental claims are broad, weakly supported or hard "
    "to verify. Treat dietary/health labels (e.g. 'vegan', 'no additives') as "
    "environmental claims only when they clearly signal environmental positioning."
)

USER_INSTRUCTION = (
    "Analyse the product for potential greenwashing risk and return ONLY valid JSON "
    "matching the provided schema. Ground every judgement in visible evidence."
)

SCHEMA = {
    "name": "greenwashing_assessment",
    "strict": True,
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "claim_detected": {"type": "boolean"},
            "claim_types": {"type": "array", "items": {"type": "string"}},
            "specificity": {"type": "string", "enum": ["specific", "mixed", "vague", "none"]},
            "evidence_strength": {"type": "string", "enum": ["strong", "moderate", "weak", "none"]},
            "risk_score": {"type": "integer", "minimum": 0, "maximum": 5},
            "risk_label": {"type": "string", "enum": ["low", "medium", "high"]},
            "evidence": {"type": "array", "items": {"type": "string"}},
            "reasoning_summary": {"type": "string"},
            "needs_human_check": {"type": "boolean"},
        },
        "required": [
            "claim_detected", "claim_types", "specificity", "evidence_strength",
            "risk_score", "risk_label", "evidence", "reasoning_summary", "needs_human_check",
        ],
    },
}


def build_image_part():
    """Return an input_image content block from a URL or an uploaded file."""
    if image_url:
        return {"type": "input_image", "image_url": image_url}
    if uploaded is not None:
        b64 = base64.b64encode(uploaded.getvalue()).decode("utf-8")
        mime = uploaded.type or "image/jpeg"
        return {"type": "input_image", "image_url": f"data:{mime};base64,{b64}"}
    return None


# ----------------------------- Run ----------------------------------------
if st.button("Analyse", type="primary"):
    if not api_key:
        st.error("Please paste your OpenAI API key in the sidebar.")
    elif not product_text.strip():
        st.error("Please add some product text.")
    else:
        user_content = [{"type": "input_text", "text": USER_INSTRUCTION +
                         "\n\nPRODUCT TEXT:\n" + product_text}]
        img = build_image_part()
        if img:
            user_content.append(img)

        try:
            client = OpenAI(api_key=api_key)
            with st.spinner("Assessing claims..."):
                resp = client.responses.create(
                    model=model,
                    temperature=0,
                    input=[
                        {"role": "system", "content": [{"type": "input_text", "text": SYSTEM_PROMPT}]},
                        {"role": "user", "content": user_content},
                    ],
                    text={"format": {"type": "json_schema", **SCHEMA}},
                )
            data = json.loads(resp.output_text)

            # ---- Display ----
            risk = data["risk_score"]
            label = data["risk_label"].upper()
            colour = {"low": "🟢", "medium": "🟡", "high": "🔴"}[data["risk_label"]]
            st.subheader(f"{colour} Risk: {risk}/5 — {label}")

            m1, m2, m3 = st.columns(3)
            m1.metric("Claim detected", "Yes" if data["claim_detected"] else "No")
            m2.metric("Specificity", data["specificity"])
            m3.metric("Evidence", data["evidence_strength"])

            if data["claim_types"]:
                st.write("**Claim types:** " + ", ".join(data["claim_types"]))
            st.write("**Reasoning:** " + data["reasoning_summary"])
            if data["evidence"]:
                st.write("**Visible evidence:**")
                for e in data["evidence"]:
                    st.write(f"- {e}")
            if data["needs_human_check"]:
                st.warning("Flagged for human review.", icon="👀")

            with st.expander("Raw JSON output"):
                st.json(data)

        except Exception as exc:
            st.error(f"API call failed: {exc}")

st.divider()
st.caption(
    "Screening tool for research/education. Not legal advice. Small-sample project — "
    "see GitHub for full methodology, evaluation and limitations."
)
