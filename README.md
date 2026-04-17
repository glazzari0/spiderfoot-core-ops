# Documentação do Sistema Customizado SpiderFoot

## 1. Objetivo deste documento

Este documento descreve o estado atual do SpiderFoot customizado neste repositório, com foco em:

- arquitetura geral da solução
- fluxo operacional atual
- customizações implementadas
- comportamento das telas e do backend
- novas capacidades adicionadas ao produto original
- direção operacional do sistema como plataforma individual de segurança

Este arquivo existe para documentar a versão customizada usada neste ambiente e deve refletir o comportamento real do projeto.

---

## 2. Visão geral do sistema

O sistema deixou de ser apenas uma interface padrão do SpiderFoot voltada a OSINT e passou a evoluir para uma plataforma unificada de apoio a:

- descoberta e enumeração
- triagem e classificação de achados
- validação técnica assistida
- evidência e conclusão analítica
- acompanhamento contínuo de ativos externos
- uso defensivo, ofensivo, auditoria, forense e investigação

A visão operacional atual do sistema é:

- catálogo vivo de ativos externos
- plataforma de pivô investigativo
- motor de correlação
- repositório de evidências
- central de monitoramento contínuo

O uso previsto é individual, ou seja, o sistema foi direcionado para um único operador com múltiplas funções, e não para colaboração multiusuário.

---

## 3. Base tecnológica

O sistema continua baseado no SpiderFoot original, mas com expansão significativa.

### Backend principal

- `Python`
- `CherryPy`
- `SQLite`
- `Mako Templates`

### Frontend principal

- templates `.tmpl`
- JavaScript próprio do projeto
- Bootstrap legado com modernização visual progressiva
- Sigma.js para visualização de grafos

### Banco de dados

O SQLite segue sendo o backend principal, mas agora também armazena dados operacionais adicionais de:

- estado de triagem dos achados
- evidências
- execuções de validação
- veredito final do caso
- sessões operacionais de validação
- resultados de correlação

---

## 4. Estrutura funcional atual

Atualmente o sistema pode ser entendido em 8 blocos principais:

1. criação de varreduras
2. GeoIP / expansão de blocos CIDR
3. navegação e análise dos achados
4. correlação e grafo
5. configuração e presets
6. verificação de disponibilidade de módulos por API
7. gestão operacional de achados
8. tema, layout e tradução da interface

---

## 5. Componentes customizados principais

## 5.1. GeoIP integrado ao portal

Foi criada uma nova área `GeoIP` na interface web, com objetivo de trabalhar com os arquivos GeoLite de forma operacional.

### Arquivos principais

- [sfwebui.py](sfwebui.py)
- [spiderfoot/geolite.py](spiderfoot/geolite.py)
- [spiderfoot/templates/geoip.tmpl](spiderfoot/templates/geoip.tmpl)
- [spiderfoot/static/js/spiderfoot.geoip.js](spiderfoot/static/js/spiderfoot.geoip.js)
- [spiderfoot/templates/HEADER.tmpl](spiderfoot/templates/HEADER.tmpl)

### O que essa área faz

- detecta datasets GeoLite na pasta `Geolite` e subpastas
- permite selecionar arquivos de:
  - `ASN Blocks`
  - `City Locations`
  - `Country Locations`
  - `City Blocks`
- cruza informações de ASN, cidade e país
- aplica filtros antes da expansão
- pagina a pré-visualização
- expande networks filtradas
- dispara uma varredura por IP individual no SpiderFoot

### Fluxo atual de uso do GeoIP

1. selecionar `ASN Blocks`, `City Locations` e `Country Locations`
2. informar filtros para reduzir o universo de dados
3. selecionar o arquivo `City Blocks`
4. expandir as networks filtradas
5. escolher o que será disparado
6. iniciar as varreduras por IP

### Proteções implementadas

- bloqueio da expansão sem arquivos de referência essenciais
- bloqueio da expansão sem filtro, para evitar travamento com arquivos muito grandes
- paginação da tabela
- organização visual da tela na ordem:
  - `Arquivos GeoLite`
  - `Filtros e Pré-visualização`
  - `Tabela com paginação`
  - `Disparo de Scans`

---

