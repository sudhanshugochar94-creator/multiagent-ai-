import hmac
import io
import json
import logging
import os
from email.parser import BytesParser
from email.policy import default
from http.server import BaseHTTPRequestHandler

from dotenv import load_dotenv
from pypdf import PdfReader

load_dotenv()

MAX_REQUEST_BYTES = 4 * 1024 * 1024 + 64 * 1024
MAX_TEXT_PER_PDF = 5000


class handler(BaseHTTPRequestHandler):
    def _respond(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        app_password = os.getenv("APP_PASSWORD")
        if not app_password:
            self._respond(503, {"error": "The app is not configured yet."})
            return

        provided_password = self.headers.get("X-App-Password", "")
        if not hmac.compare_digest(provided_password.encode("utf-8"), app_password.encode("utf-8")):
            self._respond(401, {"error": "Enter the correct app password."})
            return

        if not os.getenv("GROQ_API_KEY"):
            self._respond(503, {"error": "The AI service is not configured yet."})
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

            from crew import research_crew

            result = research_crew.kickoff(
                inputs={"topic": topic, "pdf_text": pdf_text}
            )
            self._respond(200, {"content": result.raw})
        except Exception:
            logging.exception("Content generation failed")
            self._respond(500, {"error": "Content generation failed. Check the deployment logs."})

    def log_message(self, format, *args):
        return