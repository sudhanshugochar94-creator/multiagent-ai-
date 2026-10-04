# Fieldnote

### Turn research papers into clear, shareable science content.

Fieldnote is a small scientific-content studio built to make research papers easier to understand and easier to communicate.

You give it one or more research PDFs and a topic or focus. Fieldnote extracts the relevant text, sends it through a research-first generation process, and produces an editable draft that can be turned into a short social post.

The important part is that **Fieldnote does not publish anything automatically**. The generated content is only a starting point. You review it, edit it, and decide what you want to share.

---

## ✨ What Fieldnote Does

Research papers are often difficult to turn into something that is short, clear, and understandable without losing the important details.

Fieldnote handles that first pass.

**The basic flow is:**

`Research PDF → Extract Text → Research Analysis → Content Draft → Human Review → Share`

You can:

- Upload one or more research PDFs
- Add a topic, question, or writing focus
- Generate a research-based explanation
- Turn the explanation into social-media-friendly content
- Edit the generated draft
- Edit a shorter X/Twitter version
- Save a browser reminder
- Open X with the post already filled in
- Decide yourself whether to publish it

> Fieldnote is designed to assist with scientific communication, not replace reading the original research paper or checking scientific claims.

---

## 📸 Screenshots

### Main Interface

<!-- Replace this path with your actual screenshot -->

![Fieldnote Interface](docs/images/fieldnote-interface.png)

The interface is intentionally simple: upload the paper, provide the focus, generate the draft, then review and edit the result.

---

### Generated Research Content

![Generated Content](docs/images/generated-content.png)

The generated output is editable. Fieldnote does not lock the user into the model's response.

---

### X Post Preview

![X Post Preview](docs/images/x-post-preview.png)

A shorter version can be prepared for X and opened with the content pre-filled.

---

# 🔄 How Fieldnote Works

The hosted version follows a fairly straightforward pipeline.

```text
                    ┌──────────────────────┐
                    │    Research PDFs     │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │     Browser UI       │
                    │   HTML / CSS / JS    │
                    └──────────┬───────────┘
                               │
                         Topic / Focus
                               │
                               ▼
                    ┌──────────────────────┐
                    │    /api/generate     │
                    │    Python / Vercel   │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │       pypdf          │
                    │   Extract PDF text   │
                    └──────────┬───────────┘
                               │
                       Max 5,000 chars
                         per PDF
                               │
                               ▼
                    ┌──────────────────────┐
                    │      Groq API        │
                    │ openai/gpt-oss-20b   │
                    └──────────┬───────────┘
                               │
                      Research Analysis
                               │
                               ▼
                    ┌──────────────────────┐
                    │      Groq API        │
                    │ openai/gpt-oss-20b   │
                    └──────────┬───────────┘
                               │
                       Content Draft
                               │
                               ▼
                    ┌──────────────────────┐
                    │     Browser UI       │
                    │ Edit + Review + X    │
                    └──────────────────────┘
```

### Workflow Diagram

For the repository, I recommend adding your detailed architecture image here:

![Fieldnote Workflow](docs/images/fieldnote-workflow.png)

**Suggested diagram structure:**

```text
USER
 │
 │ Upload PDFs + Topic
 ▼
FIELDNOTE WEB APP
 │
 ▼
PDF VALIDATION
 │
 │ ≤ 4 MB total
 ▼
VERCEL PYTHON API
 │
 ▼
PYPDF
 │
 │ Extract text
 │
 │ ≤ 5,000 chars / PDF
 ▼
RESEARCH ANALYSIS
 │
 │ Groq
 │ openai/gpt-oss-20b
 ▼
CONTENT GENERATION
 │
 │ Groq
 │ openai/gpt-oss-20b
 ▼
EDITABLE DRAFT
 │
 ├───────────────┐
 ▼               ▼
LONG FORM       X POST
 │               │
 ▼               ▼
USER REVIEW     USER REVIEW
 │               │
 └───────┬───────┘
         ▼
      OPEN X
         │
         ▼
   USER DECIDES
   WHETHER TO POST
```

---

# 🧠 Generation Pipeline

Fieldnote intentionally separates **research analysis** from **content writing**.

Instead of directly asking the model:

> "Write a social media post from this paper."

the hosted application uses two generation steps.

### 1. Research Analysis

The extracted paper text and the user's focus are sent to the first model request.

Its job is to identify and understand the relevant information from the supplied research.

The prompt is designed to keep the response grounded in the supplied material rather than encouraging unsupported claims.