## 5.2. Script de disparo por IP a partir de CSV

Antes da integração ao portal, foi criado um script operacional para disparar scans por IP a partir de blocos CIDR.

### Arquivo

- [Geolite/disparar_scans_por_ip.py](Geolite/disparar_scans_por_ip.py)

### Função

- ler o CSV filtrado do GeoLite
- expandir um bloco CIDR em IPs individuais
- montar `Scan Name`
- disparar uma varredura para cada IP

### Regras de nomenclatura

O nome do scan pode usar:

- IP
- ASN
- organização

### Ajustes feitos

- correção do caminho do CSV quando o script é executado dentro da própria pasta `Geolite`
- suporte a `dry-run`
- suporte a filtros de quantidade

---

## 5.3. Presets de varredura

Foi adicionada uma nova forma de iniciar varreduras por objetivo operacional.

### Arquivos principais

- [sfwebui.py](sfwebui.py)
- [spiderfoot/templates/newscan.tmpl](spiderfoot/templates/newscan.tmpl)
- [spiderfoot/static/js/spiderfoot.newscan.js](spiderfoot/static/js/spiderfoot.newscan.js)

### Presets implementados

- `Domínio Passivo Sem Custo`
- `Domínio Investigação Balanceada`
- `IP/Sub-rede Passivo Sem Custo`
- `Identidade e Vazamentos Sem Custo`

### O que os presets resolvem

- reduzem erro operacional
- evitam ligar módulos inadequados
- facilitam o uso por objetivo
- priorizam módulos gratuitos, nativos ou sem custo

### Segurança aplicada

- validação de compatibilidade entre preset e tipo de alvo
- o sistema impede uso de preset incompatível com o seed informado

---

## 5.4. Verificação de módulos que dependem de API

Foi criada uma lógica para analisar a configuração atual carregada pelo SpiderFoot e refletir isso no portal.

### Objetivo

Evitar habilitação de módulos que dependem de API obrigatória sem chave configurada.

### Onde foi aplicado

- aba `Por Dados Necessários`
- aba `Por Módulo`

### Comportamento atual

- módulo com API obrigatória não configurada fica indisponível
- o backend também rejeita ativações forçadas
- módulos com API opcional continuam disponíveis

### Ajustes adicionais

- link para configuração do módulo
- navegação via `opts?module=sfp_xxx`
- engrenagem ao lado do nome do módulo
- na aba `Por Dados Necessários`, redução de poluição visual com agrupamento mais confortável

---

## 5.5. Normalização de alvos com aspas

Foi implementada lógica para reduzir erro de entrada quando o usuário esquece aspas em seeds como:

- `HUMAN_NAME`
- `USERNAME`

### Onde foi aplicado

- criação de nova varredura
- reexecução de varreduras já concluídas

### Comportamento

- `John Smith` pode ser normalizado como `"John Smith"`
- `giovani_silva` pode ser normalizado como `"giovani_silva"`

### Arquivo principal

- [sfwebui.py](sfwebui.py)

---

## 5.6. Tradução da interface para português do Brasil

Foi feita uma tradução ampla da interface web, com padronização de textos operacionais em PT-BR e correções de encoding em telas críticas.

### Áreas traduzidas

- navegação superior
- nova varredura
- scan list
- logs
- configurações
- GeoIP
- dashboard de varredura
- grande parte das mensagens e descrições da UI

### Ajustes recentes de encoding e renderização

- normalização de textos UTF-8 em templates principais
- correção de trechos com mojibake em `scaninfo.tmpl`
- correção do estado vazio de `Varreduras`
- reforço de compatibilidade em JavaScript estático para evitar regressão de acentuação no navegador

### Observação

Ainda podem existir alguns textos em inglês vindos de descrições internas de módulos e estruturas originais do SpiderFoot.

### Arquivos impactados

