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
