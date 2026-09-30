# Fieldnote Scientific Content Studio

Generate research-based social content from PDFs, edit it, and prepare a post for X. The static web app and lightweight Python generation endpoint are configured for Vercel. `app.py` remains available as the original CrewAI-powered Streamlit interface for local development.

## Deploy to Vercel

1. Import this GitHub repository in Vercel and use the repository root as the project root.
2. Add these environment variables in the Vercel project settings:
   - `GROQ_API_KEY`: an API key from Groq.
   - `APP_PASSWORD`: a long, private password that you choose. The app asks for this password before generating content.
3. Deploy. Vercel serves `index.html` and exposes the generation endpoint at `/api/generate`.

The generation endpoint accepts PDF uploads totaling up to 4 MB and makes two sequential calls to Groq within Vercel's 60-second function limit. The Vercel function calls Groq directly and does not install CrewAI, keeping its deployment bundle small. CrewAI remains a local Streamlit dependency.

Scheduled posts are stored in the current browser's local storage. Reminders appear while the app is open; posts are not sent automatically, and opening the X link still requires human review and confirmation. Queue entries do not sync across browsers or devices.

## Run locally

Install Python 3.12, then install the local app dependencies:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-streamlit.txt
```

Create a `.env` file in the project root with `GROQ_API_KEY` and `APP_PASSWORD`, then run the original Streamlit interface:

```powershell
streamlit run app.py
```

The Vercel-style browser interface can be previewed locally with Vercel CLI (`vercel dev`) after configuring the same environment variables.