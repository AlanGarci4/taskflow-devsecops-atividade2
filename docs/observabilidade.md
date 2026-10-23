# Observabilidade - Loki/Grafana

## Objetivo
Disponibilizar visibilidade de eventos de seguranca em logs estruturados JSON com `request_id`.

## Eventos logados
- `login_success`
- `login_failed`
- `tasks_list`
- `task_created`
- `http_response`

## Garantias de higiene
- Sem senha, token, cookie ou payload bruto sensivel nos logs.

## Consultas LogQL (exemplos)
1. Falhas de login por IP (contagem em janela de 5 minutos):
   ```
   sum by (ip) (count_over_time({container="/taskflow-app-obs"} |= "login_failed" [5m]))
   ```
2. Taxa de requests por status:
   ```
   sum by (status) (count_over_time({container="/taskflow-app-obs"} |= "http_response" [5m]))
   ```
3. Eventos por request_id especifico:
   ```
   {container="/taskflow-app-obs"} |= "request_id" |= "<valor-request-id>"
   ```

## Evidencia da simulacao de incidente (forca bruta)
Checklist minimo para comprovacao no dia da entrega:
- Stack de observabilidade ativa (Grafana, Loki e Promtail).
- Simulacao executada com multiplas tentativas de login invalido.
- Query de deteccao retornando aumento de `login_failed` por IP.
- Captura de tela do Grafana com data/hora visivel.

Exemplo simples de simulacao local (PowerShell):
```powershell
1..20 | ForEach-Object {
   Invoke-WebRequest -Uri "http://localhost:5000/login" -Method Post -Body @{ username = "admin"; password = "senha_invalida" } | Out-Null
}
```

Query usada na deteccao:
```
sum by (ip) (count_over_time({container="/taskflow-app-obs"} |= "login_failed" [5m]))
```

Evidencias sugeridas para anexar no repositorio:
- Print 1: painel do Grafana com a query acima e pico por IP.
- Print 2: exploracao de logs com `request_id` de uma tentativa.
- Print 3: trecho de timeline de resposta usando as 4 fases do runbook.
