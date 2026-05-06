# SentinelOps

SentinelOps es un sistema multi-agente de deteccion y respuesta autonoma a incidentes de ciberseguridad en tiempo real. Reduce una investigacion de 2-8 horas a ~40 segundos con cuatro agentes especializados sobre Llama 70B en AMD MI300X (vLLM, sin cuantizacion). El analista humano conserva el control final desde un dashboard.

## Arquitectura (ASCII)

```mermaid
flowchart LR
    %% =======================
    %% INGESTIÓN
    %% =======================
    subgraph INGESTION["🔌 Data Ingestion Layer"]
        A1[Syslog]
        A2[Log Files]
        A3[Mock Generator]
    end

    %% =======================
    %% COLA / STREAM
    %% =======================
    subgraph STREAM["⚡ Event Streaming"]
        B[Redis Event Queue]
    end

    %% =======================
    %% AI AGENTS
    %% =======================
    subgraph AI["🧠 AI Multi-Agent Pipeline"]
        C1[Security Classifier]
        C2[Threat Investigator]
        C3[Event Correlator]
        C4[Playbook Generator]
    end

    %% =======================
    %% STORAGE
    %% =======================
    subgraph STORAGE["💾 Persistence Layer"]
        D[(PostgreSQL)]
    end

    %% =======================
    %% FRONTEND
    %% =======================
    subgraph UI["🖥️ Visualization Layer"]
        E[React Dashboard<br/>WebSockets]
    end

    %% =======================
    %% FLOW
    %% =======================
    A1 --> B
    A2 --> B
    A3 --> B

    B --> C1
    C1 --> C2
    C2 --> C3
    C3 --> C4

    C4 --> D
    D --> E

    %% =======================
    %% STYLES
    %% =======================
    classDef ingestion fill:#0f172a,color:#fff,stroke:#38bdf8,stroke-width:2px;
    classDef stream fill:#1e293b,color:#fff,stroke:#22c55e,stroke-width:2px;
    classDef ai fill:#111827,color:#fff,stroke:#a78bfa,stroke-width:2px;
    classDef storage fill:#020617,color:#fff,stroke:#f59e0b,stroke-width:2px;
    classDef ui fill:#0b1120,color:#fff,stroke:#f43f5e,stroke-width:2px;

    class A1,A2,A3 ingestion;
    class B stream;
    class C1,C2,C3,C4 ai;
    class D storage;
    class E ui;
```

## Setup rapido (menos de 10 minutos)

Requisitos: Docker Desktop, Python 3.11, Node 18.

1) Copia .env.example a .env y ajusta claves si aplica.
2) Levanta los servicios:
   - docker compose up --build
3) Abre la UI:
   - http://localhost:3000

### Setup por rol

- Product Lead: valida README, abre la UI y revisa TASKS.md.
- Cyber Security Expert: revisa data/sample_logs y ajusta reglas en agents/tools.
- ML Engineer: define VLLM_BASE_URL a AMD vLLM y prueba prompts en agents/prompts.
- Backend Developer: verifica endpoints en http://localhost:8000/docs y WS en /ws/alerts.
- Frontend Developer: revisa modo demo con REACT_APP_DEMO_MODE=true y layout responsivo.

## Variables de entorno (principales)

- VLLM_BASE_URL: endpoint OpenAI-compatible (ej: http://amd-vllm:8000/v1)
- VLLM_MODEL_NAME: nombre del modelo (ej: llama-70b)
- VIRUSTOTAL_API_KEY, ABUSEIPDB_API_KEY: credenciales externas
- REDIS_URL: cola de eventos (redis://redis:6379/0)
- DATABASE_URL: historial (postgresql://sentinel:sentinel@postgres:5432/sentinelops)
- CORS_ORIGINS: origenes permitidos para la UI
- API_SECRET_KEY: clave para futuras firmas/autorizacion
- REACT_APP_DEMO_MODE: true para UI sin backend

## Simulador de ataques (demo)

Ejecuta el script para inyectar un ataque completo:

python scripts/simulate_attack.py --base-url http://localhost:8000

El script imprime progreso por fase y envia logs al endpoint /api/logs/ingest.

## Estructura del proyecto (con comentarios)

```mermaid
flowchart LR

    %% =======================
    %% BACKEND
    %% =======================
    subgraph BACKEND["⚙️ Backend (FastAPI)"]
        B1[main.py]
        B2[routers]
        B3[models]
        B4[services]
        B5[utils]

        B2 -->|REST + WS| B1
        B3 --> B1
        B4 --> B1
        B5 --> B1
    end

    %% =======================
    %% AGENTS
    %% =======================
    subgraph AGENTS["🧠 AI Agents (CrewAI)"]
        A1[crew.py]
        A2[tools]
        A3[prompts]

        A1 --> A2
        A1 --> A3
    end

    %% =======================
    %% FRONTEND
    %% =======================
    subgraph FRONTEND["🖥️ Frontend (React)"]
        F1[App.jsx]
        F2[components]
        F3[hooks]
        F4[data]

        F1 --> F2
        F1 --> F3
        F1 --> F4
    end

    %% =======================
    %% DATA
    %% =======================
    subgraph DATA["📂 Data & Simulation"]
        D1[sample_logs]
        D2[mock_attacks]
        D3[simulate_attack.py]
    end

    %% =======================
    %% INFRA
    %% =======================
    subgraph INFRA["🐳 Infraestructura"]
        I1[docker-compose]
        I2[PostgreSQL]
        I3[Redis]
        I4[vLLM Mock Server]
    end

    %% =======================
    %% FLOW RELATIONS
    %% =======================
    D3 --> D1
    D1 --> B2

    B4 --> A1
    A1 --> B4

    B1 --> F1

    B4 --> I2
    B4 --> I3

    A1 --> I4

    I1 --> BACKEND
    I1 --> FRONTEND
    I1 --> AGENTS

    %% =======================
    %% STYLES
    %% =======================
    classDef backend fill:#0f172a,color:#fff,stroke:#38bdf8,stroke-width:2px;
    classDef agents fill:#111827,color:#fff,stroke:#a78bfa,stroke-width:2px;
    classDef frontend fill:#0b1120,color:#fff,stroke:#22c55e,stroke-width:2px;
    classDef data fill:#020617,color:#fff,stroke:#f59e0b,stroke-width:2px;
    classDef infra fill:#1e293b,color:#fff,stroke:#f43f5e,stroke-width:2px;

    class B1,B2,B3,B4,B5 backend;
    class A1,A2,A3 agents;
    class F1,F2,F3,F4 frontend;
    class D1,D2,D3 data;
    class I1,I2,I3,I4 infra;
```
