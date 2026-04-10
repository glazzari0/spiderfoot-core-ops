import json
import re

from .ollama_client import OllamaClient


class FindingAiAssistant:
    """AI-assisted analyst helper for finding triage."""

    def __init__(self, config: dict) -> None:
        self.config = config

    def enabled(self) -> bool:
        return bool(self.config.get("_ai_enabled")) and bool(self.config.get("_ai_ollama_enabled"))

    def is_configured(self) -> tuple:
        if not self.config.get("_ai_enabled"):
            return False, "A camada de IA está desabilitada nas configurações."

        if not self.config.get("_ai_ollama_enabled"):
            return False, "O uso do Ollama está desabilitado nas configurações."

        if not self.config.get("_ai_ollama_base_url"):
            return False, "A URL do servidor Ollama não foi configurada."

        if not self.config.get("_ai_ollama_chat_model"):
            return False, "Nenhum modelo de chat do Ollama foi configurado."

        return True, ""

    def _extract_json(self, raw_text: str) -> dict:
        text = (raw_text or "").strip()
        if not text:
            raise RuntimeError("O Ollama não retornou conteúdo para a análise.")

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            raise RuntimeError("O retorno do Ollama não veio em JSON válido.")

    def analyze_finding(self, finding: dict, state: dict, validations: list, evidence: list, labels: dict) -> dict:
        is_ready, message = self.is_configured()
        if not is_ready:
            raise RuntimeError(message)

        timeout_seconds = self.config.get("_ai_ollama_timeout_seconds", 180)
        try:
            timeout_seconds = float(timeout_seconds)
        except (TypeError, ValueError):
            timeout_seconds = 180.0

        client = OllamaClient(self.config.get("_ai_ollama_base_url"), timeout=timeout_seconds)

        system_prompt = (
            "Você é um assistente local de segurança do SpiderFoot Core-Ops. "
            "Seu trabalho é apoiar a triagem de um único achado de investigação. "
            "Não invente fatos. Baseie-se apenas no contexto recebido. "
            "Retorne SOMENTE JSON válido."
        )

        payload = {
            "finding": finding,
            "current_state": state,
            "recent_validations": validations[:5],
            "recent_evidence": evidence[:5],
            "allowed_labels": labels,
            "required_output_schema": {
                "summary": "string",
                "triage_status_suggestion": "one of allowed_labels.triage_status keys",
                "relevance_suggestion": "one of allowed_labels.relevance keys",
                "exploitability_suggestion": "one of allowed_labels.exploitability keys",
                "analyst_verdict_suggestion": "one of allowed_labels.analyst_verdict keys",
                "suggested_evidence_type": "short string such as nota, url, evidencia_tecnica, ioc or impacto",
                "suggested_evidence_title": "short string",
                "suggested_evidence_content": "string",
                "confidence": "integer 0-100",
                "reasoning": ["short bullet", "short bullet"],
                "evidence_gaps": ["short bullet"],
                "next_steps": ["short bullet"],
                "operator_note_draft": "string"
            }
        }

        prompt = (
            "Analise o achado abaixo e gere uma sugestão operacional para o analista.\n"
            "Regras:\n"
            "- use apenas os rótulos permitidos\n"
            "- seja conservador com explorabilidade\n"
            "- se faltar evidência, destaque isso\n"
            "- sempre preencha suggested_evidence_type, suggested_evidence_title e suggested_evidence_content\n"
            "- mantenha o resumo curto e objetivo\n\n"
            f"{json.dumps(payload, ensure_ascii=False, indent=2)}"
        )

        requested_model = self.config.get("_ai_ollama_chat_model")

        raw_response = client.generate_json(
            model=requested_model,
            prompt=prompt,
            system=system_prompt,
            temperature=0.2,
        )

        parsed = self._extract_json(raw_response.get("response", ""))
        resolved_model = raw_response.get("model") or requested_model
        suggested_evidence_title = parsed.get("suggested_evidence_title", "").strip() or f"Evidência sugerida para {finding.get('event_label') or finding.get('event_type') or 'achado'}"
        suggested_evidence_content = parsed.get("suggested_evidence_content", "").strip() or (
            parsed.get("operator_note_draft", "").strip()
            or parsed.get("summary", "").strip()
            or "Registrar evidência contextual e validação complementar para este achado."
        )

        return {
            "provider": "ollama",
            "requested_model": requested_model,
            "resolved_model": resolved_model,
            "model": resolved_model,
            "summary": parsed.get("summary", ""),
            "triage_status_suggestion": parsed.get("triage_status_suggestion", "em_triagem"),
            "relevance_suggestion": parsed.get("relevance_suggestion", "pendente"),
            "exploitability_suggestion": parsed.get("exploitability_suggestion", "nao_avaliado"),
            "analyst_verdict_suggestion": parsed.get("analyst_verdict_suggestion", "em_analise"),
            "suggested_evidence_type": parsed.get("suggested_evidence_type", "nota"),
            "suggested_evidence_title": suggested_evidence_title,
            "suggested_evidence_content": suggested_evidence_content,
            "confidence": parsed.get("confidence", 0),
            "reasoning": parsed.get("reasoning", []),
            "evidence_gaps": parsed.get("evidence_gaps", []),
            "next_steps": parsed.get("next_steps", []),
            "operator_note_draft": parsed.get("operator_note_draft", ""),
            "raw": parsed,
        }
