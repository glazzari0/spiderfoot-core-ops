# Camada local de IA

## Objetivo

Esta pasta concentra a camada de IA local usada pelo SpiderFoot customizado para apoiar a análise, sem retirar o controle final do operador.

O foco atual não é autonomia plena. A IA atua como apoio para:

- triagem contextual de achados
- explicação prática de decisões analíticas
- planejamento de reanálise de uma varredura concluída
- orientação operacional com base em cobertura, módulos e evidências já existentes

---

## Componentes atuais

### `ollama_client.py`

Cliente HTTP simples para integração com Ollama local.

Responsabilidades principais:

- consultar modelos disponíveis
- enviar prompts de análise
- receber respostas estruturadas em JSON
- aplicar timeout configurável
- retornar mensagens mais claras em caso de timeout

### `assistant.py`

Implementa os assistentes especializados usados pelo backend web.

Componentes principais:

- `_BaseOllamaAssistant`
  base comum de configuração, prompt e chamada ao cliente
- `FindingAiAssistant`
  voltado à análise de um achado individual
- `ScanReanalysisPlanner`
  monta um plano de reanálise a partir do contexto completo de uma varredura

### `registry.py`

Centraliza o catálogo lógico de capacidades e integrações de IA usadas pelo sistema.

### `__init__.py`

Expõe os assistentes para importação pelo restante da aplicação.

---

## Fluxo atual de uso

### 1. Assistência de achado

O backend monta um contexto contendo:

- achado selecionado
- bundle do evento
- correlações relacionadas
- evidências existentes
- memória operacional da varredura
- política de risco por ação

Esse contexto é enviado ao `FindingAiAssistant`, que devolve uma leitura assistida para o workbench do analista.

### 2. Planejamento de reanálise

O endpoint `scanreanalysisplan` monta um contexto de varredura contendo:

- seed e tipo do alvo
- status atual do scan
- cobertura operacional
- módulos ativos
- módulos disponíveis
- correlações geradas
- resumo operacional
- memória da varredura

Esse contexto é enviado ao `ScanReanalysisPlanner`, que retorna:

- leitura de cobertura
- justificativa analítica
- módulos sugeridos para adicionar
- módulos sugeridos para remover
- etapas operacionais recomendadas
- evidências ou áreas a revisar antes da nova execução
- orientação de decisão para o operador

O sistema não executa automaticamente a nova varredura. O operador revisa a proposta, ajusta o que desejar e então decide se reexecuta.

---

## Princípios de uso

- a IA não substitui o analista
- a decisão final permanece humana
- o sistema deve preferir orientar em vez de executar ações sensíveis
- qualquer sugestão deve ser explicável dentro do contexto real da varredura
- a saída precisa ser útil para operação, não apenas textual

---

## Configurações relevantes

As configurações podem variar conforme o ambiente, mas os parâmetros mais importantes para esta camada são:

- `_ai_enabled`
  habilita ou desabilita a camada de IA
- `_ai_provider`
  define o provedor atual
- `_ai_ollama_host`
  endereço do servidor Ollama
- `_ai_ollama_model`
  modelo padrão de chat
- `_ai_ollama_timeout_seconds`
  timeout geral para chamadas locais ao Ollama
- `_ai_ollama_reanalysis_timeout_seconds`
  timeout específico do planner de reanálise

Quando `_ai_ollama_reanalysis_timeout_seconds` não estiver configurado, o planner reaproveita o timeout geral, mas com piso maior para comportar análises mais pesadas.

---

## Relação com o dashboard

A camada de IA conversa diretamente com o dashboard operacional em:

- explicação assistida no workbench do achado
- resumo de ausência de cobertura na área de correlações
- plano de reanálise assistida na tela da varredura

Essas integrações foram desenhadas para funcionar em conjunto com:

- memória operacional por varredura
- correlações expandidas
- política de risco por ação
- inventário visual de módulos

---

## Boas práticas para evolução

Ao expandir esta pasta:

- manter assistentes especializados e de escopo pequeno
- evitar lógica de negócio crítica escondida dentro do prompt
- documentar todo novo endpoint que consumir a camada de IA
- manter alinhamento com [README.md](../../README.md)
- atualizar testes e documentação quando o formato das respostas mudar
