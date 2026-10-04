<div align="center">

# 🔬 Fieldnote

### Turn research papers into clear, shareable science content.

**Read the paper. Understand the research. Create the draft. Stay in control.**

Fieldnote is a scientific-content studio that takes research papers and helps turn them into clear, editable content for social media — while keeping the final review and publishing decision with the user.

<br>

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Vercel](https://img.shields.io/badge/Vercel-Serverless-000000?style=for-the-badge&logo=vercel&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-API-F55036?style=for-the-badge)
![CrewAI](https://img.shields.io/badge/CrewAI-Agents-000000?style=for-the-badge)
![Streamlit](https://img.shields.io/badge/Streamlit-Local_App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)

</div>

---

## ✦ What is Fieldnote?

Research papers contain a lot of useful information, but turning that information into something people can actually read and understand is another problem.

**Fieldnote handles that first step.**

Upload a research PDF, tell Fieldnote what you want to focus on, and it creates a research-based draft that you can review and edit before sharing.

```text
                 ┌──────────────────┐
                 │   Research Paper  │
                 │       PDF         │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │  Extract & Read  │
                 │      Paper       │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ Research Analysis│
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │  Content Draft   │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │  Human Review    │
                 │   & Editing      │
                 └────────┬─────────┘
                          │
                          ▼
                    Share if ready
```

The goal isn't to replace the paper.

It's to make the **paper → explanation → communication** process easier.

---

## ⚡ What You Can Do

| | Feature |
|---|---|
| 📄 | Upload one or more research PDFs |
| 🎯 | Give a topic, question, or focus |
| 🧠 | Generate a research-focused analysis |
| ✍️ | Turn the analysis into readable content |
| 📝 | Edit the generated draft |
| 𝕏 | Prepare a shorter X post |
| 🔔 | Save a browser reminder |
| 👤 | Review everything before publishing |

There is **no automatic publishing**.

Fieldnote prepares the content. **You decide what gets shared.**

---

# 🖥️ The Web App

<div align="center">

### Upload → Generate → Edit → Share

</div>

**Add your actual application screenshot below.**

> 📸 **SCREENSHOT — Add your Fieldnote UI screenshot here**

For GitHub, upload your screenshot to:

```text
docs/images/fieldnote-ui.png
```

Then replace the placeholder above with:

```markdown
<div align="center">
<img src="docs/images/fieldnote-ui.png" width="900">
</div>
```

---

# 🔄 How Fieldnote Works

The hosted application has a simple pipeline.

```text
┌─────────────────────────────────────────────────────────────┐
│                         USER                                │
│                                                             │
│       Upload PDF + Enter topic / research focus             │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                      BROWSER APP                            │
│                   HTML / CSS / JavaScript                   │
│                                                             │
│              PDF size validation ≤ 4 MB                     │
└────────────────────────────┬────────────────────────────────┘
                             │
                             │ POST /api/generate
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    VERCEL PYTHON API                        │
│                                                             │
│                    api/generate.py                           │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                          pypdf                               │
│                                                             │
│                 Extract text from PDFs                      │
│                 Maximum 5,000 chars / PDF                   │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                       GROQ API                              │
│                                                             │
│                    gpt-oss-20b                              │
│                                                             │
│                 Research Analysis                           │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                       GROQ API                              │
│                                                             │
│                    gpt-oss-20b                              │
│                                                             │
│                  Content Generation                         │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                      FIELDNOTE UI                           │
│                                                             │
│          Edit Draft → Edit X Post → Review                  │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
                      USER DECIDES
                    WHETHER TO SHARE
```

---

# 🧩 Architecture

<div align="center">

### Fieldnote Web Architecture

</div>

```text
                         FIELDNOTE
                             │
                             │
                ┌────────────┴────────────┐
                │                         │
                ▼                         ▼
          WEB APPLICATION          LOCAL APPLICATION
                │                         │
                │                         │
       HTML / CSS / JS              Streamlit
                │                         │
                ▼                         ▼
        Vercel Python API              CrewAI
                │                         │
                ▼                         ▼
              pypdf                 Research Agent
                │                         │
                │                         ▼
                │                  Content Agent
                │                         │
                └────────────┬────────────┘
                             │
                             ▼
                         GROQ API
                             │
                             ▼
                     gpt-oss-20b
```

---

## 🧠 Why Two AI Steps?

Fieldnote doesn't directly throw the PDF at the model and ask:

```text
"Write a social media post."
```

Instead, the hosted version separates the process into two steps.

### Step 1 — Research

The first model call looks at the extracted research text and the user's focus.

Its job is to understand the supplied research and identify the information that matters.

```text
PDF
 ↓
Extracted Text
 ↓
Research Analysis
```

### Step 2 — Content

The second model call takes that research analysis and turns it into a readable content draft.

```text
Research Analysis
       ↓
Content Generation
       ↓
Editable Draft
```

This keeps the research-reading step separate from the writing step.

---

# 🛠️ Tech Stack

<div align="center">

### Built with a lightweight web stack + AI workflow

</div>

```text
┌───────────────────────────────────────────────────────────┐
│                       FIELDNOTE                           │
├───────────────────────────────────────────────────────────┤
│                                                           │
│  FRONTEND              BACKEND             AI             │
│                                                           │
│  HTML                  Python              Groq           │
│  CSS                   Vercel              gpt-oss-20b    │
│  JavaScript            pypdf                              │
│                                                           │
├───────────────────────────────────────────────────────────┤
│                                                           │
│  LOCAL VERSION                                           │
│                                                           │
│  Streamlit  +  CrewAI  +  Groq                           │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

### Technologies

| Technology | Role |
|---|---|
| **HTML** | Web application structure |
| **CSS** | UI design and layout |
| **JavaScript** | Browser logic and interactions |
| **Python** | Hosted API |
| **Vercel** | Web/API deployment |
| **pypdf** | PDF text extraction |
| **Groq API** | LLM inference |
| **gpt-oss-20b** | Research and content generation |
| **Streamlit** | Local application |
| **CrewAI** | Local agent workflow |
| **localStorage** | Browser reminders |

---

# 🖼️ Project Screenshots

Instead of adding images that may break because of incorrect paths, keep your screenshots in the repository:

```text
docs/
└── images/
    ├── fieldnote-ui.png
    ├── generated-content.png
    ├── x-post.png
    ├── workflow.png
    └── tech-stack.png
```

Then add them like this:

### Main Interface

<div align="center">

<img src="docs/images/fieldnote-ui.png" width="900">

</div>

### Generated Content

<div align="center">

<img src="docs/images/generated-content.png" width="900">

</div>

### X Post

<div align="center">

<img src="docs/images/x-post.png" width="700">

</div>

### Workflow

<div align="center">

<img src="docs/images/workflow.png" width="900">

</div>

### Tech Stack

<div align="center">

<img src="docs/images/tech-stack.png" width="900">

</div>

---

# 🌐 Hosted Version

The web version is designed to run on **Vercel**.

```text
GitHub
   │
   ▼
 Vercel
   │
   ├───────────────┐
   │               │
   ▼               ▼
Frontend       Python API
                   │
                   ▼
                 pypdf
                   │
                   ▼
                Groq API
```

### Environment Variables

The application expects:

```env
GROQ_API_KEY=your_groq_api_key
APP_PASSWORD=your_application_password
```

Keep both values private.

The Groq key should remain on the server and should not be exposed in browser JavaScript.

---

# 🚀 Run Locally

The repository also contains the original Streamlit/CrewAI version.

### Requirements

- Python 3.12
- Groq API key

### Setup

```powershell
git clone <YOUR_REPOSITORY_URL>

cd <YOUR_REPOSITORY_FOLDER>

python -m venv .venv

.venv\Scripts\Activate.ps1

pip install -r requirements-streamlit.txt
```

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key
```

Then run:

```powershell
streamlit run streamlit_app.py
```

---

# 🤖 Local CrewAI Workflow

The Streamlit application follows a slightly different architecture from the hosted web app.

```text
                  RESEARCH PDF
                       │
                       ▼
                Extract PDF Text
                       │
                       ▼
              ┌─────────────────┐
              │ Research Agent  │
              │                 │
              │ Understand the  │
              │ supplied paper  │
              └────────┬────────┘
                       │
                       │ Research output
                       ▼
              ┌─────────────────┐
              │ Content Agent   │
              │                 │
              │ Turn research   │
              │ into content    │
              └────────┬────────┘
                       │
                       ▼
                  FINAL DRAFT
```

The research agent's output becomes context for the content-writing task.

---

# 📅 Reminders & Scheduling

Scheduling in Fieldnote is intentionally simple.

### Web version

The browser version stores reminders using:

```text
localStorage
```

### Streamlit version

The local application stores scheduled information in:

```text
scheduled_posts.json
```

This is **not** a centralized publishing system.

There is currently no:

- Background publishing service
- Cross-device schedule
- Hosted publishing queue
- Automatic X publishing

The user remains responsible for the final post.

---

# 🔐 Human-in-the-Loop

This is an important part of Fieldnote.

```text
              AI
               │
               ▼
          Generate Draft
               │
               ▼
          USER REVIEWS
               │
          ┌────┴────┐
          │         │
        Edit      Reject
          │
          ▼
       Review
          │
          ▼
     Decide to Share
```

The model generates content.

**The user makes the final call.**

This is especially important when working with scientific material, where generated text should be checked against the original paper before being shared.

---

# ⚠️ Current Known Issue

The checked-in hosted API currently contains an authentication issue in `api/generate.py`.

The Groq request currently contains:

```python
"Authorization": "******"
```

instead of using the supplied API key.

It should use the API key as a bearer token:

```python
"Authorization": f"Bearer {api_key}"
```

Until this is corrected, the hosted generation request may fail authentication with Groq.

---

# 📁 Project Structure

```text
Fieldnote/
│
├── api/
│   └── generate.py
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
├── vercel.json
│
└── docs/
    └── images/
        ├── fieldnote-ui.png
        ├── generated-content.png
        ├── x-post.png
        ├── workflow.png
        └── tech-stack.png
```

---

# 📌 Current Limitations

- Maximum **4 MB** total PDF upload in the web application
- Maximum **5,000 characters extracted per PDF**
- Complex PDF layouts may not extract perfectly
- Generated content requires human review
- Dataset upload controls exist in the Streamlit UI, but the current generation flow does not process those datasets
- Image-related CrewAI files exist, but the configured crew currently focuses on research and content tasks
- Scheduling is local/browser-based
- The web version requires the Groq authorization header to be corrected

---

# 🔮 What's Next?

Some possible improvements:

- Better PDF structure extraction
- Tables and figure extraction
- Paper metadata extraction
- Citation-aware generation
- Claim verification
- Section-level paper analysis
- Multiple content styles
- Saved research libraries
- User accounts
- Cloud-based drafts
- Cross-device reminders
- Additional social platforms

---

# 🎯 The Idea Behind Fieldnote

Fieldnote started from a simple problem:

**Research is valuable, but communicating research clearly takes time.**

The project tries to shorten that gap without removing the person responsible for the final message.

```text
Research
   ↓
Understand
   ↓
Draft
   ↓
Review
   ↓
Share
```

The AI helps with the middle.

**The human stays in the loop.**

---

<div align="center">

## 🔬 Fieldnote

**Research → Understanding → Communication**

Made for turning complex research into something people can actually read.

</div>