- [spiderfoot/templates/HEADER.tmpl](spiderfoot/templates/HEADER.tmpl)
- [spiderfoot/templates/scanlist.tmpl](spiderfoot/templates/scanlist.tmpl)
- [spiderfoot/templates/newscan.tmpl](spiderfoot/templates/newscan.tmpl)
- [spiderfoot/templates/opts.tmpl](spiderfoot/templates/opts.tmpl)
- [spiderfoot/templates/scaninfo.tmpl](spiderfoot/templates/scaninfo.tmpl)
- [spiderfoot/templates/error.tmpl](spiderfoot/templates/error.tmpl)
- [spiderfoot/templates/FOOTER.tmpl](spiderfoot/templates/FOOTER.tmpl)
- [spiderfoot/static/js/spiderfoot.js](spiderfoot/static/js/spiderfoot.js)
- [spiderfoot/static/js/spiderfoot.scanlist.js](spiderfoot/static/js/spiderfoot.scanlist.js)
- [spiderfoot/templates/geoip.tmpl](spiderfoot/templates/geoip.tmpl)

---

## 5.7. Modernização visual da interface

O layout padrão foi progressivamente modernizado.

### Objetivos

- tornar a interface menos poluída
- reduzir tabelas quadradas e antigas
- melhorar ergonomia em telas de análise
- criar uma experiência mais informativa e menos textual

### Arquivos principais

- [spiderfoot/static/css/spiderfoot.css](spiderfoot/static/css/spiderfoot.css)
- [spiderfoot/static/css/dark.css](spiderfoot/static/css/dark.css)
- [spiderfoot/templates/scanlist.tmpl](spiderfoot/templates/scanlist.tmpl)
- [spiderfoot/templates/scaninfo.tmpl](spiderfoot/templates/scaninfo.tmpl)

### Melhorias visuais feitas

- superfícies com tons mais coerentes
- bordas mais suaves
- tabelas menos agressivas
- contêineres arredondados
- `sf-table-shell` para conter tabelas com acabamento melhor
- melhorias específicas em:
  - `Nova Varredura`
  - `Varreduras`
  - `Configurações`
  - `Configurações da Varredura`
  - `GeoIP`
  - `Dashboard da Varredura`

### Ajustes pontuais importantes

- correção de inconsistências visuais entre áreas da interface
- compactação visual da tela de `Varreduras`
- substituição de blocos extensos de texto por painéis mais curtos e operacionais

---

## 5.8. Painel operacional e dashboard da varredura

Foi adicionado um painel de acompanhamento do andamento da varredura e a tela de `scaninfo` passou a funcionar como um dashboard operacional.

### Objetivo

Dar ao operador uma noção operacional de:

- progresso estimado
- módulos ativos
- módulos pendentes
- fila de eventos
- último sinal observável do pipeline
- inventário resumido por módulo
- situação geral de triagem, evidências e validações

### Arquivos principais

- [sfwebui.py](sfwebui.py)
- [sfscan.py](sfscan.py)
- [spiderfoot/templates/scaninfo.tmpl](spiderfoot/templates/scaninfo.tmpl)

### Evoluções recentes

- criação de um resumo operacional consumido pela UI via `scanprogress`
- dashboard com menos ruído visual e mais orientação analítica
- bloco `Inventário por módulo` remodelado para scans grandes
- substituição de listagens extensas por:
  - contadores compactos
  - distribuição visual por estado
  - malha de módulos
  - destaques operacionais
- exibição mais clara de módulos com saída, sem saída, erro e pendências

### Consistência de estados de execução

Foi ajustada a lógica para evitar que varreduras terminadas continuem mostrando módulos em execução.

Isso foi tratado em dois níveis:

- no backend web, que agora normaliza o status do scan e zera módulos em execução quando o estado é terminal
- no processo da varredura, que grava um snapshot terminal antes de marcar `FINISHED`

### Importante

O percentual atual é uma estimativa operacional, não uma garantia exata de conclusão do engine.

---

## 5.9. Grafo investigativo

O grafo original foi significativamente melhorado.

### Arquivos principais

- [spiderfoot/helpers.py](spiderfoot/helpers.py)
- [spiderfoot/templates/scaninfo.tmpl](spiderfoot/templates/scaninfo.tmpl)

### Melhorias feitas

- metadados por nó
- tamanho do nó por conectividade e atividade
- layout inicial mais organizado
- painel lateral `Leitura do Grafo`
- legenda explicativa por cor
- detalhes no hover e clique
- links clicáveis no painel lateral
- remoção de marcações internas como `<SFURL>`
- modos de rótulo:
  - `Auto`
  - `Todos`
  - `Ocultar`
