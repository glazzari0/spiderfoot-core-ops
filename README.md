# Documentação do Sistema Customizado SpiderFoot

## 1. Objetivo deste documento

Este documento descreve o estado atual do sistema SpiderFoot customizado neste repositório, com foco em:

- arquitetura geral da solução
- fluxo operacional atual
- customizações implementadas
- comportamento das telas e do backend
- novas capacidades adicionadas ao produto original
- direção operacional do sistema como plataforma individual de segurança

Este arquivo existe para documentar a versão customizada usada neste ambiente.

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

---

## 4. Estrutura funcional atual

Atualmente o sistema pode ser entendido em 8 blocos principais:

1. Criação de varreduras
2. GeoIP / expansão de blocos CIDR
3. Navegação e análise dos achados
4. Correlação e grafo
5. Configuração e presets
6. Verificação de disponibilidade de módulos por API
7. Gestão operacional de achados
8. Tema, layout e tradução da interface

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

1. Selecionar `ASN Blocks`, `City Locations` e `Country Locations`
2. Informar filtros para reduzir o universo de dados
3. Selecionar o arquivo `City Blocks`
4. Expandir as networks filtradas
5. Escolher o que será disparado
6. Iniciar as varreduras por IP

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

Foi feita uma tradução ampla da interface web.

### Áreas traduzidas

- navegação superior
- nova varredura
- scan list
- logs
- configurações
- GeoIP
- grande parte das mensagens e descrições da UI

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
- criar um modo escuro mais profissional
- melhorar ergonomia em telas de análise

### Arquivos principais

- [spiderfoot/static/css/spiderfoot.css](spiderfoot/static/css/spiderfoot.css)
- [spiderfoot/static/css/dark.css](spiderfoot/static/css/dark.css)

### Melhorias visuais feitas

- tema escuro em linha mais próxima de VS Code
- superfícies com tons de cinza coerentes
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

### Ajustes pontuais importantes

- correção de mistura entre tema claro e escuro
- correção de bordas claras vazando no dark mode
- compactação visual da tela de `Varreduras`

---

## 5.8. Progresso da execução da varredura

Foi adicionado um painel de acompanhamento do andamento da varredura.

### Objetivo

Dar ao operador uma noção operacional de:

- progresso estimado
- módulos ativos
- módulos pendentes
- fila de eventos
- último sinal observável do pipeline

### Arquivos principais

- [sfwebui.py](sfwebui.py)
- [spiderfoot/templates/scaninfo.tmpl](spiderfoot/templates/scaninfo.tmpl)

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
- tamanho do nó por conectividade/atividade
- layout inicial mais organizado
- painel lateral `Leitura do Grafo`
- legenda
- detalhes no hover/clique
- links clicáveis no painel lateral
- remoção de marcações internas como `<SFURL>`
- modos de rótulo:
  - `Auto`
  - `Todos`
  - `Ocultar`
- correção de cores dos tipos de nó
- classificação visual adicional por heurística

### Problemas corrigidos

- nós aparecendo todos pretos
- labels vazando sobre o canvas
- tags internas aparecendo no texto
- links inválidos por `</SFURL>`
- inconsistência entre cor da legenda e cor real dos nós

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
- logs
- correlações
- resumo da varredura

### Etapa 5. Navegação dos achados

Na aba `Navegar`, o operador:

- entra no tipo de dado
- abre a visão completa
- seleciona um achado específico

### Etapa 6. Painel de Análise do Achado

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

1. Selecionar arquivos de referência
2. Aplicar filtros para reduzir o volume
3. Escolher o arquivo de blocos
4. Expandir
5. Pré-visualizar com paginação
6. Disparar varreduras por IP
7. Tratar e validar os achados gerados

---

## 6.3. Fluxo específico de análise de achados

1. Abrir uma varredura
2. Ir para `Navegar`
3. Selecionar o tipo de dado
4. Abrir a visão completa
5. Clicar no botão de análise do achado
6. Preencher classificação
7. Rodar validação segura
8. Anexar evidências
9. Registrar notas
10. Atualizar o veredito do caso

---

## 7. Endpoints e lógica web adicionados

Entre os principais pontos adicionados/alterados no backend web:

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

Também houve alteração na lógica de:

- `startscan`
- `rerunscan`
- `rerunscanmulti`
- `opts`

---

## 8. Melhorias de experiência do operador

Hoje o sistema já oferece vantagens importantes para o uso individual:

