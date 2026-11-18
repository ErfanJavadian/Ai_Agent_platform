"""Small standard-library web server for the personal assistant.

Secrets stay server-side. Set AI_AGENT_API_KEY, AI_AGENT_MODEL,
AI_AGENT_PROVIDER=openai_compatible, and APP_ACCESS_PASSWORD.
"""
from __future__ import annotations

import json
import os
import secrets
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from ai_agent_platform.agents.loader import load_agent
from ai_agent_platform.core.models import AgentRequest
from ai_agent_platform.providers.factory import create_provider

ROOT = Path(__file__).resolve().parent
AGENT_PATH = Path(os.environ.get("AI_AGENT_MANIFEST", "examples/agents/erfan_personal_assistant.json"))
MAX_BODY = 16_000
MAX_MESSAGES = 20
MAX_MESSAGE_CHARS = 5_000
WINDOW_SECONDS = 60
MAX_REQUESTS_PER_WINDOW = 12
_access_password = os.environ.get("APP_ACCESS_PASSWORD", "")
if len(_access_password) < 16:
    raise RuntimeError("Set APP_ACCESS_PASSWORD to a random value of at least 16 characters.")
_agent = load_agent(AGENT_PATH)
_provider = create_provider()
_requests: dict[str, list[float]] = {}


class Handler(BaseHTTPRequestHandler):
    server_version = "PersonalAssistant/1.0"

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: int, payload: dict) -> None:
        self._send(status, json.dumps(payload, ensure_ascii=False).encode(), "application/json; charset=utf-8")

    def do_GET(self) -> None:
        if urlparse(self.path).path not in {"/", "/index.html"}:
            self._json(404, {"error": "Not found"})
            return
        self._send(200, (ROOT / "index.html").read_bytes(), "text/html; charset=utf-8")

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/chat":
            self._json(404, {"error": "Not found"})
            return
        supplied = self.headers.get("Authorization", "")
        if not supplied.startswith("Bearer ") or not secrets.compare_digest(supplied[7:], _access_password):
            self._json(401, {"error": "رمز ورود نادرست است."})
            return
        client = self.client_address[0]
        now = time.time()
        recent = [t for t in _requests.get(client, []) if now - t < WINDOW_SECONDS]
        if len(recent) >= MAX_REQUESTS_PER_WINDOW:
            self._json(429, {"error": "تعداد درخواست‌ها زیاد است. کمی بعد دوباره تلاش کن."})
            return
        recent.append(now)
        _requests[client] = recent
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > MAX_BODY:
                self._json(413, {"error": "درخواست بیش از حد بزرگ است."})
                return
            data = json.loads(self.rfile.read(length))
            messages = data.get("messages")
            if not isinstance(messages, list) or not messages or len(messages) > MAX_MESSAGES:
                self._json(400, {"error": "ساختار تاریخچه گفتگو معتبر نیست."})
                return
            safe_messages = []
            for item in messages:
                if not isinstance(item, dict) or item.get("role") not in {"user", "assistant"}:
                    self._json(400, {"error": "پیام نامعتبر است."})
                    return
                content = item.get("content")
                if not isinstance(content, str) or not content.strip() or len(content) > MAX_MESSAGE_CHARS:
                    self._json(400, {"error": "متن پیام خالی یا بیش از حد طولانی است."})
                    return
                safe_messages.append({"role": item["role"], "content": content})
            if safe_messages[-1]["role"] != "user":
                self._json(400, {"error": "آخرین پیام باید از طرف کاربر باشد."})
                return
            turn = _provider.generate_turn(
                _agent, AgentRequest(task=safe_messages[-1]["content"]),
                safe_messages, [],
            )
            answer = getattr(turn, "content", None)
            if not isinstance(answer, str) or not answer.strip():
                self._json(502, {"error": "مدل پاسخ متنی معتبری برنگرداند."})
                return
            self._json(200, {"reply": answer.strip()})
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
            self._json(400, {"error": "درخواست JSON معتبر نیست."})
        except Exception:
            # Never send provider internals, headers, or credentials to the browser.
            self._json(502, {"error": "ارتباط با مدل هوش مصنوعی ناموفق بود. تنظیمات سرور را بررسی کن."})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