- classificação visual adicional por heurística

### Problemas corrigidos

- nós aparecendo todos pretos
- labels vazando sobre o canvas
- tags internas aparecendo no texto
- links inválidos por `</SFURL>`
- inconsistência entre cor da legenda e cor real dos nós
- desaparecimento visual dos marcadores da legenda
- quebra de JavaScript na tela do grafo por trecho corrompido de regex

---

## 5.10. Gestão operacional de achados

Esta é uma das maiores evoluções do sistema até agora.

### Objetivo

Transformar o SpiderFoot de simples coletor de dados em uma ferramenta de:

- triagem
- classificação
- validação
- evidência
- conclusão

### Arquivos principais

- [spiderfoot/db.py](spiderfoot/db.py)
- [sfwebui.py](sfwebui.py)
- [spiderfoot/templates/scaninfo.tmpl](spiderfoot/templates/scaninfo.tmpl)
- [spiderfoot/static/css/spiderfoot.css](spiderfoot/static/css/spiderfoot.css)

### Novas tabelas SQLite

- `tbl_scan_finding_state`
- `tbl_scan_finding_evidence`
- `tbl_scan_validation_run`
- `tbl_scan_case_verdict`
- `tbl_agent_session`
- `tbl_agent_session_step`

### O que passou a existir

#### No nível do achado

- status de triagem
- relevância
- explorabilidade
- veredito do analista
- notas do analista
- evidências anexadas
- histórico de validações

#### No nível do caso/varredura

- veredito final
- conclusão resumida
- contagem operacional de evidências
- contagem de validações

### Estados e classificações atuais

#### Triagem

- `novo`
- `em_triagem`
- `relevante`
- `descartado`
- `falso_positivo`
- `confirmado`

#### Relevância

- `pendente`
- `baixa`
- `media`
- `alta`
- `critica`

#### Explorabilidade

- `nao_avaliado`
- `nao_aplicavel`
- `nao_exploravel`
- `potencial`
- `confirmada`

#### Veredito do achado / caso

- `em_analise`
- `monitorar`
- `sem_risco_pratico`
- `exposto_confirmado`
- `exploravel`
- `critico`

---

## 5.11. Validadores de achados

Foi criada uma base extensível de validadores.

### Arquivo principal

- [spiderfoot/validators.py](spiderfoot/validators.py)

### Objetivo

Permitir que praticamente todo tipo relevante de achado possa passar por:

- triagem técnica segura
- checagem de consistência
- validação assistida
- produção de evidência inicial

### Modelo adotado

Foi criado um `engine` de validadores, com:

- suporte declarado por tipo
- descrição do validador usado
- separação por família de achados
- fallback genérico para o que ainda não tiver regra especializada

### Famílias atualmente cobertas

- IPs
- hostnames / domínios / URLs / social / contas externas / repositórios
- e-mails
- usernames
- nomes humanos
- telefones
- endereços cripto
- blocos de rede
- organizações / ASN
- geolocalização
- indicadores de serviço
- dados brutos observacionais

### Situação atual

O sistema já possui uma base ampla para expansão e um número inicial grande de tipos suportados por família. A meta futura é ampliar o nível de profundidade dos validadores especializados, principalmente para:

- takeover
- buckets
- TLS
- banners
- portas
- certificados
- leaks
- vulnerabilidades
- indicadores de exposição real

---

## 5.12. Security Loop de validação

Foi adicionado um núcleo inicial de orquestração inspirado no conceito de loop de agente, mas implementado integralmente no padrão Python do SpiderFoot.

### Arquivos principais

- [spiderfoot/agent.py](spiderfoot/agent.py)
- [spiderfoot/db.py](spiderfoot/db.py)
- [sfwebui.py](sfwebui.py)

### Objetivo

Evoluir a validação de achados de um passo único para uma sessão curta com:

- plano de validação
- memória de sessão
- deduplicação de etapas recentes
- execução observacional segura
- persistência de evidência resumida

### Componentes

#### `SecurityValidationLoop`

Orquestra o ciclo:

- observar o achado
- montar um plano curto
- executar ferramentas seguras
- consolidar a validação final
- registrar sessão, passos, validação e evidência

