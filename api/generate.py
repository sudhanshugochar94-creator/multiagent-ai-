import hmac
import io
import json
import logging
import os
from pathlib import Path
from email.parser import BytesParser
from email.policy import default
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from dotenv import load_dotenv
from pypdf import PdfReader

load_dotenv()

MAX_REQUEST_BYTES = 4 * 1024 * 1024 + 64 * 1024
MAX_TEXT_PER_PDF = 5000
GROQ_CHAT_COMPLETIONS_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "openai/gpt-oss-20b"
STATIC_FILES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/styles.css": ("styles.css", "text/css; charset=utf-8"),
    "/script.js": ("script.js", "text/javascript; charset=utf-8"),
    "/assets/arctic.jpg": ("assets/arctic.jpg", "image/jpeg"),
}


def _groq_completion(api_key, messages):
    request = Request(
        GROQ_CHAT_COMPLETIONS_URL,
        data=json.dumps({"model": GROQ_MODEL, "messages": messages, "temperature": 0.2}).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urlopen(request, timeout=22) as response:
        payload = json.load(response)

    choices = payload.get("choices", [])
    if not choices:
        raise ValueError("Groq returned no completion choices.")

    content = choices[0].get("message", {}).get("content")
    if not isinstance(content, str) or not content.strip():
        raise ValueError("Groq returned an empty completion.")
    return content.strip()


def _generate_content(api_key, topic, pdf_text):
    research = _groq_completion(
        api_key,
        [
            {
                "role": "system",
                "content": (
                    "You are a scientific research assistant. Analyze only the supplied source. "
                    "Return a concise analysis with Main topic, Key findings (up to 5 bullets), "
                    "and Conclusion. Do not invent facts."
                ),
            },
            {
                "role": "user",
                "content": f"User request:\n{topic}\n\nScientific information:\n{pdf_text}",
            },
        ],
    )
    return _groq_completion(
        api_key,
        [
            {
                "role": "system",
                "content": (
                    "You create accurate scientific social content using only the supplied analysis. "
                    "Return a Hook, Post/Caption, Short description, Hashtags, and References. "
                    "Do not invent facts, numbers, results, or claims. Keep the post suitable for X."
                ),
            },
            {
                "role": "user",
                "content": f"User request:\n{topic}\n\nResearch analysis:\n{research}",
            },
        ],
    )


class handler(BaseHTTPRequestHandler):
    def _respond(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self._respond_body(status, "application/json; charset=utf-8", body)

    def _respond_body(self, status, content_type, body, include_body=True):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        if include_body:
            self.wfile.write(body)

    def _serve_static(self, include_body=True):
        static_file = STATIC_FILES.get(urlsplit(self.path).path)
        if static_file is None:
            self._respond(404, {"error": "Not found."})
            return

        file_path = Path.cwd() / static_file[0]
        try:
            body = file_path.read_bytes()
        except OSError:
            logging.exception("Static asset could not be read: %s", static_file[0])
            self._respond(404, {"error": "Page asset not found."})
            return

        self._respond_body(200, static_file[1], body, include_body)

    def do_GET(self):
        self._serve_static()

    def do_HEAD(self):
        self._serve_static(include_body=False)

    def do_POST(self):
        app_password = os.getenv("APP_PASSWORD")
        if app_password:
            provided_password = self.headers.get("X-App-Password", "")
            if not hmac.compare_digest(provided_password.encode("utf-8"), app_password.encode("utf-8")):
                self._respond(401, {"error": "Enter the correct app password."})
                return

        if not os.getenv("GROQ_API_KEY"):
            self._respond(
                503,
                {"error": "Set GROQ_API_KEY in Vercel project settings, then redeploy."},
            )
            return

        try:
            request_size = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._respond(400, {"error": "Invalid request size."})
            return

        if request_size <= 0 or request_size > MAX_REQUEST_BYTES:
            self._respond(413, {"error": "Upload PDFs totaling less than 4 MB."})
            return

        content_type = self.headers.get("Content-Type", "").encode("ascii", "ignore")
        body = self.rfile.read(request_size)
        message = BytesParser(policy=default).parsebytes(
            b"Content-Type: " + content_type + b"\r\nMIME-Version: 1.0\r\n\r\n" + body
        )

        if not message.is_multipart():
            self._respond(400, {"error": "Send the request as a multipart form."})
            return

        topic = ""
        pdfs = []
        for part in message.iter_parts():
            name = part.get_param("name", header="content-disposition")
            if name == "topic":
                topic = (part.get_payload(decode=True) or b"").decode("utf-8", "replace").strip()
            elif name == "pdfs" and part.get_filename():
                pdfs.append(part.get_payload(decode=True) or b"")

        if not topic:
            self._respond(400, {"error": "Enter a topic or instruction."})
            return
        if not pdfs:
            self._respond(400, {"error": "Upload at least one research PDF."})
            return

        try:
            pdf_text = ""
            for pdf_data in pdfs:
                reader = PdfReader(io.BytesIO(pdf_data))
                text = "\n".join(page.extract_text() or "" for page in reader.pages)
                pdf_text += f"\n\n{text[:MAX_TEXT_PER_PDF]}"

            content = _generate_content(os.environ["GROQ_API_KEY"], topic, pdf_text)
            self._respond(200, {"content": content})
        except Exception:
            logging.exception("Content generation failed")
            self._respond(500, {"error": "Content generation failed. Check the deployment logs."})

    def log_message(self, format, *args):
        return