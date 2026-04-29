import os
import json
import re
import streamlit as st
from google import genai

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Proposal Generator",
    page_icon="🏗️",
    layout="wide",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');
    html, body, [class*="css"] { font-family: 'DM Mono', monospace; }
    h1, h2, h3, h4 { font-family: 'Syne', sans-serif !important; }
    .stApp { background: #0d0d0d; color: #e8e0d0; }
    .main-header { padding: 2.5rem 0 1.5rem 0; border-bottom: 1px solid #2a2a2a; margin-bottom: 2rem; }
    .main-title { font-family: 'Syne', sans-serif; font-size: 2.8rem; font-weight: 800; color: #f0e6c8; letter-spacing: -1px; margin: 0; }
    .main-subtitle { font-family: 'DM Mono', monospace; font-size: 0.78rem; color: #5a5a5a; letter-spacing: 3px; text-transform: uppercase; margin-top: 0.4rem; }
    .section-label { font-family: 'DM Mono', monospace; font-size: 0.7rem; color: #c8a96e; letter-spacing: 3px; text-transform: uppercase; margin-bottom: 0.8rem; border-left: 2px solid #c8a96e; padding-left: 0.6rem; }
    .data-card { background: #161616; border: 1px solid #2a2a2a; border-radius: 4px; padding: 1.4rem; margin-bottom: 1rem; }
    .estimate-row { display: flex; justify-content: space-between; align-items: center; padding: 0.6rem 0; border-bottom: 1px solid #1e1e1e; font-size: 0.88rem; }
    .estimate-row:last-child { border-bottom: none; }
    .estimate-label { color: #8a8a8a; }
    .estimate-value { color: #e8e0d0; font-weight: 500; }
    .estimate-total { display: flex; justify-content: space-between; align-items: center; padding: 1rem 0 0 0; margin-top: 0.5rem; border-top: 1px solid #c8a96e; }
    .estimate-total-label { font-family: 'Syne', sans-serif; font-size: 1rem; font-weight: 700; color: #c8a96e; text-transform: uppercase; letter-spacing: 2px; }
    .estimate-total-value { font-family: 'Syne', sans-serif; font-size: 1.5rem; font-weight: 800; color: #c8a96e; }
    .proposal-box { background: #111; border: 1px solid #2a2a2a; border-left: 3px solid #c8a96e; border-radius: 4px; padding: 1.8rem; font-family: 'DM Mono', monospace; font-size: 0.85rem; line-height: 1.9; color: #d0c8b8; white-space: pre-wrap; }
    .stTextArea textarea { background: #161616 !important; border: 1px solid #2a2a2a !important; color: #e8e0d0 !important; font-family: 'DM Mono', monospace !important; font-size: 0.88rem !important; border-radius: 4px !important; }
    .stTextArea textarea:focus { border-color: #c8a96e !important; box-shadow: 0 0 0 1px #c8a96e22 !important; }
    .stNumberInput input { background: #161616 !important; border: 1px solid #2a2a2a !important; color: #e8e0d0 !important; font-family: 'DM Mono', monospace !important; border-radius: 4px !important; }
    .stButton > button { background: #c8a96e !important; color: #0d0d0d !important; border: none !important; font-family: 'Syne', sans-serif !important; font-weight: 700 !important; font-size: 0.82rem !important; letter-spacing: 2px !important; text-transform: uppercase !important; border-radius: 3px !important; padding: 0.6rem 1.8rem !important; }
    .stButton > button:hover { background: #d4b97e !important; }
    hr { border-color: #1e1e1e !important; }
</style>
""", unsafe_allow_html=True)

# ─── Gemini Client Setup ──────────────────────────────────────────────────────
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyATnodZTie9J1JMQgn6UVA_oSUvEpJN0aw")
client = None

if GEMINI_API_KEY:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        st.error(f"Failed to initialise Gemini client: {e}")

GEMINI_MODEL = "models/gemini-2.5-flash"
FALLBACK_MODEL = "gemini-1.5-pro"



# ─── Helper: Safe JSON extraction ────────────────────────────────────────────
def extract_json_safely(raw_text: str):
    """Strip markdown fences, find first { ... } block, parse JSON safely."""
    if not raw_text:
        return None
    # Remove ```json or ``` fences
    text = re.sub(r"```(?:json)?", "", raw_text).strip()
    # Extract between first { and last }
    start = text.find("{")
    end   = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None

import time

def call_gemini(prompt, temperature=0.1):

    models = [
        "models/gemini-2.5-flash",
        "models/gemini-2.0-flash",
        "models/gemini-flash-latest"
    ]

    for attempt in range(3):

        for model_name in models:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config={"temperature": temperature},
                )

                if response and response.text:
                    return response.text

            except Exception as e:
                error_str = str(e)

                # 🔥 HANDLE 503 (busy)
                if "503" in error_str:
                    continue

                # 🔥 HANDLE 429 (quota)
                if "429" in error_str:
                    time.sleep(30)
                    continue

                else:
                    raise e

        time.sleep(2)

    return None
# ─── AI: Extract structured project data ─────────────────────────────────────
def extract_project_data(description: str):
    if not client:
        st.error("Gemini client not initialised. Check your GEMINI_API_KEY.")
        return None

    prompt = f"""
You are a construction estimation assistant specialising in epoxy flooring.

Read the project description and extract the fields below.
Return ONLY a valid JSON object — no markdown, no explanation, no extra text.

Fields:
  project_name  (string)
  area_sf       (number – square feet of floor area)
  cove_lf       (number – linear feet of cove base)
  demo_sf       (number – square feet of demo / surface prep)
  system        (string – e.g. "Broadcast Flake", "Metallic", "Solid Color", "Quartz")
  texture       (string – e.g. "High-Gloss", "Matte", "Anti-Slip")

Defaults if unknown: area_sf=0, cove_lf=0, demo_sf=0, system="Standard Epoxy", texture="High-Gloss"

Project Description:
{description}
"""

    try:
        raw = call_gemini(prompt, temperature=0.1)

        if not raw:
            st.error("No response from Gemini after retries.")
            return None

        parsed = extract_json_safely(raw)

        if parsed is None:
            st.error("Could not parse Gemini response as JSON.\n\nRaw output:\n" + raw)

        return parsed

    except Exception as e:
        st.error(f"Gemini API error (extraction): {e}")
        return None


# ─── Estimate Logic (pure Python, no AI) ─────────────────────────────────────
def calculate_estimate(area_sf: float, cove_lf: float, demo_sf: float) -> dict:
    material = area_sf * 5
    cove     = cove_lf * 2
    demo     = demo_sf * 1
    total    = material + cove + demo
    return {"material_cost": material, "cove_cost": cove, "demo_cost": demo, "total": total}


# ─── AI: Generate proposal ───────────────────────────────────────────────────
def generate_proposal(data: dict, estimate: dict):
    if not client:
        st.error("Gemini client not initialised. Check your GEMINI_API_KEY.")
        return None

    prompt = f"""
You are a professional epoxy flooring contractor writing a client-facing proposal.
Generate a polished, professional proposal using the details below.
Use plain-text UPPERCASE section headers (no markdown symbols like # or *).
Include all six sections, separated by blank lines.

Sections:
  1. PROJECT OVERVIEW
  2. SCOPE OF WORK
  3. PROJECT SCHEDULE
  4. EXCLUSIONS
  5. PRICING BREAKDOWN
  6. TERMS & CONDITIONS

Project Details:
  Name        : {data.get('project_name') or 'N/A'}
  System      : {data.get('system') or 'N/A'}
  Texture     : {data.get('texture') or 'N/A'}
  Floor Area  : {float(data.get('area_sf') or 0):,.0f} sq ft
  Cove Base   : {float(data.get('cove_lf') or 0):,.0f} ln ft
  Demo / Prep : {float(data.get('demo_sf') or 0):,.0f} sq ft

Pricing:
  Material Cost : ${estimate.get('material_cost', 0):,.2f}
  Cove Cost     : ${estimate.get('cove_cost', 0):,.2f}
  Demo / Prep   : ${estimate.get('demo_cost', 0):,.2f}
  TOTAL         : ${estimate.get('total', 0):,.2f}

Professional tone. Plain text only. No markdown.
"""

    try:
        result = call_gemini(prompt, temperature=0.4)

        if not result:
            st.error("No response from Gemini after retries.")
            return None

        return result

    except Exception as e:
        st.error(f"Gemini API error (proposal): {e}")
        return None


# ─── Session State Initialisation ────────────────────────────────────────────
for k, v in {
    "extracted_data": None,
    "estimate":       None,
    "proposal":       None,
    "area_sf":        0.0,
    "cove_lf":        0.0,
    "demo_sf":        0.0,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
  <div class="main-title">🏗️ AI Proposal Generator</div>
  <div class="main-subtitle">Epoxy Flooring · Estimation & Proposal Suite · Powered by Gemini</div>
</div>
""", unsafe_allow_html=True)

if not GEMINI_API_KEY:
    st.warning("⚠️  Set the `GEMINI_API_KEY` environment variable to enable AI features.")


# ════════════════════════════════════════════════════════════════════════════
# STEP 1 — Project Description
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-label">Step 01 — Project Description</div>', unsafe_allow_html=True)

description = st.text_area(
    label="Project Description",
    placeholder=(
        "e.g. We need a broadcast flake epoxy system for a 2,500 sq ft commercial "
        "garage. There's roughly 120 linear feet of cove base required, and we'll "
        "need to demo and prep about 800 sq ft of the existing concrete. "
        "Client prefers a high-gloss finish."
    ),
    height=150,
    label_visibility="collapsed",
)

col_btn1, _ = st.columns([1, 4])
with col_btn1:
    clicked_estimate = st.button("⚡ Generate Estimate", use_container_width=True)

if clicked_estimate:
    if not description.strip():
        st.error("Please enter a project description before generating an estimate.")
    else:
        with st.spinner("Extracting project data with Gemini…"):
            extracted = extract_project_data(description)

        if extracted is not None:
            st.session_state.extracted_data = extracted
            st.session_state.area_sf = float(extracted.get("area_sf") or 0)
            st.session_state.cove_lf = float(extracted.get("cove_lf") or 0)
            st.session_state.demo_sf = float(extracted.get("demo_sf") or 0)
            st.session_state.estimate = calculate_estimate(
                st.session_state.area_sf,
                st.session_state.cove_lf,
                st.session_state.demo_sf,
            )
            st.session_state.proposal = None
            st.success("✅ Project data extracted successfully.")


# ════════════════════════════════════════════════════════════════════════════
# STEP 2 & 3 — Extracted Data + Editable Estimate
# ════════════════════════════════════════════════════════════════════════════
if st.session_state.extracted_data:
    st.markdown("---")
    data = st.session_state.extracted_data
    left_col, right_col = st.columns([1, 1], gap="large")

    with left_col:
        st.markdown('<div class="section-label">Step 02 — Extracted Data</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="data-card">
          <div class="estimate-row"><span class="estimate-label">Project Name</span><span class="estimate-value">{data.get('project_name') or '—'}</span></div>
          <div class="estimate-row"><span class="estimate-label">System</span><span class="estimate-value">{data.get('system') or '—'}</span></div>
          <div class="estimate-row"><span class="estimate-label">Texture</span><span class="estimate-value">{data.get('texture') or '—'}</span></div>
          <div class="estimate-row"><span class="estimate-label">Floor Area</span><span class="estimate-value">{float(data.get('area_sf') or 0):,.0f} sq ft</span></div>
          <div class="estimate-row"><span class="estimate-label">Cove Base</span><span class="estimate-value">{float(data.get('cove_lf') or 0):,.0f} ln ft</span></div>
          <div class="estimate-row"><span class="estimate-label">Demo / Prep</span><span class="estimate-value">{float(data.get('demo_sf') or 0):,.0f} sq ft</span></div>
        </div>
        """, unsafe_allow_html=True)

    with right_col:
        st.markdown('<div class="section-label">Step 03 — Edit Values & Estimate</div>', unsafe_allow_html=True)

        new_area = st.number_input("Area (sq ft)",        min_value=0.0, value=st.session_state.area_sf, step=10.0, format="%.0f")
        new_cove = st.number_input("Cove Base (ln ft)",   min_value=0.0, value=st.session_state.cove_lf, step=5.0,  format="%.0f")
        new_demo = st.number_input("Demo / Prep (sq ft)", min_value=0.0, value=st.session_state.demo_sf, step=10.0, format="%.0f")

        # Live recalculation when values change
        if (new_area != st.session_state.area_sf or
            new_cove != st.session_state.cove_lf or
            new_demo != st.session_state.demo_sf):
            st.session_state.area_sf = new_area
            st.session_state.cove_lf = new_cove
            st.session_state.demo_sf = new_demo
            st.session_state.estimate = calculate_estimate(new_area, new_cove, new_demo)
            st.session_state.proposal = None  # reset so user re-generates

        est = st.session_state.estimate
        st.markdown(f"""
        <div class="data-card" style="margin-top:1rem;">
          <div class="estimate-row">
            <span class="estimate-label">Material Cost ({new_area:,.0f} sf × $5)</span>
            <span class="estimate-value">${est['material_cost']:,.2f}</span>
          </div>
          <div class="estimate-row">
            <span class="estimate-label">Cove Cost ({new_cove:,.0f} lf × $2)</span>
            <span class="estimate-value">${est['cove_cost']:,.2f}</span>
          </div>
          <div class="estimate-row">
            <span class="estimate-label">Demo Cost ({new_demo:,.0f} sf × $1)</span>
            <span class="estimate-value">${est['demo_cost']:,.2f}</span>
          </div>
          <div class="estimate-total">
            <span class="estimate-total-label">Total Estimate</span>
            <span class="estimate-total-value">${est['total']:,.2f}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# STEP 4 — Generate Proposal
# ════════════════════════════════════════════════════════════════════════════
if st.session_state.estimate is not None:
    st.markdown("---")
    st.markdown('<div class="section-label">Step 04 — Proposal</div>', unsafe_allow_html=True)

    col_btn2, _ = st.columns([1, 4])
    with col_btn2:
        clicked_proposal = st.button("📄 Generate Proposal", use_container_width=True)

    if clicked_proposal:
        merged_data = {**(st.session_state.extracted_data or {})}
        merged_data["area_sf"] = st.session_state.area_sf
        merged_data["cove_lf"] = st.session_state.cove_lf
        merged_data["demo_sf"] = st.session_state.demo_sf

        with st.spinner("Drafting your proposal with Gemini…"):
            proposal_text = generate_proposal(merged_data, st.session_state.estimate)

        if proposal_text:
            st.session_state.proposal = proposal_text
            st.success("✅ Proposal generated successfully.")
        else:
            st.error("Proposal generation returned an empty response. Please try again.")

    if st.session_state.proposal:
        st.markdown(
            f'<div class="proposal-box">{st.session_state.proposal}</div>',
            unsafe_allow_html=True,
        )

        # Safe filename — strip special chars
        raw_name  = (st.session_state.extracted_data or {}).get("project_name") or "proposal"
        safe_name = re.sub(r"[^\w\s-]", "", raw_name).strip().replace(" ", "_") or "proposal"

        st.download_button(
            label="⬇ Download Proposal (.txt)",
            data=st.session_state.proposal,
            file_name=f"{safe_name}_proposal.txt",
            mime="text/plain",
        )