"""Shared fixtures: the real hospital API on a free port and an offline lexical retriever."""
import json
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import pytest

from rag.config import ChunkingConfig, EncoderConfig, RetrieverConfig, SelectionConfig
from rag.retriever import Retriever

REPO_ROOT = Path(__file__).resolve().parents[1]


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("localhost", 0))
        return sock.getsockname()[1]


@pytest.fixture(scope="session")
def api_url():
    """The graders' api/servidor.py, unmodified, listening on a free local port."""
    port = _free_port()
    server = subprocess.Popen([sys.executable, str(REPO_ROOT / "api" / "servidor.py"), "--puerto", str(port)],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    url = f"http://127.0.0.1:{port}"
    deadline = time.monotonic() + 10
    while True:
        try:
            urllib.request.urlopen(f"{url}/espera", timeout=1).close()
            break
        except OSError:
            if time.monotonic() > deadline:
                server.kill()
                raise
            time.sleep(0.1)
    yield url
    server.kill()
    server.wait()


@pytest.fixture
def lexical_config(tmp_path) -> Path:
    """A retriever configuration file with the offline lexical encoder, for code that loads one by path."""
    path = tmp_path / "retriever.json"
    path.write_text(json.dumps({
        "corpus_dir": "datos/corpus",
        "encoder": {"type": "hashing_bow"},
        "chunking": {"strategy": "section", "max_chars": 700, "metadata": True},
        "selection": {"top_k": 1},
    }), encoding="utf-8")
    return path


@pytest.fixture(scope="session")
def lexical_retriever():
    config = RetrieverConfig(EncoderConfig("hashing_bow"), ChunkingConfig(strategy="section", max_chars=700),
                             SelectionConfig(top_k=2), corpus_dir="datos/corpus")
    return Retriever.from_config(config, base_dir=REPO_ROOT)
