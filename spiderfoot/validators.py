# -*- coding: utf-8 -*-
import ipaddress
import json
import re
import socket
import ssl
import urllib.parse
import urllib.request


class FindingValidatorEngine:
    URLISH_TYPES = {
        "INTERNET_NAME", "DOMAIN_NAME", "AFFILIATE_INTERNET_NAME", "AFFILIATE_DOMAIN_NAME",
        "SOCIAL_MEDIA", "ACCOUNT_EXTERNAL_OWNED", "SIMILAR_ACCOUNT_EXTERNAL",
        "PUBLIC_CODE_REPO", "APPSTORE_ENTRY", "LEAKSITE_URL", "DARKNET_MENTION_URL",
        "CO_HOSTED_SITE", "CO_HOSTED_SITE_DOMAIN", "DOMAIN_NAME_PARENT", "SIMILARDOMAIN"
    }
    IP_TYPES = {"IP_ADDRESS", "IPV6_ADDRESS", "AFFILIATE_IPADDR", "AFFILIATE_IPV6_ADDRESS", "INTERNAL_IP_ADDRESS"}
    EMAIL_TYPES = {"EMAILADDR", "AFFILIATE_EMAILADDR", "EMAILADDR_GENERIC"}
    USERNAME_TYPES = {"USERNAME"}
    HUMAN_TYPES = {"HUMAN_NAME"}
    PHONE_TYPES = {"PHONE_NUMBER"}
    CRYPTO_TYPES = {"BITCOIN_ADDRESS", "ETHEREUM_ADDRESS"}
    NETBLOCK_TYPES = {"NETBLOCK_OWNER", "NETBLOCKV6_OWNER", "NETBLOCK_MEMBER", "NETBLOCKV6_MEMBER"}
    COMPANY_TYPES = {"COMPANY_NAME", "AFFILIATE_COMPANY_NAME", "BGP_AS_OWNER", "BGP_AS_MEMBER"}
    GEO_TYPES = {"COUNTRY_NAME", "PHYSICAL_ADDRESS", "PHYSICAL_COORDINATES", "GEOINFO"}
    SERVICE_TYPES = {
        "PROVIDER_DNS", "PROVIDER_HOSTING", "PROVIDER_MAIL", "PROVIDER_TELCO", "PROVIDER_JAVASCRIPT",
        "TCP_PORT_OPEN", "UDP_PORT_OPEN", "TCP_PORT_OPEN_BANNER", "UDP_PORT_OPEN_INFO",
        "WEBSERVER_BANNER", "WEBSERVER_HTTPHEADERS", "SSL_CERTIFICATE_ISSUED", "SSL_CERTIFICATE_ISSUER"
    }
    DATA_TYPES = {
        "RAW_RIR_DATA", "RAW_DNS_RECORDS", "TARGET_WEB_CONTENT", "SEARCH_ENGINE_WEB_CONTENT",
        "LEAKSITE_CONTENT", "DARKNET_MENTION_CONTENT", "DOMAIN_WHOIS", "NETBLOCK_WHOIS",
        "AFFILIATE_DOMAIN_WHOIS", "CO_HOSTED_SITE_DOMAIN_WHOIS", "SIMILARDOMAIN_WHOIS",
        "PGP_KEY", "HASH", "HASH_COMPROMISED", "ERROR_MESSAGE"
    }

    def supported_event_types(self):
        return sorted(
            self.URLISH_TYPES | self.IP_TYPES | self.EMAIL_TYPES | self.USERNAME_TYPES |
            self.HUMAN_TYPES | self.PHONE_TYPES | self.CRYPTO_TYPES | self.NETBLOCK_TYPES |
            self.COMPANY_TYPES | self.GEO_TYPES | self.SERVICE_TYPES | self.DATA_TYPES
        )

    def describe_support(self, event_type):
        event_type = (event_type or "").upper()
        if event_type in self.URLISH_TYPES:
            return {"mode": "especializado", "validator": "http_dns_probe", "description": "Confirma resolução DNS e resposta HTTP/HTTPS quando aplicável."}
        if event_type in self.IP_TYPES:
            return {"mode": "especializado", "validator": "ip_basic_probe", "description": "Confirma resposta em portas comuns e tenta reverso DNS."}
        if event_type in self.EMAIL_TYPES:
            return {"mode": "especializado", "validator": "email_domain_probe", "description": "Verifica integridade do e-mail e resolução do domínio associado."}
        if event_type in self.USERNAME_TYPES:
            return {"mode": "especializado", "validator": "username_sanity", "description": "Valida formato e consistência básica do username para pivô."}
        if event_type in self.HUMAN_TYPES:
            return {"mode": "especializado", "validator": "human_name_sanity", "description": "Verifica estrutura plausível de nome humano."}
        if event_type in self.PHONE_TYPES:
            return {"mode": "especializado", "validator": "phone_sanity", "description": "Valida estrutura básica do telefone em formato internacional."}
        if event_type in self.CRYPTO_TYPES:
            return {"mode": "especializado", "validator": "crypto_sanity", "description": "Valida o formato base do endereço cripto para triagem."}
        if event_type in self.NETBLOCK_TYPES:
            return {"mode": "especializado", "validator": "netblock_sanity", "description": "Confirma CIDR, tamanho do bloco e capacidade operacional."}
        if event_type in self.COMPANY_TYPES:
            return {"mode": "especializado", "validator": "organization_sanity", "description": "Verifica consistência textual para entidades organizacionais."}
        if event_type in self.GEO_TYPES:
            return {"mode": "especializado", "validator": "geo_sanity", "description": "Valida coerência mínima de achados geográficos."}
        if event_type in self.SERVICE_TYPES:
            return {"mode": "especializado", "validator": "service_indicator_sanity", "description": "Valida presença e consistência de indicadores técnicos de serviço."}
        if event_type in self.DATA_TYPES:
            return {"mode": "observacional", "validator": "data_capture_review", "description": "Registra preview e orienta revisão técnica manual."}
        return {"mode": "fallback", "validator": "generic_observation", "description": "Ainda sem validador específico; aplica triagem genérica segura."}

    def validate(self, event_type, event_data):
        event_type = (event_type or "").upper()
        event_data = (event_data or "").strip()

        if not event_data:
            return {
                "validator": "sem_dados",
                "status": "error",
                "summary": "O achado não possui dados suficientes para validação.",
                "details": "O valor do achado está vazio."
            }

        if event_type in self.IP_TYPES:
            return self._validate_ip(event_type, event_data)
        if event_type in self.URLISH_TYPES:
            return self._validate_urlish(event_type, event_data)
        if event_type in self.EMAIL_TYPES:
            return self._validate_email(event_type, event_data)
        if event_type in self.USERNAME_TYPES:
            return self._validate_username(event_type, event_data)
        if event_type in self.HUMAN_TYPES:
            return self._validate_human(event_type, event_data)
        if event_type in self.PHONE_TYPES:
            return self._validate_phone(event_type, event_data)
        if event_type in self.CRYPTO_TYPES:
            return self._validate_crypto(event_type, event_data)
        if event_type in self.NETBLOCK_TYPES:
            return self._validate_netblock(event_type, event_data)
        if event_type in self.COMPANY_TYPES:
            return self._validate_organization(event_type, event_data)
        if event_type in self.GEO_TYPES:
            return self._validate_geo(event_type, event_data)
        if event_type in self.SERVICE_TYPES:
            return self._validate_service_indicator(event_type, event_data)
        if event_type in self.DATA_TYPES:
            return self._validate_data_capture(event_type, event_data)
        return self._generic_validation(event_type, event_data)

    def _http_probe(self, target, timeout=4.0):
        candidate_urls = []
        if re.match(r"^https?://", target, re.IGNORECASE):
            candidate_urls.append(target)
        else:
            candidate_urls.extend([f"https://{target}", f"http://{target}"])

        last_error = None
        for url in candidate_urls:
            req = urllib.request.Request(url, method="GET", headers={"User-Agent": "SpiderFoot-Validation/1.0"})
            try:
                with urllib.request.urlopen(req, timeout=timeout, context=ssl.create_default_context()) as response:
                    return {
                        "status": "ok",
                        "url": url,
                        "code": getattr(response, "status", response.getcode()),
                        "server": response.headers.get("Server", ""),
                        "content_type": response.headers.get("Content-Type", "")
                    }
            except Exception as e:
                last_error = str(e)
        return {"status": "error", "error": last_error or "Não foi possível consultar o alvo via HTTP/HTTPS."}

    def _tcp_probe(self, host, ports, timeout=1.5):
        findings = []
        for port in ports:
            sock = socket.socket(socket.AF_INET6 if ":" in host else socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            try:
                sock.connect((host, port))
                findings.append(port)
            except Exception:
                pass
            finally:
                sock.close()
        return findings

    def _json_result(self, validator, status, summary, details_obj):
        return {
            "validator": validator,
            "status": status,
            "summary": summary,
            "details": json.dumps(details_obj, ensure_ascii=False, indent=2) if not isinstance(details_obj, str) else details_obj
        }

    def _extract_target(self, event_data):
        cleaned = re.sub(r"</?sfurl>", "", event_data or "", flags=re.IGNORECASE).strip()
        match = re.search(r"https?://[^\s>]+", cleaned, re.IGNORECASE)
        if match:
            return match.group(0).rstrip(".,);]'\">")
        return cleaned.split()[0].rstrip(".,);]'\">") if cleaned.split() else ""

    def _validate_ip(self, event_type, event_data):
        open_ports = self._tcp_probe(event_data, [21, 22, 25, 53, 80, 110, 143, 443, 445, 8080, 8443])
        reverse_name = ""
        try:
            reverse_name = socket.gethostbyaddr(event_data)[0]
        except Exception:
            reverse_name = ""
        return self._json_result(
            "ip_basic_probe",
            "ok" if open_ports or reverse_name else "warning",
            "IP respondeu em portas comuns ou possui reverso DNS." if open_ports or reverse_name else "IP sem resposta conclusiva nas verificações seguras.",
            {"event_type": event_type, "ip": event_data, "reverse_dns": reverse_name, "open_ports": open_ports}
        )

    def _validate_urlish(self, event_type, event_data):
        probe_target = self._extract_target(event_data)
        http_result = self._http_probe(probe_target)
        host = urllib.parse.urlparse(probe_target).hostname if re.match(r"^https?://", probe_target, re.IGNORECASE) else probe_target
        dns_records = []
        try:
            dns_records = sorted({item[4][0] for item in socket.getaddrinfo(host, None)})
        except Exception:
            dns_records = []
        ok = http_result.get("status") == "ok" or bool(dns_records)
        return self._json_result(
            "http_dns_probe",
            "ok" if ok else "warning",
            "Hostname/URL validado com resposta observável." if ok else "Sem resposta conclusiva para hostname/URL.",
            {"event_type": event_type, "target": probe_target, "dns": dns_records, "http": http_result}
        )

    def _validate_email(self, event_type, event_data):
        if "@" not in event_data:
            return self._json_result("email_domain_probe", "error", "E-mail malformado.", {"event_type": event_type, "email": event_data})
        domain = event_data.split("@", 1)[1]
        resolution = []
        try:
            resolution = sorted({item[4][0] for item in socket.getaddrinfo(domain, 25)})
        except Exception:
            resolution = []
        return self._json_result(
            "email_domain_probe",
            "ok" if resolution else "warning",
            "Domínio do e-mail possui resolução." if resolution else "Não foi possível confirmar resolução do domínio do e-mail.",
            {"event_type": event_type, "email": event_data, "domain": domain, "resolution": resolution}
        )

    def _validate_username(self, event_type, event_data):
        looks_valid = bool(re.match(r"^[A-Za-z0-9_.-]{3,64}$", event_data))
        return self._json_result(
            "username_sanity",
            "ok" if looks_valid else "warning",
            "Username possui formato consistente para pivô." if looks_valid else "Username com formato incomum.",
            {"event_type": event_type, "username": event_data, "format_valid": looks_valid}
        )

    def _validate_human(self, event_type, event_data):
        looks_valid = len(event_data.split()) >= 2
        return self._json_result(
            "human_name_sanity",
            "ok" if looks_valid else "warning",
            "Nome humano com formato plausível." if looks_valid else "Nome pouco conclusivo para validação automática.",
            {"event_type": event_type, "name": event_data, "word_count": len(event_data.split())}
        )

    def _validate_phone(self, event_type, event_data):
        looks_valid = bool(re.match(r"^\+?[0-9][0-9\s().-]{6,}$", event_data))
        return self._json_result(
            "phone_sanity",
            "ok" if looks_valid else "warning",
            "Telefone com estrutura plausível." if looks_valid else "Telefone com formato incomum.",
            {"event_type": event_type, "phone": event_data, "format_valid": looks_valid}
        )

    def _validate_crypto(self, event_type, event_data):
        valid = False
        if event_type == "BITCOIN_ADDRESS":
            valid = bool(re.match(r"^(bc1|[13])[a-zA-HJ-NP-Z0-9]{20,}$", event_data, re.IGNORECASE))
        if event_type == "ETHEREUM_ADDRESS":
            valid = bool(re.match(r"^0x[a-fA-F0-9]{40}$", event_data))
        return self._json_result(
            "crypto_sanity",
            "ok" if valid else "warning",
            "Endereço cripto com formato consistente." if valid else "Endereço cripto com formato incomum.",
            {"event_type": event_type, "address": event_data, "format_valid": valid}
        )

    def _validate_netblock(self, event_type, event_data):
        try:
            network = ipaddress.ip_network(event_data, strict=False)
            return self._json_result(
                "netblock_sanity",
                "ok",
                "Bloco de rede válido para expansão e análise.",
                {"event_type": event_type, "network": str(network), "version": network.version, "num_addresses": network.num_addresses}
            )
        except Exception as e:
            return self._json_result("netblock_sanity", "error", "Bloco de rede inválido.", {"event_type": event_type, "value": event_data, "error": str(e)})

    def _validate_organization(self, event_type, event_data):
        looks_valid = len(event_data.strip()) >= 3
        return self._json_result(
            "organization_sanity",
            "ok" if looks_valid else "warning",
            "Entidade organizacional com texto consistente." if looks_valid else "Texto insuficiente para uma entidade organizacional.",
            {"event_type": event_type, "value": event_data, "length": len(event_data.strip())}
        )

    def _validate_geo(self, event_type, event_data):
        looks_valid = len(event_data.strip()) >= 2
        return self._json_result(
            "geo_sanity",
            "ok" if looks_valid else "warning",
            "Achado geográfico com estrutura básica válida." if looks_valid else "Achado geográfico pouco conclusivo.",
            {"event_type": event_type, "value": event_data}
        )

    def _validate_service_indicator(self, event_type, event_data):
        looks_valid = len(event_data.strip()) >= 1
        return self._json_result(
            "service_indicator_sanity",
            "ok" if looks_valid else "warning",
            "Indicador técnico presente e utilizável na análise." if looks_valid else "Indicador técnico vazio ou inconsistente.",
            {"event_type": event_type, "value": event_data}
        )

    def _validate_data_capture(self, event_type, event_data):
        preview = event_data[:500]
        return self._json_result(
            "data_capture_review",
            "warning",
            "Achado do tipo dado bruto registrado para revisão técnica assistida.",
            {"event_type": event_type, "preview": preview, "length": len(event_data)}
        )

    def _generic_validation(self, event_type, event_data):
        return self._json_result(
            "generic_observation",
            "warning",
            "Ainda não há um validador específico para este tipo de achado.",
            {"event_type": event_type, "event_data": event_data}
        )
