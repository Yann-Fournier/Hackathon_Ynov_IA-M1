"""
Backend / API client for the TechCorp financial assistant chat.

Wraps the Ollama HTTP API (https://github.com/ollama/ollama/blob/main/docs/api.md):
- GET  /api/tags  -> server status + list of available models
- POST /api/chat  -> chat completion, with streaming support

A mock mode is included so the frontend can be built/tested before the
Ollama server is reachable or the financial model is loaded.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Generator

import requests

DEFAULT_BASE_URL = "http://localhost:11434"
DEFAULT_TIMEOUT = 5  # seconds, for status checks
CHAT_TIMEOUT = 120  # seconds, for generation requests


@dataclass
class ServerStatus:
    connected: bool
    models: list[str] = field(default_factory=list)
    error: str | None = None


class OllamaClient:
    def __init__(self, base_url: str = DEFAULT_BASE_URL, model: str | None = None):
        self.base_url = base_url.rstrip("/")
        self.model = model

    def check_connection(self) -> ServerStatus:
        """Ping the server and list available models. Used for the connected/disconnected indicator."""
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=DEFAULT_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            models = [m["name"] for m in data.get("models", [])]
            return ServerStatus(connected=True, models=models)
        except requests.exceptions.RequestException as exc:
            return ServerStatus(connected=False, error=str(exc))

    def chat(
        self,
        messages: list[dict],
        stream: bool = True,
    ) -> Generator[str, None, None]:
        """
        Send the full conversation history to /api/chat and yield response
        text chunks as they arrive (or a single chunk if stream=False).

        messages: list of {"role": "user"|"assistant"|"system", "content": str}
        """
        if not self.model:
            raise ValueError("No model configured. Set client.model before calling chat().")

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
        }

        with requests.post(
            f"{self.base_url}/api/chat",
            json=payload,
            stream=stream,
            timeout=CHAT_TIMEOUT,
        ) as resp:
            resp.raise_for_status()

            if not stream:
                yield resp.json()["message"]["content"]
                return

            for line in resp.iter_lines():
                if not line:
                    continue
                chunk = json.loads(line)
                if chunk.get("done"):
                    break
                content = chunk.get("message", {}).get("content", "")
                if content:
                    yield content


class MockOllamaClient:
    """Drop-in replacement for OllamaClient, no network calls. Lets the frontend
    be developed and demoed before the real Ollama server/model is available."""

    def __init__(self, base_url: str = DEFAULT_BASE_URL, model: str | None = "phi3-financial-mock"):
        self.base_url = base_url
        self.model = model

    def check_connection(self) -> ServerStatus:
        return ServerStatus(connected=True, models=[self.model])

    def chat(self, messages: list[dict], stream: bool = True) -> Generator[str, None, None]:
        last_user_msg = next(
            (m["content"] for m in reversed(messages) if m["role"] == "user"), ""
        )
        fake_response = (
            f"[MOCK] Voici une reponse simulee a : \"{last_user_msg}\". "
            "Branchez le vrai serveur Ollama pour une reponse reelle."
        )
        if not stream:
            yield fake_response
            return
        for word in fake_response.split(" "):
            time.sleep(0.05)
            yield word + " "


class ConversationHistory:
    """Server-side conversation state, independent of any UI framework."""

    def __init__(self, system_prompt: str | None = None):
        self.messages: list[dict] = []
        if system_prompt:
            self.messages.append({"role": "system", "content": system_prompt})

    def add_user(self, content: str) -> None:
        self.messages.append({"role": "user", "content": content})

    def add_assistant(self, content: str) -> None:
        self.messages.append({"role": "assistant", "content": content})

    def as_list(self) -> list[dict]:
        return self.messages

    def clear(self, keep_system: bool = True) -> None:
        if keep_system:
            self.messages = [m for m in self.messages if m["role"] == "system"]
        else:
            self.messages = []


def get_client(base_url: str = DEFAULT_BASE_URL, model: str | None = None, mock: bool = False):
    """Factory used by the frontend: flip `mock=True` to develop without a live server."""
    if mock:
        return MockOllamaClient(base_url=base_url, model=model or "phi3-financial-mock")
    return OllamaClient(base_url=base_url, model=model)


if __name__ == "__main__":
    # Quick manual test from the terminal, no Streamlit required:
    #   python backend.py            -> uses the real Ollama server
    #   python backend.py --mock     -> uses the mock client
    import sys

    use_mock = "--mock" in sys.argv
    client = get_client(mock=use_mock)

    status = client.check_connection()
    print(f"Connected: {status.connected}")
    if status.connected:
        print(f"Available models: {status.models}")
    else:
        print(f"Error: {status.error}")
        if not use_mock:
            sys.exit(1)

    if not client.model:
        if status.models:
            client.model = status.models[0]
            print(f"No model specified, using: {client.model}")
        else:
            print("No model available on the server.")
            sys.exit(1)

    history = ConversationHistory(
        system_prompt="You are a financial assistant for TechCorp Industries."
    )
    history.add_user("What is compound interest?")

    print("\nAssistant: ", end="", flush=True)
    full_response = ""
    for chunk in client.chat(history.as_list(), stream=True):
        print(chunk, end="", flush=True)
        full_response += chunk
    print()
    history.add_assistant(full_response)
