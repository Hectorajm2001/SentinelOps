# SentinelOps - 48h Plan

## H0-H8 (Setup y fundamentos)
- Todos: setup del repo, variables de entorno, verificar que docker-compose levanta
- ML Engineer: levantar vLLM en AMD Developer Cloud, verificar endpoint
- Backend: esqueleto FastAPI corriendo, Redis conectado, WebSocket basico
- Frontend: React corriendo, layout de 3 paneles sin datos
- Cyber Expert: preparar datasets de logs, definir reglas de deteccion
- Product Lead: preparar estructura del pitch, coordinar dependencias

## H8-H24 (Nucleo funcional)
- ML Engineer: 4 agentes CrewAI funcionando con mock-vllm, prompts refinados
- Backend: pipeline completo logs -> Redis -> agentes -> PostgreSQL
- Frontend: WebSocket conectado, alertas en tiempo real
- Cyber Expert: validar clasificaciones tecnicas
- Product Lead: primera demo interna, identificar cuellos de botella

## H24-H40 (Integracion y pulido)
- ML Engineer: conectar agentes al AMD MI300X real, optimizar prompts
- Backend: APIs externas (VirusTotal, AbuseIPDB) integradas
- Frontend: playbook renderizado, botones de aprobar/exportar, graficas
- Cyber Expert: refinar playbooks, agregar casos de ataque adicionales
- Product Lead: grabar video demo backup, preparar pitch de 3 minutos

## H40-H48 (Demo y entrega)
- Todos: bug fixing, deploy final, ensayo del demo
- Product Lead: pitch final, submission en lablab.ai, posts Build in Public
- Cyber Expert: preparar respuestas tecnicas para jueces
- Script simulate_attack.py corriendo en vivo durante el demo
