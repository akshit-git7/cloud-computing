import json
import mimetypes
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

HOST = "127.0.0.1"
PORT = int(os.environ.get("PORT", 3000))
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.join(ROOT_DIR, "public")


def get_bot_reply(message: str) -> str:
    normalized = message.strip().lower()

    if not normalized:
        return "Say something so I can help you."

    if any(word in normalized for word in ["hi", "hello", "hey", "hola"]):
        return "Hello! I am Nova, your friendly chat bot. How can I help you today?"

    if "your name" in normalized:
        return "I am Nova, a simple chat bot built with Python."

    if "time" in normalized:
        from datetime import datetime
        return f"The current time is {datetime.now().strftime('%I:%M %p')}."

    if "date" in normalized:
        from datetime import datetime
        return f"Today is {datetime.now().strftime('%B %d, %Y')}."

    if "weather" in normalized:
        return "I cannot check live weather right now, but I can help you look up a forecast."

    if "help" in normalized:
        return "You can ask me about greetings, my name, the time, the date, weather, or just say thanks."

    if "thanks" in normalized or "thank you" in normalized:
        return "You are very welcome!"

    return f'You said: "{message}". I am still learning, but I can help with greetings, my name, the time, the date, weather, or general questions.'


class ChatHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/health":
            self.send_json({"status": "ok"})
            return

        if path == "/":
            path = "/index.html"

        safe_path = os.path.normpath(path.lstrip("/"))
        abs_path = os.path.join(PUBLIC_DIR, safe_path)

        if not abs_path.startswith(PUBLIC_DIR):
            self.send_error(HTTPStatus.FORBIDDEN, "Forbidden")
            return

        if os.path.isdir(abs_path):
            abs_path = os.path.join(abs_path, "index.html")

        if os.path.exists(abs_path) and os.path.isfile(abs_path):
            content_type, _ = mimetypes.guess_type(abs_path)
            if not content_type:
                content_type = "application/octet-stream"
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", content_type)
            self.end_headers()
            with open(abs_path, "rb") as fh:
                self.wfile.write(fh.read())
        else:
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/api/chat":
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")
            return

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8")

        try:
            payload = json.loads(body or "{}")
        except json.JSONDecodeError:
            self.send_json({"error": "Invalid JSON payload"}, status=HTTPStatus.BAD_REQUEST)
            return

        reply = get_bot_reply(payload.get("message", ""))
        self.send_json({"reply": reply})

    def send_json(self, payload, status=HTTPStatus.OK):
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format, *args):
        return


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), ChatHandler)
    print(f"Chat bot server running at http://{HOST}:{PORT}")
    server.serve_forever()
