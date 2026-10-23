# IaC Scan - Evidencias e Gates

## Objetivo
Comprovar que o pipeline de IaC bloqueia merge quando houver risco critico e aprova quando a configuracao estiver segura.

## Gates aplicados no CI
- Checkov para Terraform em `codigo/iac/infra`.
- Trivy Config para avaliacao de configuracao em `codigo/iac/docker-compose.yml`.

## Comportamento esperado
1. Se houver achado critico, o job falha (gate ativo).
2. Com configuracao corrigida, os dois jobs passam em verde.

## Evidencia no PR final
- Workflow `IaC Scan` com `Checkov` e `Trivy Config` em status `success`.
- PR `#3` com checks obrigatorios verdes antes do merge.

## Observacoes tecnicas
- Trivy executa via container oficial (`aquasec/trivy:0.56.2`).
- Para esse modo de execucao, usar `--quiet` no `trivy config` e manter `--exit-code 1` para bloquear em caso critico.
