"""
Context extraction via OpenRouter (OpenAI-compatible API).
Reads venture documents and produces structured research signals.
"""
import json
from pathlib import Path
from openai import OpenAI
from .prompts import CONTEXT_EXTRACTION_SYSTEM, CONTEXT_EXTRACTION_USER
from .models import ContextSignals
from config.settings import (
    OPENROUTER_API_KEY, OPENROUTER_BASE_URL,
    CONTEXT_LLM_MODEL, CONTEXT_LLM_MAX_TOKENS,
)


class ContextExtractor:
    def __init__(self):
        self.client = OpenAI(
            base_url=OPENROUTER_BASE_URL,
            api_key=OPENROUTER_API_KEY,
        )

    def extract(
        self,
        venture_docs_dir: Path,
        metadata: dict | None = None
    ) -> ContextSignals:
        """
        Read all documents in venture_docs_dir, call LLM via OpenRouter,
        return structured ContextSignals.
        """
        documents_text = self._read_documents(venture_docs_dir)

        metadata_text = json.dumps(metadata, indent=2) if metadata else "No structured metadata provided."

        schema_json = json.dumps(ContextSignals.model_json_schema(), indent=2)

        user_message = CONTEXT_EXTRACTION_USER.format(
            documents_text=documents_text,
            metadata_text=metadata_text,
            schema_json=schema_json
        )

        response = self.client.chat.completions.create(
            model=CONTEXT_LLM_MODEL,
            max_tokens=CONTEXT_LLM_MAX_TOKENS,
            messages=[
                {"role": "system", "content": CONTEXT_EXTRACTION_SYSTEM},
                {"role": "user", "content": user_message},
            ],
        )

        response_text = response.choices[0].message.content

        if response_text.startswith("```"):
            response_text = response_text.split("\n", 1)[1]
            response_text = response_text.rsplit("```", 1)[0]

        signals = ContextSignals.model_validate_json(response_text)
        return signals

    def _read_documents(self, docs_dir: Path) -> str:
        """Read all supported files from the documents directory."""
        supported_extensions = {".md", ".txt", ".pdf", ".docx", ".csv"}
        documents = []

        for file_path in sorted(docs_dir.iterdir()):
            if file_path.suffix.lower() in supported_extensions:
                if file_path.suffix.lower() in {".md", ".txt", ".csv"}:
                    content = file_path.read_text(encoding="utf-8")
                    documents.append(f"--- FILE: {file_path.name} ---\n{content}\n")
                else:
                    documents.append(f"--- FILE: {file_path.name} (binary — extraction not yet implemented) ---\n")

        if not documents:
            raise FileNotFoundError(f"No supported documents found in {docs_dir}")

        return "\n".join(documents)
