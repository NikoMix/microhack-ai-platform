"""FastAPI chat application for the Contoso AI Assistant."""

from __future__ import annotations

import html
import json
import logging
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel, Field

from aiplatform.config import Settings, get_settings
from aiplatform.inference import Message, Role, get_chat_provider
from aiplatform.rag import RetrievedChunk, get_retriever

LOGGER = logging.getLogger(__name__)


class ChatMessage(BaseModel):
    """Incoming API chat message."""

    role: str = "user"
    content: str


class ChatRequest(BaseModel):
    """Incoming chat request body."""

    message: str | None = None
    messages: list[ChatMessage] = Field(default_factory=list)


class ChatResponseBody(BaseModel):
    """Outgoing grounded chat response body."""

    answer: str
    citations: list[str]
    sources: list[RetrievedChunk]
    provider: str
    model: str


HTML_PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Contoso AI Assistant</title>
  <style>
    body{font-family:system-ui,sans-serif;max-width:860px;margin:2rem auto;padding:0 1rem}
    #log{border:1px solid #ddd;border-radius:8px;padding:1rem;min-height:16rem}
    .user{font-weight:700}.assistant{white-space:pre-wrap}
    form{display:flex;gap:.5rem;margin-top:1rem}input{flex:1;padding:.75rem}button{padding:.75rem}
  </style>
</head>
<body>
  <h1>Contoso AI Assistant</h1>
  <p>Ask a grounded question about Contoso policy or the AI Platform microhack.</p>
  <div id="log"></div>
  <form id="form"><input id="message" autocomplete="off" autofocus><button>Send</button></form>
  <script>
    const log = document.querySelector('#log');
    document.querySelector('#form').addEventListener('submit', async (event) => {
      event.preventDefault();
      const input = document.querySelector('#message');
      const message = input.value.trim();
      if (!message) return;
      input.value = '';
      log.innerHTML += `<p class="user">You: ${message.replaceAll('<','&lt;')}</p>`;
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {'content-type':'application/json'},
        body: JSON.stringify({message})
      });
      const data = await response.json();
      log.innerHTML += `<p class="assistant">Assistant: ${data.answer.replaceAll('<','&lt;')}</p>`;
    });
  </script>
</body>
</html>"""


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create and configure the FastAPI application."""
    resolved = settings or get_settings()
    app = FastAPI(title="Contoso AI Assistant")
    app.state.settings = resolved

    @app.get("/", response_class=HTMLResponse)
    async def index() -> str:
        return HTML_PAGE

    @app.get("/healthz")
    async def healthz() -> dict[str, str]:
        return {
            "status": "ok",
            "provider": resolved.inference_provider.value,
            "retrieval_backend": resolved.retrieval_backend.value,
        }

    @app.post("/api/chat")
    async def chat(request: ChatRequest) -> ChatResponseBody:
        prompt = _extract_prompt(request)
        chunks = await get_retriever(resolved).retrieve(prompt, k=4)
        messages = _build_grounded_messages(prompt, chunks, request.messages)
        provider = get_chat_provider(resolved)
        try:
            completion = await provider.complete(messages)
        finally:
            await provider.aclose()
        citations = [chunk.source for chunk in chunks]
        answer = _append_citations(completion.content, citations)
        LOGGER.info("Answered chat request", extra={"sources": len(citations)})
        return ChatResponseBody(
            answer=answer,
            citations=citations,
            sources=chunks,
            provider=completion.provider,
            model=completion.model,
        )

    @app.get("/api/stream")
    async def stream(message: str) -> StreamingResponse:
        chunks = await get_retriever(resolved).retrieve(message, k=4)
        messages = _build_grounded_messages(message, chunks, [])
        return StreamingResponse(
            _sse_stream(messages, resolved),
            media_type="text/event-stream",
        )

    return app


def _extract_prompt(request: ChatRequest) -> str:
    if request.message:
        return request.message
    if request.messages:
        return request.messages[-1].content
    return ""


def _build_grounded_messages(
    prompt: str,
    chunks: list[RetrievedChunk],
    history: list[ChatMessage],
) -> list[Message]:
    context = "\n\n".join(
        f"Source: {chunk.source}\nScore: {chunk.score:.3f}\n{chunk.text}" for chunk in chunks
    )
    system = Message.system(
        "You are Contoso AI Assistant. Answer only from the supplied context. "
        "Cite source names inline. If the context is insufficient, say what is missing."
    )
    prior_messages = [
        Message(role=Role(role.role), content=role.content)
        for role in history[:-1]
        if role.role in {"user", "assistant", "system"}
    ]
    grounded_prompt = Message.user(
        f"Context:\n{context or 'No context retrieved.'}\n\nQuestion:\n{prompt}"
    )
    return [system, *prior_messages, grounded_prompt]


def _append_citations(answer: str, citations: list[str]) -> str:
    if not citations:
        return answer
    escaped = ", ".join(html.escape(source) for source in citations)
    return f"{answer}\n\nSources: {escaped}"


async def _sse_stream(messages: list[Message], settings: Settings) -> AsyncIterator[str]:
    provider = get_chat_provider(settings)
    try:
        async for chunk in provider.stream(messages):
            yield f"data: {json.dumps({'delta': chunk})}\n\n"
        yield "data: [DONE]\n\n"
    finally:
        await provider.aclose()


app = create_app()