#### `ValidationPlanBuilder`

Responsável por decidir a ordem e a prioridade do plano com base em:

- risco do achado
- estado de triagem
- histórico de validações
- presença de evidências
- correlações associadas ao finding

#### `SecurityToolExecutor`

Executa o conjunto inicial de ferramentas seguras:

- `dns_lookup`
- `http_probe`
- `reverse_dns`
- `tcp_common`
- `email_domain_resolution`
- `final_validation`

### Persistência

#### `tbl_agent_session`

Armazena:

- tipo do agente
- status da sessão
- resumo final
- plano serializado
- timestamps

#### `tbl_agent_session_step`

Armazena:

- ordem da etapa
- ferramenta usada
- ação planejada
- status
- observação serializada

### Fluxo atual

Ao acionar `findingvalidate`, o SpiderFoot agora:

1. carrega o contexto do achado
2. carrega correlações associadas ao achado
3. consulta a sessão anterior mais recente para evitar repetições triviais
4. monta um plano compatível com o tipo do achado e com a prioridade calculada
5. ordena a validação com base em triagem, risco e correlações
6. executa probes seguros por etapa
7. roda o validador consolidado do SpiderFoot
8. registra a sessão no banco
9. grava uma evidência textual resumindo o que aconteceu

### Estado atual e limites

Este núcleo foi desenhado para triagem e validação técnica segura. Ele:

- não reutiliza código externo ao projeto
- permanece observacional e conservador
- usa o banco SQLite do SpiderFoot como trilha de auditoria

### Próximos passos naturais

- planejar etapas com mais contexto de correlação
- ampliar o catálogo de ferramentas seguras por família de achado
- usar IA local apenas para priorização e sumarização do plano
- expor a sessão do agente de forma mais detalhada na interface

---

## 5.13. Correlações expandidas

O motor de correlação passou a cobrir melhor cenários operacionais que antes ficavam com pouco ou nenhum resultado, principalmente scans focados em IP, identidade, vazamentos e footprint público.

### Arquivos principais

- [correlations](correlations)
- [sf.py](sf.py)
- [spiderfoot/correlation.py](spiderfoot/correlation.py)

### Direção adotada

Em vez de criar regras para todo tipo de evento isolado, a expansão foi organizada por famílias analíticas:

- IP e superfície exposta
- domínio e hostname
- identidade pessoal
- vazamentos e leak sites
- perfis sociais, contas externas e repositórios públicos

### Cobertura adicionada

#### IP e infraestrutura

- confirmação de `AFFILIATE_IPADDR` por múltiplos módulos
- destaque para superfícies grandes de IP afiliado
- diferenciação de achados encontrados apenas por `dnsneighbor`
- portas abertas e múltiplas portas no mesmo IP afiliado
- stack de software associada a IP afiliado
- confirmação de hostname afiliado e `NETBLOCK_MEMBER` por múltiplos módulos

#### Identidade pessoal

- e-mail ou telefone comprometido e também marcado como malicioso
- e-mail ligado a múltiplos sinais de identidade
- username reutilizado em múltiplas contas externas
- nomes, usernames e telefones confirmados por mais de uma fonte
- presença social ou de conta externa confirmada por múltiplos módulos

#### Vazamentos e leak sites

- URL de leak site confirmada por mais de um módulo
- menções darknet confirmadas por múltiplas fontes
- conteúdo de leak ou darknet com múltiplos tipos de identidade
- usernames encontrados apenas em contexto darknet
- identidade comprometida também ligada a artefatos de leak ou darknet

#### Perfis sociais e code repos

- repositórios públicos confirmados por mais de um módulo
- múltiplos repositórios públicos ligados à mesma identidade
- identidade com presença social e também presença em código público
- username espalhado entre social, contas externas e repositórios

### Resultado esperado

O sistema continua dependente da qualidade dos dados coletados pelo scan, mas agora oferece uma camada analítica mais útil para:

- scans de IP e netblock
- investigações de identidade
- casos com vazamentos
- footprint público de usuários e organizações

---

## 5.14. Lista de varreduras e experiência operacional

A tela de `Varreduras` foi ajustada para preservar melhor o contexto do operador durante o uso.

### Arquivos principais

