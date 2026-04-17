# -*- coding: utf-8 -*-
import json
import socket
import urllib.parse

from spiderfoot.validators import FindingValidatorEngine


class SecurityToolExecutor:
    """Executes the safe validation tools used by the Security Loop."""

    def __init__(self, validator_engine: FindingValidatorEngine = None) -> None:
        self.validator_engine = validator_engine or FindingValidatorEngine()

    def execute(self, tool_name: str, finding: dict) -> dict:
        if tool_name == "dns_lookup":
            return self._dns_lookup(finding)
        if tool_name == "http_probe":
            return self._http_probe(finding)
        if tool_name == "reverse_dns":
            return self._reverse_dns(finding)
        if tool_name == "tcp_common":
            return self._tcp_common(finding)
        if tool_name == "email_domain_resolution":
            return self._email_domain_resolution(finding)
        if tool_name == "final_validation":
            return self.validator_engine.validate(finding.get("event_type"), finding.get("data"))
        raise ValueError(f"Ferramenta de validação não suportada: {tool_name}")

    def _extract_host(self, finding: dict) -> str:
        event_data = (finding.get("data") or "").strip()
        if not event_data:
            return ""

        extracted = self.validator_engine._extract_target(event_data)
        if not extracted:
            return ""

        if extracted.lower().startswith(("http://", "https://")):
            return urllib.parse.urlparse(extracted).hostname or ""

        if "@" in extracted and not extracted.startswith("@"):
            return extracted.split("@", 1)[1]

        return extracted

    def _dns_lookup(self, finding: dict) -> dict:
        host = self._extract_host(finding)
        records = []
        error = ""

        if host:
            try:
                records = sorted({item[4][0] for item in socket.getaddrinfo(host, None)})
            except Exception as exc:
                error = str(exc)

        return {
            "tool_name": "dns_lookup",
            "status": "ok" if records else "warning",
            "summary": "Resolução DNS observada." if records else "Sem resposta DNS conclusiva.",
            "details": {"host": host, "records": records, "error": error},
        }

    def _http_probe(self, finding: dict) -> dict:
        target = self.validator_engine._extract_target(finding.get("data"))
        result = self.validator_engine._http_probe(target)
        status = "ok" if result.get("status") == "ok" else "warning"
        return {
            "tool_name": "http_probe",
            "status": status,
            "summary": "HTTP/HTTPS respondeu ao probe seguro." if status == "ok" else "Sem resposta HTTP/HTTPS conclusiva.",
            "details": {"target": target, "probe": result},
        }

    def _reverse_dns(self, finding: dict) -> dict:
        target = (finding.get("data") or "").strip()
        resolved = ""
        error = ""

        try:
            resolved = socket.gethostbyaddr(target)[0]
        except Exception as exc:
            error = str(exc)

        return {
            "tool_name": "reverse_dns",
            "status": "ok" if resolved else "warning",
            "summary": "Reverse DNS identificado." if resolved else "Reverse DNS não identificado.",
            "details": {"target": target, "reverse_dns": resolved, "error": error},
        }

    def _tcp_common(self, finding: dict) -> dict:
        target = (finding.get("data") or "").strip()
        ports = self.validator_engine._tcp_probe(target, [21, 22, 25, 53, 80, 110, 143, 443, 445, 8080, 8443])
        return {
            "tool_name": "tcp_common",
            "status": "ok" if ports else "warning",
            "summary": "Portas comuns responderam ao probe seguro." if ports else "Nenhuma porta comum respondeu ao probe seguro.",
            "details": {"target": target, "open_ports": ports},
        }

    def _email_domain_resolution(self, finding: dict) -> dict:
        target = (finding.get("data") or "").strip()
        domain = target.split("@", 1)[1] if "@" in target else ""
        records = []
        error = ""

        if domain:
            try:
                records = sorted({item[4][0] for item in socket.getaddrinfo(domain, 25)})
            except Exception as exc:
                error = str(exc)

        return {
            "tool_name": "email_domain_resolution",
            "status": "ok" if records else "warning",
            "summary": "Domínio do e-mail possui resolução observável." if records else "Não foi possível observar resolução do domínio do e-mail.",
            "details": {"domain": domain, "records": records, "error": error},
        }


