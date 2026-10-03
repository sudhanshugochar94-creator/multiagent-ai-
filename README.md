# Fieldnote Scientific Content Studio

Generate research-based social content from PDFs, edit it, and prepare a post for X. The static web app and lightweight Python generation endpoint are configured for Vercel. `streamlit_app.py` remains available as the original CrewAI-powered Streamlit interface for local development.

## Deploy to Vercel

1. Import this GitHub repository in Vercel and use the repository root as the project root.
2. Add these environment variables in the Vercel project settings:
   - `OPENAI_API_KEY`: an API key from OpenAI with API access and billing/credits enabled.
3. Deploy. Vercel serves `index.html` at `/` and exposes the generation endpoint at `/api/generate`.

The Vercel generation endpoint uses OpenAI's `gpt-4o-mini` model. Add `OPENAI_API_KEY` under **Project Settings → Environment Variables**, ensure it applies to the deployment environment, and redeploy after adding or changing it. Keep the key server-side; do not put it in browser code or commit it to this repository. For runtime errors, check **Runtime Logs** for the `/api/generate` invocation; build logs only confirm that deployment completed.

The generation endpoint does not use an app password and is publicly callable when the deployment is public. If access should be restricted, enable Vercel Deployment Protection for the project.

The generation endpoint accepts PDF uploads totaling up to 4 MB and makes two sequential calls to OpenAI within Vercel's 60-second function limit. The Vercel function calls OpenAI directly and does not install CrewAI, keeping its deployment bundle small. The original local Streamlit interface remains separate and uses its configured CrewAI provider.

Scheduled posts are stored in the current browser's local storage. Reminders appear while the app is open; posts are not sent automatically, and opening the X link still requires human review and confirmation. Queue entries do not sync across browsers or devices.

## Run locally

Install Python 3.12, then install the local app dependencies:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-streamlit.txt
```

Create a `.env` file in the project root with `GROQ_API_KEY` for the original local Streamlit interface, then run it:

```powershell
streamlit run streamlit_app.py
```

The Vercel-style browser interface can be previewed locally with Vercel CLI (`vercel dev`) after configuring the same environment variables.