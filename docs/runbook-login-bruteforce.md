# Runbook - Login Brute Force (NIST SP 800-61)

## Condicao de disparo
- Mais de 10 eventos `login_failed` do mesmo IP em 5 minutos.

## Query de deteccao (Loki)
```
sum by (ip) (count_over_time({container="/taskflow-app-obs"} |= "login_failed" [5m]))
```

## 1) Preparacao
- Confirmar stack de observabilidade ativa (Grafana/Loki/Promtail).
- Validar retencao de logs e acesso do time.

## 2) Deteccao e Analise
- Identificar IPs com volume anormal de `login_failed`.
- Correlacionar com `http_response` e `request_id` para escopo do incidente.

## 3) Contencao, Erradicacao e Recuperacao
- Bloquear IP ofensivo no controle de borda.
- Forcar reset de credenciais afetadas, se houver evidencias.
- Monitorar reducao dos eventos apos bloqueio.

## 4) Pos-incidente
- Registrar timeline do incidente.
- Criar acao corretiva: rate-limit em `/login` e alerta automatico no Grafana.
- Revisar e atualizar este runbook com licoes aprendidas.