class ValidationPlanBuilder:
    """Builds a richer validation plan using triage state, correlations and history."""

    def __init__(self, validator_engine: FindingValidatorEngine = None, max_steps: int = 4) -> None:
        self.validator_engine = validator_engine or FindingValidatorEngine()
        self.max_steps = max_steps

    def build(self, finding: dict, state: dict = None, evidence_rows: list = None,
              validation_rows: list = None, correlation_rows: list = None, prior_steps: list = None) -> dict:
        state = state or {}
        evidence_rows = evidence_rows or []
        validation_rows = validation_rows or []
        correlation_rows = correlation_rows or []
        prior_steps = prior_steps or []

        priority = self._score_priority(finding, state, validation_rows, correlation_rows)
        reasoning = self._build_reasoning(finding, state, validation_rows, correlation_rows, evidence_rows)
        steps = self._assemble_steps(finding, state, validation_rows, correlation_rows, prior_steps)

        return {
            "priority_score": priority,
            "priority_label": self._priority_label(priority),
            "reasoning": reasoning,
            "steps": steps[:self.max_steps],
        }

    def _risk_policy_for_tool(self, tool_name: str) -> dict:
        policies = {
            "dns_lookup": {
                "category": "enriquecimento_externo",
                "label": "Enriquecimento externo",
                "requires_confirmation": False,
            },
            "reverse_dns": {
                "category": "enriquecimento_externo",
                "label": "Enriquecimento externo",
                "requires_confirmation": False,
            },
            "email_domain_resolution": {
                "category": "enriquecimento_externo",
                "label": "Enriquecimento externo",
                "requires_confirmation": False,
            },
            "http_probe": {
                "category": "validacao_ativa",
                "label": "Validação ativa",
                "requires_confirmation": True,
            },
            "tcp_common": {
                "category": "validacao_ativa",
                "label": "Validação ativa",
                "requires_confirmation": True,
            },
            "final_validation": {
                "category": "leitura_segura",
                "label": "Leitura segura",
                "requires_confirmation": False,
            },
        }
        return policies.get(tool_name, {
            "category": "acao_controlada",
            "label": "Ação controlada",
            "requires_confirmation": False,
        })

    def _score_priority(self, finding: dict, state: dict, validation_rows: list, correlation_rows: list) -> int:
        score = 0
        score += min(max(int(finding.get("risk", 0) or 0), 0), 100)

        relevance = (state.get("relevance") or "").lower()
        score += {"critica": 35, "alta": 25, "media": 15, "baixa": 5}.get(relevance, 0)

        triage_status = (state.get("triage_status") or "").lower()
        if triage_status in ["novo", "em_triagem", "relevante"]:
            score += 15
        if triage_status in ["descartado", "falso_positivo"]:
            score -= 25

        exploitability = (state.get("exploitability") or "").lower()
        if exploitability == "potencial":
            score += 15
        if exploitability == "confirmada":
            score += 25
        if exploitability in ["nao_aplicavel", "nao_exploravel"]:
            score -= 10

        verdict = (state.get("analyst_verdict") or "").lower()
        if verdict in ["exploravel", "critico", "exposto_confirmado"]:
            score += 20
        if verdict in ["monitorar", "sem_risco_pratico"]:
            score -= 10

        if not validation_rows:
            score += 12
        else:
            latest_status = (validation_rows[0][2] or "").lower()
            if latest_status == "warning":
                score += 8
            if latest_status == "error":
                score += 5
            if latest_status == "ok":
                score -= 5

        for corr in correlation_rows:
            risk = (corr[3] or "").lower()
            score += {"critical": 30, "high": 20, "medium": 10, "low": 4}.get(risk, 0)

        return max(0, min(score, 100))

    def _priority_label(self, score: int) -> str:
        if score >= 80:
            return "imediata"
        if score >= 60:
            return "alta"
        if score >= 35:
            return "media"
        return "rotina"

    def _build_reasoning(self, finding: dict, state: dict, validation_rows: list,
                         correlation_rows: list, evidence_rows: list) -> list:
        reasons = []

        if correlation_rows:
            top = correlation_rows[0]
            reasons.append(
                f"Achado relacionado à correlação '{top[1]}' com risco '{top[3]}', aumentando a prioridade de validação."
            )

        relevance = state.get("relevance")
        if relevance in ["alta", "critica", "media"]:
            reasons.append(f"Relevância atual marcada como '{relevance}', indicando necessidade de confirmação técnica.")

        triage_status = state.get("triage_status")
        if triage_status in ["novo", "em_triagem", "relevante"]:
            reasons.append(f"Achado em estado '{triage_status}', ainda sem encerramento operacional.")

        if not validation_rows:
            reasons.append("Ainda não há histórico de validação registrado para este achado.")
        elif (validation_rows[0][2] or "").lower() != "ok":
            reasons.append("A validação mais recente não foi conclusiva, então o plano reforça observações seguras.")

        if not evidence_rows:
            reasons.append("Ainda não há evidência operacional anexada, então o loop deve produzir um resumo verificável.")

        if not reasons:
            reasons.append("O plano foi mantido enxuto porque o achado já possui contexto operacional relevante.")

        return reasons

    def _assemble_steps(self, finding: dict, state: dict, validation_rows: list,
                        correlation_rows: list, prior_steps: list) -> list:
        event_type = (finding.get("event_type") or "").upper()
        steps = []
        seen = set()
        for step in prior_steps:
            if len(step) >= 3:
                seen.add(step[2])

        if correlation_rows and event_type in self.validator_engine.URLISH_TYPES:
            steps.append({
                "tool_name": "dns_lookup",
                "action": "Priorizar DNS porque o achado participa de correlações que dependem de contexto de infraestrutura.",
                "reason": "correlation_priority",
            })

        if correlation_rows and event_type in self.validator_engine.IP_TYPES:
            steps.append({
                "tool_name": "reverse_dns",
                "action": "Enriquecer o IP correlacionado com reverse DNS antes da consolidação.",
                "reason": "correlation_priority",
            })

        if event_type in self.validator_engine.URLISH_TYPES:
            steps.extend([
                {
                    "tool_name": "dns_lookup",
                    "action": "Confirmar resolução do hostname/URL antes da validação consolidada.",
                    "reason": "entity_family_urlish",
                },
                {
                    "tool_name": "http_probe",
                    "action": "Executar probe HTTP/HTTPS seguro para observar resposta do alvo.",
                    "reason": "entity_family_urlish",
                },
            ])
        elif event_type in self.validator_engine.IP_TYPES:
            steps.extend([
                {
                    "tool_name": "reverse_dns",
                    "action": "Consultar reverse DNS do endereço para enriquecer o contexto.",
                    "reason": "entity_family_ip",
                },
                {
                    "tool_name": "tcp_common",
                    "action": "Testar portas comuns com probe TCP seguro e observacional.",
                    "reason": "entity_family_ip",
                },
            ])
        elif event_type in self.validator_engine.EMAIL_TYPES:
            steps.append({
                "tool_name": "email_domain_resolution",
                "action": "Validar a resolução do domínio associado ao endereço de e-mail.",
                "reason": "entity_family_email",
            })

        if not validation_rows:
            steps.append({
                "tool_name": "final_validation",
                "action": "Executar o validador consolidado do SpiderFoot pela primeira vez.",
                "reason": "missing_validation_history",
            })
        else:
            steps.append({
                "tool_name": "final_validation",
                "action": "Reexecutar o validador consolidado do SpiderFoot com o contexto mais recente.",
                "reason": "refresh_validation_history",
            })

        deduped = []
        added = set()
        for step in steps:
            key = step["tool_name"]
            if key in added:
                continue
            added.add(key)
            deduped.append({
                "tool_name": step["tool_name"],
                "action": step["action"],
                "reason": step["reason"],
                "already_executed": step["tool_name"] in seen and step["tool_name"] != "final_validation",
                "risk_policy": self._risk_policy_for_tool(step["tool_name"]),
            })

        return deduped


