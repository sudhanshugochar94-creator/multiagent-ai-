<div align="center">

# 🔬 Fieldnote

### Turn research papers into clear, shareable science content.

**Read the paper. Understand the research. Create the draft. Stay in control.**

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Vercel](https://img.shields.io/badge/Vercel-Serverless-000000?style=flat-square&logo=vercel&logoColor=white)](https://vercel.com/)
[![Groq](https://img.shields.io/badge/Groq-API-F55036?style=flat-square)](https://groq.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Local_App-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io/)

</div>

---

## About

Fieldnote turns research papers into clear, editable content for social media. Upload a PDF, choose your focus, and let the app analyze the research and create a draft. You can review, edit, and approve everything before sharing.

> **Research → Understand → Create → Review → Share**

---

## ✨ Features

- 📄 Upload research PDFs
- 🎯 Choose a topic or focus
- 🧠 Analyze the research with AI
- ✍️ Generate an editable content draft
- 𝕏 Create a shorter X post
- 🔔 Save a browser reminder
- 👤 Review everything before sharing

**No automatic publishing. You stay in control.**

---

## 🖥️ App Preview

<div align="center">

<img src="docs/images/fieldnote-ui.png" width="850">

</div>

---

## 🔄 Workflow

<div align="center">

<img src="docs/images/workflow.png" width="850">

</div>

### How it works

```text
Research PDF
     ↓
Extract Text
     ↓
Research Analysis
     ↓
Content Generation
     ↓
Editable Draft
     ↓
Human Review
     ↓
Share if Ready
```

The hosted web app uses `pypdf` to extract the research text and sends it through two AI steps: research analysis followed by content generation.

---

## 🧠 AI Pipeline

Fieldnote separates **understanding the research** from **writing the content**.

### 01 — Research Analysis

The first AI request looks at the extracted paper text and the user's focus to identify the important research information.

### 02 — Content Generation

The second request uses that analysis to create a readable, social-media-friendly draft.

```text
PDF
 ↓
Extracted Research
 ↓
Research Analysis
 ↓
Content Draft
 ↓
User Review
```

This helps keep the writing process grounded in the supplied research.

---

## 🛠️ Tech Stack

<div align="center">

<img src="docs/images/tech-stack.png" width="750">

</div>

| Technology | Purpose |
|---|---|
| **HTML / CSS** | Web interface |
| **JavaScript** | Browser-side functionality |
| **Python** | API backend |
| **Vercel** | Hosting |
| **pypdf** | PDF text extraction |
| **Groq API** | AI inference |
| **gpt-oss-20b** | Research & content generation |
| **Streamlit** | Local application |
| **CrewAI** | Local agent workflow |
| **localStorage** | Browser reminders |

---

## 🏗️ Architecture

```text
                         FIELDNOTE
                             │
              ┌──────────────┴──────────────┐
              │                             │
              ▼                             ▼
        WEB APPLICATION              LOCAL APPLICATION
              │                             │
        HTML / CSS / JS                 Streamlit
              │                             │
              ▼                           CrewAI
       Vercel Python API                    │
              │                    ┌────────┴────────┐
              ▼                    ▼                 ▼
            pypdf             Research Agent   Content Agent
              │                    │                 │
              └────────────────────┴────────┬────────┘
                                             │
                                             ▼
                                          Groq API
                                             │
                                             ▼
                                        gpt-oss-20b
```

---

## 🌐 Web App

The main version is designed for Vercel.

```text
Browser
   │
   │ PDF + Topic
   ▼
Vercel Python API
   │
   ▼
pypdf
   │
   ▼
Groq
   │
   ▼
Generated Content
   │
   ▼
Browser
   │
   ▼
Edit → Review → Share
```

The browser validates that uploaded PDFs are within the **4 MB total limit**. The API extracts up to **5,000 characters per PDF** for the generation workflow.

---

## 🤖 Local Streamlit Version

The repository also contains an older local version built with Streamlit and CrewAI.

```text
Research PDF
     ↓
Extract Text
     ↓
Research Agent
     ↓
Content Agent
     ↓
Final Draft
```

The research agent's output is passed as context to the content-writing task.

---

## 🔐 Environment Variables

For the hosted application:

```env
GROQ_API_KEY=your_groq_api_key
APP_PASSWORD=your_application_password
```

For the local Streamlit version:

```env
GROQ_API_KEY=your_groq_api_key
```

Never commit `.env` or expose your API key in frontend code.

---

## 🚀 Run Locally

```powershell
git clone <YOUR_REPOSITORY_URL>
cd <YOUR_REPOSITORY_FOLDER>

python -m venv .venv
.venv\Scripts\Activate.ps1

pip install -r requirements-streamlit.txt

streamlit run streamlit_app.py
```

Python **3.12** is used by the project.

---

## 📁 Project Structure

```text
Fieldnote/
│
├── api/
│   └── generate.py
│
├── docs/
│   └── images/
│       ├── fieldnote-ui.png
│       ├── workflow.png
│       └── tech-stack.png
│
├── index.html
├── styles.css
├── script.js
│
├── streamlit_app.py
├── agents.py
├── tasks.py
├── content_agent.py
├── content_task.py
├── crew.py
│
├── pyproject.toml
├── requirements.txt
├── requirements-streamlit.txt
├── .python-version
└── vercel.json
```

---

## 🔐 Human in the Loop

Fieldnote is designed around one simple principle:

**AI creates the draft. The human makes the final decision.**

```text
AI
 ↓
Draft
 ↓
Review
 ↓
Edit
 ↓
Check
 ↓
Share
```

The app does not automatically publish content to X.

---

## 📅 Reminders

The web version stores reminders in the browser using `localStorage`.

The Streamlit version stores scheduled information in:

```text
scheduled_posts.json
```

These are reminders, not a centralized publishing system.

---

## ⚠️ Current Status

The hosted API currently needs one authentication fix in `api/generate.py`.

The Groq request should use the supplied API key as a bearer token:

```python
"Authorization": f"Bearer {api_key}"
```

Once corrected, the hosted generation workflow can authenticate with Groq normally.

---

## 🔮 Future Improvements

- Better PDF structure extraction
- Tables and figure extraction
- Citation-aware generation
- Claim verification
- Paper metadata extraction
- Saved research libraries
- Cloud-based drafts
- Cross-device reminders
- Additional social platforms

---

<div align="center">

## 🔬 Fieldnote

**Research → Understanding → Communication**

*Making scientific content easier to create, review, and share.*

</div>
