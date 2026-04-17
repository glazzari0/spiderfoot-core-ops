import json
import socket
import urllib.error
import urllib.request


class OllamaClient:
    """Minimal local Ollama client for SpiderFoot Core-Ops."""

    def __init__(self, base_url: str, timeout: float = 60.0) -> None:
        self.base_url = (base_url or "http://127.0.0.1:11434").rstrip("/")
        self.timeout = timeout

    def _post_json(self, path: str, payload: dict) -> dict:
        body = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url}{path}",
            data=body,
            method="POST",
            headers={"Content-Type": "application/json"},
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"Ollama retornou erro HTTP {e.code}: {detail}") from e
        except (TimeoutError, socket.timeout) as e:
            raise RuntimeError(
                f"O Ollama excedeu o tempo limite de {self.timeout:.0f}s ao processar a solicitação."
            ) from e
        except urllib.error.URLError as e:
            raise RuntimeError(
                f"Não foi possível alcançar o Ollama em {self.base_url}. Verifique se o servidor local está ativo."
            ) from e

    def _get_json(self, path: str) -> dict:
        request = urllib.request.Request(
            f"{self.base_url}{path}",
            method="GET",
            headers={"Content-Type": "application/json"},
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"Ollama retornou erro HTTP {e.code}: {detail}") from e
        except (TimeoutError, socket.timeout) as e:
            raise RuntimeError(
                f"O Ollama excedeu o tempo limite de {self.timeout:.0f}s ao processar a solicitação."
            ) from e
        except urllib.error.URLError as e:
            raise RuntimeError(
                f"NÃ£o foi possÃ­vel alcanÃ§ar o Ollama em {self.base_url}. Verifique se o servidor local estÃ¡ ativo."
            ) from e

    def list_models(self) -> list:
        payload = self._get_json("/api/tags")
        return payload.get("models", [])

    def generate_json(self, model: str, prompt: str, system: str = None, temperature: float = 0.2) -> dict:
        if not model:
            raise RuntimeError("Nenhum modelo Ollama foi configurado para análise.")

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": temperature,
            },
        }
        if system:
            payload["system"] = system

        return self._post_json("/api/generate", payload)