- [spiderfoot/static/js/spiderfoot.js](spiderfoot/static/js/spiderfoot.js)
- [spiderfoot/static/js/spiderfoot.scanlist.js](spiderfoot/static/js/spiderfoot.scanlist.js)
- [spiderfoot/templates/scanlist.tmpl](spiderfoot/templates/scanlist.tmpl)

### Melhorias recentes

- remoção imediata de scans excluídos sem refresh completo da página
- preservação do contexto visual ao excluir itens
- renderização de estado vazio sem recarregar a tela inteira
- correção do texto do estado vazio em português do Brasil

### Benefício operacional

O operador consegue acompanhar uma operação em andamento, excluir scans finalizados e manter o contexto visual da lista sem perder filtros ou precisar reiniciar a leitura da tela.

---

## 5.15. Reanálise assistida por IA

Foi adicionada uma camada de planejamento assistido por IA para orientar uma nova execução da varredura sem retirar o controle final do operador.

### Objetivo

Usar IA local com Ollama para:

- avaliar a cobertura do scan já concluído
- sugerir módulos adicionais realmente úteis
- sugerir remoção de módulos redundantes ou ruidosos
- orientar as próximas etapas antes de uma reexecução
- manter a decisão final e o ajuste fino nas mãos do operador

### Arquivos principais

- [sfwebui.py](sfwebui.py)
- [spiderfoot/ai/assistant.py](spiderfoot/ai/assistant.py)
- [spiderfoot/ai/ollama_client.py](spiderfoot/ai/ollama_client.py)
- [spiderfoot/templates/scaninfo.tmpl](spiderfoot/templates/scaninfo.tmpl)
- [spiderfoot/templates/newscan.tmpl](spiderfoot/templates/newscan.tmpl)

### Como o fluxo funciona

1. o operador solicita o plano de reanálise no dashboard da varredura
2. o sistema monta um contexto com:
   - status do scan
   - cobertura por tipos de evento
   - correlações encontradas
   - resumo operacional
   - memória operacional da varredura
   - módulos já ativos
   - módulos disponíveis e indisponíveis
3. o Ollama analisa esse contexto
4. a UI apresenta:
   - leitura de cobertura
   - módulos sugeridos para adicionar
   - módulos sugeridos para remover
   - etapas sugeridas
   - evidências a revisar antes da reexecução
   - orientação de decisão
5. o operador abre a tela `Nova Varredura` já pré-preenchida com a seleção sugerida
6. o operador revisa, ajusta e só então executa a nova varredura

### Características importantes

- não há reexecução automática cega
- a IA não substitui a decisão final do analista
- a sugestão vem acompanhada de racional e leitura de cobertura
- a nova varredura continua totalmente editável antes da execução

### Timeout e comportamento do Ollama

O planner de reanálise pode exigir mais tempo que a análise assistida de um único achado, especialmente com modelos maiores. Por isso:

- o fluxo de reanálise aceita timeout próprio
- se esse timeout específico não estiver configurado, usa o timeout geral do Ollama
- foi adotado um piso mínimo mais alto para evitar falhas prematuras enquanto o modelo ainda está carregando e processando o contexto

---

## 6. Fluxo operacional atual

## 6.1. Fluxo de uma operação padrão

### Etapa 1. Escolha do objetivo

O operador decide o tipo de missão:

- descoberta
- investigação
- validação
- auditoria
- pentest
- análise defensiva
- OSINT

### Etapa 2. Criação da varredura

Pode ser feita por:

- `Caso de Uso`
- `Preset`
- `Por Dados Necessários`
- `Por Módulo`
- `GeoIP`

### Etapa 3. Coleta

O sistema dispara módulos apropriados e coleta eventos.

### Etapa 4. Acompanhamento

O operador observa:

- progresso da execução
- inventário resumido dos módulos
- logs
- correlações
- resumo da varredura

### Etapa 5. Navegação dos achados

Na aba `Navegar`, o operador:

- entra no tipo de dado
- abre a visão completa
- seleciona um achado específico

### Etapa 6. Painel de análise do achado

Ao abrir um achado, o operador pode:

- classificar
- descartar
- confirmar
- marcar como falso positivo
- definir relevância
- avaliar explorabilidade
- adicionar notas
- anexar evidências
- executar validação segura

