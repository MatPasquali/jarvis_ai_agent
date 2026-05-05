"""
Módulo de memória do JARVIS
- Primário: ChromaDB (busca semântica por vetores)
- Fallback: JSON simples (sem dependências extras)
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List

MEMORY_DIR = Path("memory")
MEMORY_FILE = MEMORY_DIR / "history.json"

try:
    import chromadb
    from chromadb.utils import embedding_functions
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False


class MemoryModule:
    def __init__(self):
        MEMORY_DIR.mkdir(exist_ok=True)
        self.backend = "chroma" if CHROMA_AVAILABLE else "json"

        if self.backend == "chroma":
            self._init_chroma()
        else:
            self._init_json()

        print(f"   ✓ Memória pronta (backend: {self.backend})")

    def _init_chroma(self):
        """Inicializa o ChromaDB para busca semântica."""
        self.client = chromadb.PersistentClient(path=str(MEMORY_DIR / "chroma"))
        ef = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.client.get_or_create_collection(
            name="jarvis_memory",
            embedding_function=ef,
        )

    def _init_json(self):
        """Inicializa memória simples em JSON."""
        if not MEMORY_FILE.exists():
            MEMORY_FILE.write_text("[]")

    def save(self, user_input: str, assistant_reply: str):
        """Salva um par pergunta/resposta na memória."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "user": user_input,
            "assistant": assistant_reply,
        }

        if self.backend == "chroma":
            doc_id = f"mem_{datetime.now().timestamp()}"
            self.collection.add(
                documents=[f"Usuário: {user_input}\nJARVIS: {assistant_reply}"],
                ids=[doc_id],
                metadatas=[entry],
            )
        else:
            history = json.loads(MEMORY_FILE.read_text())
            history.append(entry)
            # Mantém apenas as últimas 500 entradas
            if len(history) > 500:
                history = history[-500:]
            MEMORY_FILE.write_text(json.dumps(history, ensure_ascii=False, indent=2))

    def search(self, query: str, k: int = 3) -> List[str]:
        """Busca memórias relevantes para o contexto atual."""
        if self.backend == "chroma":
            try:
                results = self.collection.query(query_texts=[query], n_results=k)
                return results["documents"][0] if results["documents"] else []
            except Exception:
                return []
        else:
            # Busca simples por palavras-chave no JSON
            history = json.loads(MEMORY_FILE.read_text())
            query_words = set(query.lower().split())
            matches = []
            for entry in reversed(history[-100:]):
                text = entry["user"].lower() + " " + entry["assistant"].lower()
                if any(w in text for w in query_words):
                    matches.append(f"Usuário: {entry['user']}\nJARVIS: {entry['assistant']}")
                if len(matches) >= k:
                    break
            return matches

    def get_recent(self, n: int = 5) -> List[dict]:
        """Retorna as n interações mais recentes."""
        if self.backend == "chroma":
            try:
                results = self.collection.get(limit=n, include=["metadatas"])
                return results.get("metadatas", [])
            except Exception:
                return []
        else:
            history = json.loads(MEMORY_FILE.read_text())
            return history[-n:]

    def clear(self):
        """Limpa toda a memória."""
        if self.backend == "chroma":
            self.client.delete_collection("jarvis_memory")
            self._init_chroma()
        else:
            MEMORY_FILE.write_text("[]")
        print("🗑️  Memória limpa.")
