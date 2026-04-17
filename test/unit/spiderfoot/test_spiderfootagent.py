import json
import unittest
import uuid

from spiderfoot import SecurityValidationLoop, SpiderFootDb, SpiderFootEvent, SpiderFootHelpers, ValidationPlanBuilder


class FakeToolExecutor:
    def __init__(self):
        self.calls = []

    def execute(self, tool_name, finding):
        self.calls.append(tool_name)
        if tool_name == "dns_lookup":
            return {
                "tool_name": tool_name,
                "status": "ok",
                "summary": "DNS observado.",
                "details": {"records": ["93.184.216.34"]},
            }
        if tool_name == "http_probe":
            return {
                "tool_name": tool_name,
                "status": "ok",
                "summary": "HTTP observado.",
                "details": {"code": 200},
            }
        if tool_name == "final_validation":
            return {
                "validator": "http_dns_probe",
                "status": "ok",
                "summary": "Validação consolidada concluída.",
                "details": json.dumps({"code": 200}, ensure_ascii=False),
            }
        return {
            "tool_name": tool_name,
            "status": "warning",
            "summary": "Etapa genérica.",
            "details": {},
        }


class TestSpiderFootAgent(unittest.TestCase):
    def setUp(self):
        self.default_options = {
            '_debug': False,
            '__logging': True,
            '__outputfilter': None,
            '_useragent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0',
            '_dnsserver': '',
            '_fetchtimeout': 5,
            '_internettlds': 'https://publicsuffix.org/list/effective_tld_names.dat',
            '_internettlds_cache': 72,
            '_genericusers': ",".join(SpiderFootHelpers.usernamesFromWordlists(['generic-usernames'])),
            '__database': f"{SpiderFootHelpers.dataPath()}/spiderfoot.test.db",
            '__modules__': None,
            '__correlationrules__': None,
            '_socks1type': '',
            '_socks2addr': '',
            '_socks3port': '',
            '_socks4user': '',
            '_socks5pwd': '',
            '__logstdout': False
        }

    def _create_scan_with_finding(self, dbh):
        instance_id = f"agent-scan-{uuid.uuid4()}"
        dbh.scanInstanceCreate(instance_id, "Agent Scan", "example.org")

        root_event = SpiderFootEvent("ROOT", "example.org", "", None)
        dbh.scanEventStore(instance_id, root_event)

        finding_event = SpiderFootEvent("DOMAIN_NAME", "example.org", "sfp_test", root_event)
        dbh.scanEventStore(instance_id, finding_event)

        return instance_id, finding_event.hash

    def test_security_validation_loop_should_store_session_validation_and_evidence(self):
        dbh = SpiderFootDb(self.default_options, False)
        instance_id, result_hash = self._create_scan_with_finding(dbh)
        executor = FakeToolExecutor()
        loop = SecurityValidationLoop(tool_executor=executor)

        result = loop.run(
            dbh,
            instance_id,
            result_hash,
            {
                "event_type": "DOMAIN_NAME",
                "event_label": "Domain Name",
                "data": "example.org",
            },
        )

        self.assertEqual(result["final_validation"]["status"], "ok")
        self.assertEqual(executor.calls, ["dns_lookup", "http_probe", "final_validation"])

        latest_session = dbh.agentSessionLatest(instance_id, result_hash, loop.AGENT_TYPE)
        self.assertIsNotNone(latest_session)
        self.assertEqual(latest_session["status"], "completed")

        session_steps = dbh.agentSessionSteps(latest_session["id"])
        self.assertEqual(len(session_steps), 3)

        validation_rows = dbh.validationRunList(instance_id, result_hash)
        self.assertEqual(len(validation_rows), 1)
        self.assertEqual(validation_rows[0][1], "http_dns_probe")

        evidence_rows = dbh.findingEvidenceList(instance_id, result_hash)
        self.assertEqual(len(evidence_rows), 1)
        self.assertEqual(evidence_rows[0][1], "security_loop")
        self.assertIn("Prioridade calculada:", result["summary"])

    def test_security_validation_loop_should_skip_tools_seen_in_previous_session(self):
        dbh = SpiderFootDb(self.default_options, False)
        instance_id, result_hash = self._create_scan_with_finding(dbh)
        first_executor = FakeToolExecutor()
        second_executor = FakeToolExecutor()

        first_loop = SecurityValidationLoop(tool_executor=first_executor)
        second_loop = SecurityValidationLoop(tool_executor=second_executor)

        finding = {
            "event_type": "DOMAIN_NAME",
            "event_label": "Domain Name",
            "data": "example.org",
        }

        first_loop.run(dbh, instance_id, result_hash, finding)
        result = second_loop.run(dbh, instance_id, result_hash, finding)

        self.assertEqual(second_executor.calls, ["final_validation"])
        self.assertEqual(result["steps"][0]["status"], "skipped")
        self.assertEqual(result["steps"][1]["status"], "skipped")
        self.assertEqual(result["steps"][2]["status"], "ok")

    def test_validation_plan_builder_should_prioritize_correlation_and_triage_context(self):
        dbh = SpiderFootDb(self.default_options, False)
        instance_id, result_hash = self._create_scan_with_finding(dbh)
        dbh.findingStateSet(instance_id, result_hash, "em_triagem", "critica", "potencial", "em_analise", "priorizar")
        dbh.correlationResultCreate(
            instance_id,
            "vulnerability_critical",
            "Critical Exposure",
            "Correlation showing high-risk context",
            "critical",
            "logic: example",
            "Hostname appears in critical exposure chain",
            [result_hash],
        )

        builder = ValidationPlanBuilder(max_steps=4)
        plan_bundle = builder.build(
            {
                "event_type": "DOMAIN_NAME",
                "event_label": "Domain Name",
                "data": "example.org",
                "risk": 40,
            },
            state=dbh.findingStateGet(instance_id, result_hash),
            evidence_rows=dbh.findingEvidenceList(instance_id, result_hash),
            validation_rows=dbh.validationRunList(instance_id, result_hash),
            correlation_rows=dbh.findingCorrelationList(instance_id, result_hash),
            prior_steps=[],
        )

        self.assertEqual(plan_bundle["priority_label"], "imediata")
        self.assertGreaterEqual(plan_bundle["priority_score"], 80)
        self.assertTrue(plan_bundle["reasoning"])
        self.assertEqual(plan_bundle["steps"][0]["tool_name"], "dns_lookup")
        self.assertEqual(plan_bundle["steps"][1]["tool_name"], "http_probe")
