"""Registry for local AI capabilities used by SpiderFoot Core-Ops.

This module is intentionally lightweight. It defines the first local AI
capability map so the platform can evolve around explicit components instead
of a single monolithic "AI" flag.
"""


class LocalAiRegistry:
    """Describe the local AI engines supported by the platform."""

    @staticmethod
    def ollama_defaults() -> dict:
        return {
            "provider": "ollama",
            "mode": "local",
            "roles": [
                "summarization",
                "assisted correlation",
                "pivot suggestions",
                "verdict drafting",
                "embedding generation",
            ],
        }

    @staticmethod
    def local_engines() -> list:
        return [
            {
                "id": "triage_classifier",
                "name": "Classificador de triagem",
                "family": "decision_tree_or_boosting",
                "purpose": "Classificar relevancia, ruído e falso positivo.",
            },
            {
                "id": "finding_ranker",
                "name": "Ranqueador de prioridades",
                "family": "ranking_model",
                "purpose": "Ordenar achados e proximos passos por impacto e custo operacional.",
            },
            {
                "id": "change_detector",
                "name": "Detector de mudancas",
                "family": "anomaly_detection",
                "purpose": "Identificar exposicoes novas, drift e alteracoes relevantes entre scans.",
            },
            {
                "id": "graph_correlator",
                "name": "Correlacionador de grafo",
                "family": "graph_analytics",
                "purpose": "Sugerir pivôs investigativos e relacionamentos provaveis entre entidades.",
            },
            {
                "id": "operator_memory",
                "name": "Memoria operacional",
                "family": "incremental_learning",
                "purpose": "Aprender com classificacoes, validacoes e vereditos do analista.",
            },
        ]