- interface em português
- presets com explicação
- navegação mais clara
- bloqueio de módulos inviáveis sem API
- links diretos para configuração
- tema claro e escuro mais coerentes
- painéis mais modernos
- análise de achados no mesmo fluxo da investigação
- distinção entre coleta e conclusão analítica

---

## 9. Limitações atuais

Apesar da evolução significativa, o sistema ainda está em uma fase intermediária.

### Limitações presentes

- nem todos os tipos de achado possuem validação profunda
- ainda não existe diff entre varreduras
- ainda não existe watchlist/monitoramento recorrente completo
- ainda não existe alerta automatizado por mudança
- ainda não existe painel executivo separado do técnico
- ainda não existe exploração controlada guiada para todos os cenários
- ainda não existe exportação de dossiê investigativo completo consolidado

---

## 10. Próximas evoluções naturais

Com base no que já foi implementado, os próximos blocos de alto valor seriam:

### 10.1. Monitoramento contínuo

- watchlists
- scans agendados
- diff entre execuções
- alertas por mudança

### 10.2. Validadores avançados

- takeover
- cloud storage
- TLS/certificados
- banners e portas
- vulnerabilidades
- fingerprinting seguro

### 10.3. Evidência e conclusão

- exportação de dossiê
- snapshots técnicos
- timeline da investigação
- pacote final de conclusão

### 10.4. Pivô investigativo

- abrir nova investigação a partir de um achado
- cadeia de investigação entre scan e evidência
- histórico por entidade

---

## 11. Resumo executivo do que o sistema já se tornou

Hoje este SpiderFoot customizado já não é apenas um scanner OSINT padrão.

Ele já funciona como:

- console unificado de coleta
- painel de expansão GeoIP/ASN/City/Country
- interface de presets operacionais
- ambiente de análise de achados
- sistema de triagem
- base de validação segura
- repositório de evidências
- painel de conclusão analítica

Em outras palavras, ele já começou a se transformar em uma plataforma individual de segurança com perfil de:

- canivete suíço operacional
- laboratório de investigação
- suporte a OSINT
- suporte a auditoria
- suporte a validação técnica
- suporte a análise defensiva e ofensiva

---

## 12. Arquivos mais relevantes para manutenção futura

### Backend

- [sfwebui.py](sfwebui.py)
- [spiderfoot/db.py](spiderfoot/db.py)
- [spiderfoot/helpers.py](spiderfoot/helpers.py)
- [spiderfoot/geolite.py](spiderfoot/geolite.py)
- [spiderfoot/validators.py](spiderfoot/validators.py)

### Templates

- [spiderfoot/templates/HEADER.tmpl](spiderfoot/templates/HEADER.tmpl)
- [spiderfoot/templates/newscan.tmpl](spiderfoot/templates/newscan.tmpl)
- [spiderfoot/templates/geoip.tmpl](spiderfoot/templates/geoip.tmpl)
- [spiderfoot/templates/scaninfo.tmpl](spiderfoot/templates/scaninfo.tmpl)
- [spiderfoot/templates/opts.tmpl](spiderfoot/templates/opts.tmpl)
- [spiderfoot/templates/scanlist.tmpl](spiderfoot/templates/scanlist.tmpl)

### Frontend JS

- [spiderfoot/static/js/spiderfoot.js](spiderfoot/static/js/spiderfoot.js)
- [spiderfoot/static/js/spiderfoot.newscan.js](spiderfoot/static/js/spiderfoot.newscan.js)
- [spiderfoot/static/js/spiderfoot.geoip.js](spiderfoot/static/js/spiderfoot.geoip.js)
- [spiderfoot/static/js/spiderfoot.opts.js](spiderfoot/static/js/spiderfoot.opts.js)
- [spiderfoot/static/js/spiderfoot.scanlist.js](spiderfoot/static/js/spiderfoot.scanlist.js)

### CSS

- [spiderfoot/static/css/spiderfoot.css](spiderfoot/static/css/spiderfoot.css)
- [spiderfoot/static/css/dark.css](spiderfoot/static/css/dark.css)

### Scripts auxiliares

- [Geolite/disparar_scans_por_ip.py](Geolite/disparar_scans_por_ip.py)

---

## 13. Observação final

Este documento reflete o estado atual da customização conhecida até este momento da evolução do sistema.

Ele deve ser atualizado sempre que houver mudanças relevantes em:

- fluxo operacional
- novas áreas da interface
- modelos de validação
- estrutura do banco
- mecanismos de monitoramento
- capacidade de conclusão e evidência
