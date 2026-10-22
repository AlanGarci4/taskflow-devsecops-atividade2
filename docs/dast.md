# DAST - Achados Antes x Depois

## Objetivo
Demonstrar o bloqueio do merge por DAST quando ha comportamento inseguro em runtime.

## Antes (vulneravel)
- XSS armazenado disparava ao renderizar tarefas com payload `<script>alert('XSS')</script>`.
- Endpoint `/debug/info` expunha informacoes internas.

## Depois (corrigido)
- A listagem de tarefas usa template Jinja2 com autoescape (sem `| safe`).
- Endpoint `/debug/info` removido (404).
- Debug controlado por variavel de ambiente e desligado por padrao.

## Mapeamento OWASP Top 10
- XSS armazenado: OWASP A03 - Injection.
- Exposicao de endpoint de debug e informacao sensivel: OWASP A05 - Security Misconfiguration.

## Evidencias esperadas na demo
1. PR com regressao de XSS bloqueado no workflow DAST.
2. PR com correcao de XSS e debug endpoint passando com check verde.
3. Relatorio do ZAP como artefato do workflow.
