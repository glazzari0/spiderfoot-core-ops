# SpiderFoot Core-Ops

Plataforma customizada baseada no SpiderFoot, evoluída para uso operacional individual em:

- OSINT
- análise defensiva
- validação técnica
- auditoria
- investigação
- apoio a pentest
- triagem e conclusão de achados

O objetivo deste fork é transformar o SpiderFoot em uma ferramenta de operação contínua para um profissional de segurança, funcionando como:

- catálogo vivo de ativos externos
- plataforma de pivô investigativo
- motor de correlação
- repositório de evidências
- central de monitoramento contínuo

## O que muda neste fork

Além do comportamento original do SpiderFoot, este fork adiciona uma camada operacional orientada a fluxo de trabalho.

Principais customizações:

- interface traduzida para português do Brasil
- tema claro/escuro modernizado
- nova aba `GeoIP` para trabalhar com datasets GeoLite
- expansão controlada de blocos CIDR em IPs individuais
- presets de varredura por objetivo operacional
- bloqueio visual e lógico de módulos que exigem API obrigatória sem configuração
- normalização de seeds como `USERNAME` e `HUMAN_NAME` sem obrigar aspas manuais
- progresso operacional de execução da varredura
- grafo investigativo aprimorado
- gestão de achados com:
  - triagem
  - relevância
  - explorabilidade
  - veredito do analista
  - notas
  - evidências
  - validações
- veredito final por varredura/caso
- base extensível de validadores por tipo de achado

## Documentação

Esse documento cobre:

- arquitetura do sistema
- fluxo operacional atual
- mudanças no backend
- mudanças na interface
- banco de dados operacional
- validadores
- GeoIP
- gestão de achados
- evolução planejada

## Estrutura principal

Arquivos e áreas mais importantes deste fork:

- [sfwebui.py](sfwebui.py)
- [spiderfoot/db.py](spiderfoot/db.py)
- [spiderfoot/helpers.py](spiderfoot/helpers.py)
- [spiderfoot/geolite.py](spiderfoot/geolite.py)
- [spiderfoot/validators.py](spiderfoot/validators.py)
- [spiderfoot/templates/newscan.tmpl](spiderfoot/templates/newscan.tmpl)
- [spiderfoot/templates/geoip.tmpl](spiderfoot/templates/geoip.tmpl)
- [spiderfoot/templates/scaninfo.tmpl](spiderfoot/templates/scaninfo.tmpl)
- [spiderfoot/static/js/spiderfoot.geoip.js](spiderfoot/static/js/spiderfoot.geoip.js)
- [spiderfoot/static/js/spiderfoot.newscan.js](spiderfoot/static/js/spiderfoot.newscan.js)
- [spiderfoot/static/css/spiderfoot.css](spiderfoot/static/css/spiderfoot.css)
- [spiderfoot/static/css/dark.css](spiderfoot/static/css/dark.css)

## Requisitos

- Python 3
- ambiente virtual local
- dependências de `requirements.txt`

## Execução local

No Windows, com `venv` já criado:

```powershell
venv\Scripts\activate
python .\sf.py -l 127.0.0.1:5001
```

Ou usando o launcher:

```powershell
.\start_spiderfoot.bat
```

