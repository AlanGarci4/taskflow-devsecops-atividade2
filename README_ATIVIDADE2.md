# Atividade 2 - DAST, IaC e Observabilidade

## Estrutura entregue
- `codigo/dast/`: app corrigida para DAST, templates e Dockerfile de pipeline.
- `codigo/iac/`: compose seguro, `.env.example` e Terraform corrigido.
- `codigo/observabilidade/`: app instrumentada + stack Loki/Grafana/Promtail.
- `.github/workflows/dast.yml`: DAST com ZAP baseline e artefato.
- `.github/workflows/iac-scan.yml`: Checkov + Trivy config como gates.
- `.github/workflows/observability-smoke.yml`: smoke de logs JSON.
- `docs/`: evidencias DAST/IaC/Observabilidade e runbook.

## Execucao local rapida
1. DAST app corrigida:
   - `set TASKFLOW_SECRET_KEY=valor-local` (Windows) ou `export TASKFLOW_SECRET_KEY=valor-local` (Linux/macOS)
   - `python codigo/dast/app_fixed_dast.py`
2. Observabilidade:
   - `cd codigo/observabilidade`
   - `docker compose up --build -d`

## Arquitetura (resumo)
- App TaskFlow corrigida roda em container proprio e e validada por DAST no pipeline.
- Ambiente IaC usa Compose com redes separadas `frontend` e `backend`; banco acessivel apenas na rede interna.
- Observabilidade usa stack Loki + Promtail + Grafana para ingestao, consulta e visualizacao de logs JSON com `request_id`.

## Como disparar os workflows
1. DAST (`.github/workflows/dast.yml`)
   - Automatico em `pull_request` e `push` para `main`.
   - Manual: Actions > DAST > Run workflow.
2. IaC Scan (`.github/workflows/iac-scan.yml`)
   - Automatico em `pull_request` e `push` para `main`.
   - Manual: Actions > IaC Scan > Run workflow.
3. Observability Smoke (`.github/workflows/observability-smoke.yml`)
   - Automatico em `pull_request` e `push` para `main`.
   - Manual: Actions > Observability Smoke > Run workflow.

## Observacoes
- `.env` nunca deve ser versionado.
- Segredos devem ser injetados por variaveis de ambiente/secrets.