class SecurityValidationLoop:
    """Small session-based validation loop for SpiderFoot findings."""

    AGENT_TYPE = "finding_validation_loop"

    def __init__(self, validator_engine: FindingValidatorEngine = None,
                 tool_executor: SecurityToolExecutor = None, max_steps: int = 4,
                 plan_builder: ValidationPlanBuilder = None) -> None:
        self.validator_engine = validator_engine or FindingValidatorEngine()
        self.tool_executor = tool_executor or SecurityToolExecutor(self.validator_engine)
        self.max_steps = max_steps
        self.plan_builder = plan_builder or ValidationPlanBuilder(self.validator_engine, max_steps=max_steps)

    def run(self, dbh, scan_instance_id: str, result_hash: str, finding: dict,
            state: dict = None, evidence_rows: list = None, validation_rows: list = None,
            correlation_rows: list = None, auto_store_evidence: bool = True) -> dict:
        previous_session = dbh.agentSessionLatest(scan_instance_id, result_hash, self.AGENT_TYPE)
        previous_steps = dbh.agentSessionSteps(previous_session["id"]) if previous_session else []
        plan_bundle = self.plan_builder.build(
            finding,
            state=state,
            evidence_rows=evidence_rows,
            validation_rows=validation_rows,
            correlation_rows=correlation_rows,
            prior_steps=previous_steps,
        )
        plan = plan_bundle["steps"]
        session_id = dbh.agentSessionCreate(
            scan_instance_id,
            result_hash,
            self.AGENT_TYPE,
            status="running",
            summary="Sessão de validação em execução.",
            planJson=json.dumps(plan_bundle, ensure_ascii=False),
        )

        executed_steps = []
        final_validation = None
        step_index = 0

        for planned_step in plan:
            step_index += 1
            if planned_step.get("already_executed"):
                skipped = {
                    "tool_name": planned_step["tool_name"],
                    "status": "skipped",
                    "summary": "Etapa pulada porque já havia sido observada em sessão anterior recente.",
                    "details": {"reason": "already_executed", "plan_reason": planned_step.get("reason", "")},
                }
                dbh.agentSessionStepAdd(
                    session_id,
                    step_index,
                    planned_step["tool_name"],
                    planned_step["action"],
                    "skipped",
                    json.dumps(skipped, ensure_ascii=False),
                )
                executed_steps.append(skipped)
                continue

            result = self.tool_executor.execute(planned_step["tool_name"], finding)
            if "tool_name" not in result:
                result["tool_name"] = planned_step["tool_name"]
            result["plan_reason"] = planned_step.get("reason", "")
            dbh.agentSessionStepAdd(
                session_id,
                step_index,
                planned_step["tool_name"],
                planned_step["action"],
                result.get("status", "warning"),
                json.dumps(result, ensure_ascii=False),
            )
            executed_steps.append(result)

            if planned_step["tool_name"] == "final_validation":
                final_validation = result
                dbh.validationRunAdd(
                    scan_instance_id,
                    result_hash,
                    result.get("validator", planned_step["tool_name"]),
                    result.get("status", "warning"),
                    result.get("summary", ""),
                    result.get("details", ""),
                )

        if final_validation is None:
            final_validation = self.validator_engine.validate(finding.get("event_type"), finding.get("data"))
            dbh.validationRunAdd(
                scan_instance_id,
                result_hash,
                final_validation.get("validator", "final_validation"),
                final_validation.get("status", "warning"),
                final_validation.get("summary", ""),
                final_validation.get("details", ""),
            )

        summary = self._build_summary(finding, plan_bundle, final_validation, executed_steps, correlation_rows or [])
        evidence_id = None
        if auto_store_evidence:
            evidence_id = dbh.findingEvidenceAdd(
                scan_instance_id,
                result_hash,
                "security_loop",
                f"Sessão de validação para {finding.get('event_label') or finding.get('event_type') or 'achado'}",
                summary,
            )

        dbh.agentSessionUpdate(session_id, "completed", summary=summary, planJson=json.dumps(plan_bundle, ensure_ascii=False))

        return {
            "session_id": session_id,
            "summary": summary,
            "plan": plan,
            "plan_bundle": plan_bundle,
            "steps": executed_steps,
            "final_validation": final_validation,
            "evidence_id": evidence_id,
        }

    def _build_summary(self, finding: dict, plan_bundle: dict, final_validation: dict,
                       executed_steps: list, correlation_rows: list) -> str:
        lines = [
            f"Achado: {finding.get('event_label') or finding.get('event_type') or 'desconhecido'}",
            f"Valor: {finding.get('data') or ''}",
            f"Prioridade calculada: {plan_bundle.get('priority_label', 'rotina')} ({plan_bundle.get('priority_score', 0)})",
            f"Validador final: {final_validation.get('validator', 'desconhecido')}",
            f"Status final: {final_validation.get('status', 'warning')}",
            f"Resumo final: {final_validation.get('summary', '')}",
            "",
            "Razões de priorização:",
        ]

        for item in plan_bundle.get("reasoning", []):
            lines.append(f"- {item}")

        if correlation_rows:
            lines.append("")
            lines.append("Correlações associadas:")
            for corr in correlation_rows[:5]:
                lines.append(f"- {corr[1]} | risco={corr[3]} | regra={corr[2]}")

        lines.append("")
        lines.append("Etapas executadas:")
        for step in executed_steps:
            details = step.get("details", "")
            if isinstance(details, dict):
                rendered_details = json.dumps(details, ensure_ascii=False, sort_keys=True)
            else:
                rendered_details = str(details)
            lines.append(
                f"- {step.get('tool_name', 'desconhecido')}: {step.get('status', 'warning')} | "
                f"{step.get('summary', '')} | razão={step.get('plan_reason', '')} | {rendered_details}"
            )

        return "\n".join(lines)