### Etapa 7. Consolidação

No `Resumo`, o operador acompanha:

- total de achados
- correlações
- distribuição por triagem
- contagem de evidências
- contagem de validações
- veredito final da varredura

### Etapa 8. Conclusão

O operador produz um veredito final, por exemplo:

- monitorar
- sem risco prático
- exposto e confirmado
- explorável
- crítico

---

## 6.2. Fluxo específico do GeoIP

1. selecionar arquivos de referência
2. aplicar filtros para reduzir o volume
3. escolher o arquivo de blocos
4. expandir
5. pré-visualizar com paginação
6. disparar varreduras por IP
7. tratar e validar os achados gerados

---

## 6.3. Fluxo específico de análise de achados

1. abrir uma varredura
2. ir para `Navegar`
3. selecionar o tipo de dado
4. abrir a visão completa
5. clicar no botão de análise do achado
6. preencher classificação
7. rodar validação segura
8. anexar evidências
9. registrar notas
10. atualizar o veredito do caso

---

## 6.4. Fluxo específico de correlação e leitura operacional

1. concluir ou acompanhar uma varredura
2. revisar o painel `Resumo`
3. observar o inventário por módulo e o último sinal do pipeline
4. analisar correlações geradas por família de contexto
5. usar o grafo como pivô de investigação
6. descer para o detalhe dos achados quando a correlação apontar algo prioritário

---

## 7. Endpoints e lógica web adicionados

Entre os principais pontos adicionados ou alterados no backend web:

- `geoip`
- `geoipdatasets`
- `geoippreview`
- `geoipstartscans`
- `scanprogress`
- `findingdetail`
- `findingupdate`
- `findingevidenceadd`
- `findingvalidate`
- `scanopssummary`
- `scanverdictupdate`
- `scanmemoryupdate`
- `correlationrules`
- `ollamastatus`
- `scanreanalysisplan`

Também houve alteração na lógica de:

- `startscan`
- `rerunscan`
- `rerunscanmulti`
- `opts`
- `scandelete`
- `scaninfo`
- `newscan`

---

## 8. Melhorias de experiência do operador

Hoje o sistema já oferece vantagens importantes para o uso individual:

- interface em português do Brasil
- correções de UTF-8 em telas críticas
- presets com explicação
- navegação mais clara
- bloqueio de módulos inviáveis sem API
- links diretos para configuração
- lista de varreduras mais estável durante operações
- dashboard de scan mais visual e menos tabelado
- inventário compacto de módulos para scans grandes
- progresso operacional mais confiável em scans finalizados
- grafo mais legível e com legenda funcional
- correlações mais úteis para IP, identidade, vazamentos e footprint público
- memória operacional por varredura para retomada de análise
- explicabilidade prática das correlações no dashboard
- plano de reanálise assistida por IA com revisão humana antes da execução
- análise de achados no mesmo fluxo da investigação
- distinção entre coleta e conclusão analítica

---

## 9. Situação atual do projeto

O projeto hoje já opera como uma versão fortemente customizada do SpiderFoot, com foco em:

- operação individual
- observabilidade da execução
- triagem analítica
- validação segura
- redução de ruído visual
- leitura operacional dos resultados

O próximo estágio natural de evolução é aprofundar:

- priorização automática de risco
- explicabilidade das correlações na interface
- enriquecimento de validadores especializados
- maior cobertura de correlações por contexto operacional
- refinamento contínuo da UX do dashboard

---

## 10. Documentação interna relacionada

Além deste documento principal, o repositório agora possui documentação complementar para áreas específicas:

- [correlations/README.md](correlations/README.md)
  descreve a estrutura das regras de correlação e observações do pacote expandido usado neste projeto
- [spiderfoot/ai/README.md](spiderfoot/ai/README.md)
  documenta a camada local de IA com Ollama, o assistente de achados e o planner de reanálise assistida
- [test/README.md](test/README.md)
  reúne instruções de testes, incluindo os pontos mais relevantes para validar dashboard, correlações e IA local

Esses documentos devem ser mantidos alinhados com este arquivo sempre que a arquitetura operacional ou a experiência da interface forem alteradas.