### 2. Content Generation

The research analysis is then passed into a second model request.

This step turns the analysis into a readable content draft.

The separation makes the workflow easier to reason about:

```text
PDF
 │
 ▼
Extracted Research
 │
 ▼
Research Analysis
 │
 ▼
Content Draft
```

The generated content is still reviewed by the user before it is shared.

---

# 🛠️ Tech Stack

## Web Application

| Technology | Used For |
|---|---|
| HTML | Application structure |
| CSS | Layout and visual design |
| JavaScript | Browser-side application logic |
| Python | Backend API |
| Vercel | Hosting / serverless API |
| pypdf | PDF text extraction |
| Groq API | LLM inference |
| openai/gpt-oss-20b | Generation model |
| localStorage | Browser-side reminders |

## Local Version

| Technology | Used For |
|---|---|
| Streamlit | Local application UI |
| CrewAI | Agent workflow |
| Python | Application logic |
| Groq | Model access |
| pypdf | PDF processing |
| JSON | Local schedule storage |

---

## ⚙️ Tech Stack Overview

![Fieldnote Tech Stack](docs/images/fieldnote-tech-stack.png)

A simple tech-stack diagram can show:

```text
                 FIELDNOTE
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
     FRONTEND       API         LOCAL APP
        │            │            │
   HTML/CSS/JS    Python      Streamlit
                     │            │
                     │          CrewAI
                     │
                 Vercel
                     │
                     ▼
                 pypdf
                     │
                     ▼
                  Groq API
                     │
                     ▼
             openai/gpt-oss-20b
```

---

# 🌐 Hosted Web App

The main version of Fieldnote is designed to run on Vercel.

### Request flow

```text
Browser
   │
   │ POST /api/generate
   ▼
Python API
   │
   ├── Validate app password
   │
   ├── Validate PDF size
   │
   ├── Extract PDF text
   │
   ├── Limit extracted text
   │
   ├── Call Groq
   │
   └── Return generated content
   │
   ▼
Browser
```

The browser checks that the uploaded PDFs are within the **4 MB total limit** before sending them to the API.

The API extracts a maximum of **5,000 characters from each PDF** for the generation workflow.

---

# 🔐 Environment Variables

The hosted application expects:

```env
GROQ_API_KEY=your_groq_api_key
APP_PASSWORD=your_application_password
```

The Groq API key is intended to remain **server-side**.

Do not put the Groq key directly inside `script.js`, HTML, or other browser-exposed files.

For Vercel, add these values under:

```text
Vercel
  → Project
    → Settings
      → Environment Variables
```

Then redeploy the project.

---

# 🚀 Running the Local Streamlit Version

The repository also contains an older local version based on Streamlit and CrewAI.

Make sure Python 3.12 is installed.

### 1. Clone the repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd <YOUR_REPOSITORY_FOLDER>
```

### 2. Create a virtual environment

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements-streamlit.txt
```

### 4. Create `.env`

Create a `.env` file in the repository root:

```env
GROQ_API_KEY=your_groq_api_key
```

Keep this file private.

### 5. Start Streamlit

```powershell
streamlit run streamlit_app.py
```

The application should then be available through the local Streamlit URL shown in the terminal.

---

# ☁️ Deploying to Vercel

The repository already contains Vercel configuration.

### Deployment flow

```text
GitHub Repository
       │
       ▼
    Vercel
       │
       ├── Build / Deploy
       │
       ▼
Python API
       │
       ▼
    Groq API
```

### Steps

1. Import the repository into Vercel.
2. Use the repository root as the project root.
3. Add:

```text
GROQ_API_KEY
APP_PASSWORD
```

4. Select the environment in which the variables should be available.
5. Deploy.
6. Open the deployed application.
7. Test PDF upload and generation.
8. If generation fails, check the Vercel runtime logs.

> Having Vercel configuration in the repository does not by itself mean that a live deployment exists or is currently working.

---

# ⚠️ Current Hosted API Note

There is currently an important implementation issue in the checked-in `api/generate.py`.

The Groq request currently uses:

```python
"Authorization": "******"
```

instead of passing the API key as a bearer token.

The request should use the supplied API key, for example:

```python
"Authorization": f"Bearer {api_key}"
```

Without the correct authorization header, the hosted API request to Groq is expected to fail authentication.

This should be corrected before relying on the deployed generation workflow.

---

# 🖥️ Project Structure

