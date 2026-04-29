# 🏗️ AI Proposal Generator

**End-to-end tool that turns natural project descriptions into a draft estimate and a client-ready proposal.**

---
## 🌐 Live Demo

https://ai-proposal-tool-j33q5ljjxbx5n3mnvkfpbd.streamlit.app/

## 🚀 Overview

Estimators typically:

1. Gather project details verbally
2. Manually fill an estimate sheet
3. Manually draft a proposal

This tool automates that workflow:

**Natural Input → AI Extraction → Editable Estimate → Proposal Generation**

Built as a lightweight web app using Streamlit and Google Gemini.

---

## ✨ Key Features

* 🎤 **Natural Language Intake**
  Accepts conversational input (simulating verbal intake)

* 🤖 **AI-Powered Data Extraction**
  Extracts structured fields (area, cove, demo, system, texture)

* 📊 **Auto Estimate Generation**
  Deterministic pricing logic (transparent & editable)

* ✏️ **Editable Values**
  Users can adjust quantities before finalizing

* 📄 **Proposal Generation**
  Generates contractor-style proposal aligned with template

* 🔄 **Dynamic Updates**
  Changes in estimate automatically reflect in proposal

* ⚡ **Robust API Handling**
  Retry + fallback logic for Gemini (handles 503/429 errors)

---

## 🧠 System Architecture

```
User Input (Natural Language)
        ↓
Gemini AI → Extract structured data (JSON)
        ↓
Python Logic → Calculate estimate
        ↓
Gemini AI → Generate proposal
        ↓
User Review & Edit
```

---

## 🛠️ Tech Stack

* **Frontend**: Streamlit
* **AI Model**: Gemini (google-genai SDK)
* **Language**: Python

---

## ▶️ How to Run

### 1. Install dependencies

```
pip install -r requirements.txt
```

### 2. Set API Key

```
export GEMINI_API_KEY=your_key_here
```

(Windows)

```
set GEMINI_API_KEY=your_key_here
```

### 3. Run app

```
streamlit run app.py
```

---

## 🧪 Example Input

```
9250 sq ft epoxy flooring, 2300 LF cove, demo 1584 sq ft, broadcast flake system
```

---

## 📌 What’s Automated vs Manual

| Step                 | Automation |
| -------------------- | ---------- |
| Data extraction      | ✅ AI       |
| Estimate calculation | ✅ Code     |
| Proposal generation  | ✅ AI       |
| Final adjustments    | ⚠️ User    |

---

## ⚠️ Limitations

* Uses **simplified pricing model** (for demo clarity)
* Gemini free tier may hit **rate limits (429/503)**
* Voice input simulated via text

---

## 🔮 Future Improvements

* 🎤 Real voice input (speech-to-text)
* 📄 Export proposal as `.docx`
* 📊 Full contractor-grade pricing model (labor, markup, tax)
* 🌐 Deploy as hosted web app

---

## 💡 Key Insight

This project focuses on:

> **Workflow automation, AI integration, and system design — not perfect pricing accuracy**

---

## 👤 Author

**Shreejit Magadum**

---

## 📬 Submission Note

This tool demonstrates:

* Practical use of AI for real workflows
* Clear separation of AI vs deterministic logic
* Functional end-to-end system within limited time

---