A simplified view of the repository:

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
        ├── fieldnote-interface.png
        ├── generated-content.png
        ├── x-post-preview.png
        ├── fieldnote-workflow.png
        └── fieldnote-tech-stack.png
```

---

# 🧩 Two Versions, Two Workflows

Fieldnote currently contains two different implementations.

### Web Version

```text
HTML
CSS
JavaScript
   │
   ▼
Vercel Python API
   │
   ▼
pypdf
   │
   ▼
Groq
```

This is the version intended for deployment.

### Streamlit Version

```text
Streamlit
   │
   ▼
PDF Processing
   │
   ▼
CrewAI
   │
   ├── Research Agent
   │
   └── Content Agent
   │
   ▼
Groq
```

The two versions should be considered separate workflows rather than two interfaces for exactly the same backend.

---

# 🤖 Streamlit / CrewAI Workflow

The local application uses a CrewAI-based workflow.

```text
                 PDF
                  │
                  ▼
           Extract PDF Text
                  │
                  ▼
        ┌─────────────────────┐
        │    Research Agent   │
        │                     │
        │ Understand research │
        │ and identify useful │
        │ information         │
        └──────────┬──────────┘
                   │
                   │ Research output
                   ▼
        ┌─────────────────────┐
        │   Content Agent     │
        │                     │
        │ Turn research into  │
        │ readable content    │
        └──────────┬──────────┘
                   │
                   ▼
              Final Draft
```

The research task acts as context for the content-writing task.

---

# 📅 Scheduling

Fieldnote's scheduling feature is intentionally lightweight.

The hosted web application stores reminders in:

```text
Browser localStorage
```

The Streamlit version stores its schedule in:

```text
scheduled_posts.json
```

This means the project does **not** currently provide:

- Cross-device scheduling
- Hosted job execution
- Automatic posting
- A centralized publishing queue
- Background social-media publishing

The reminder is there to help the user remember to review or share content.

---

# 🛡️ Human Review

One of the main design choices in Fieldnote is keeping the user in control.

The workflow is:

```text
AI generates
      ↓
User reads
      ↓
User edits
      ↓
User checks claims
      ↓
User decides whether to publish
```

Fieldnote does not automatically publish the generated content to X.

The X integration simply opens X with the prepared text so the user can make the final decision.

---

# 🎯 Why Fieldnote?

The idea is simple:

**Research should not have to become less useful just because it needs to be communicated simply.**

Fieldnote tries to make the first step from:

```text
Long research paper
        ↓
Understandable explanation
        ↓
Editable social content
```

a little easier.

It is not intended to replace the paper, the researcher, or scientific review.

---

# 🔮 Possible Future Improvements

Some natural next steps for the project could include:

- Better PDF parsing for complex papers
- Section-aware extraction
- Tables and figure extraction
- Citation/reference preservation
- Better claim verification
- Paper metadata extraction
- Multiple writing styles
- Linked citations in generated content
- User accounts
- Cloud-based saved drafts
- Cross-device reminders
- Research-paper libraries
- More social platforms
- Background scheduling
- Improved scientific fact checking

---

# 📌 Current Limitations

A few limitations are intentional or worth knowing:

- PDF uploads are limited to **4 MB total** in the web workflow.
- Text extraction is limited to **5,000 characters per PDF**.
- Complex PDF layouts may not extract perfectly.
- Generated content still requires human review.
- The Streamlit dataset upload controls are present, but the current generation flow does not process those datasets.
- Image-related CrewAI files exist, but the configured crew currently runs the research and content tasks rather than an image-generation task.
- Scheduling is local/browser-based rather than a hosted publishing system.
- The hosted Groq authorization header needs to be corrected before the main generation workflow can work reliably.

---

# 📄 Project Philosophy

Fieldnote is built around a simple idea:

> **Use AI to help communicate research, while keeping the human responsible for the final message.**

The model helps with the transformation.

The user remains responsible for reviewing the science.

---

## Built With

**Frontend**

HTML · CSS · JavaScript

**Backend**

Python · Vercel

**Research Processing**

pypdf

**AI**

Groq · openai/gpt-oss-20b

**Local Workflow**

Streamlit · CrewAI

**Browser Storage**

localStorage

---

## 👨‍💻 Project

Fieldnote is a project focused on making scientific communication more approachable without removing the human from the process.

If you find an issue, have an idea, or want to improve the workflow, feel free to open an issue or contribute to the project.

---

### Fieldnote

**Read the research. Understand it. Edit it. Then decide what to share.**
