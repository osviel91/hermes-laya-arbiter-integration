# Hermes + Laya/Arbiter

Integración de un motor de decisiones estructuradas Laya/Arbiter con Hermes Agent mediante MCP.

Este repositorio documenta una arquitectura en la que Hermes mantiene el razonamiento abierto, la investigación y la orquestación, mientras Arbiter/Laya resuelve decisiones acotadas con alternativas cerradas, puntuaciones, probabilidades y decisiones agrupadas.

## Qué incluye

- La skill `bounded-decision-arbiter` en inglés.
- Configuración reproducible del servidor MCP `arbiter` para Hermes.
- Guía de despliegue de Laya/Arbiter en un nodo Apple Silicon con MLX.
- Guía de uso de la API `/v1/systemone`.
- Política conservadora de confianza y seguridad.
- Casos de uso y resultados experimentales.
- Scripts de validación sin secretos.

## Arquitectura

```text
Hermes Agent
  |
  | MCP stdio
  v
Arbiter MCP bridge
  |
  | HTTPS + Bearer token
  v
Laya/Arbiter remoto
  |
  +-- laya-english
  +-- laya-multilingual
  +-- laya-typed-decisions
```

El nodo de inferencia mantiene Laya separado de Hermes. Hermes no descarga checkpoints ni ejecuta el servidor de inferencia localmente.

## Estado validado

Validado el 27 de septiembre de 2026 en la instalación real de Hermes:

- Hermes Agent `v0.21.5+2144.g7b761da`.
- Python del entorno Hermes `3.14.7`.
- `mcp` disponible en el entorno Python de Hermes.
- Bridge oficial de Arbiter clonado desde `0xBakeer/arbiter`.
- Servicio remoto accesible mediante `https://laya.osviel.duckdns.org`.
- `hermes mcp test arbiter`: conexión correcta.
- Cinco tools descubiertas: `arbiter_check`, `arbiter_classify`, `arbiter_score`, `arbiter_gate`, `arbiter_decide`.
- Prueba funcional de `arbiter_classify` ejecutada contra el servicio remoto.

Los valores sensibles y tokens están deliberadamente excluidos de este repositorio.

## Inicio rápido

1. Clona el repositorio de Arbiter en el nodo donde se ejecutará el bridge:

   ```bash
   git clone https://github.com/0xBakeer/arbiter.git "$HOME/.hermes/arbiter"
   ```

2. Comprueba que `LAYA_API_KEY` existe en el `.env` efectivo de Hermes.

3. Configura el MCP con la CLI de Hermes usando la guía:

   - [`docs/hermes-mcp-configuration.md`](docs/hermes-mcp-configuration.md)

4. Valida:

   ```bash
   hermes config check
   hermes mcp test arbiter
   ```

5. Lee la skill:

   - [`skills/bounded-decision-arbiter/SKILL.md`](skills/bounded-decision-arbiter/SKILL.md)

## Principio operativo

Arbiter no sustituye el razonamiento abierto. El flujo recomendado es:

```text
comprender e investigar
        ↓
sintetizar hechos relevantes
        ↓
formular una decisión cerrada
        ↓
consultar Arbiter/Laya
        ↓
interpretar probabilidades + confidence + margen
        ↓
actuar solo si la política y el riesgo lo permiten
```

`arbiter_gate` es advisory. Nunca debe ser la única autoridad para borrar datos, modificar producción, cambiar credenciales, publicar información o ejecutar acciones irreversibles.

## Estructura

```text
.
├── README.md
├── LICENSE
├── .gitignore
├── docs/
│   ├── hermes-mcp-configuration.md
│   ├── laya-deployment.md
│   ├── laya-usage.md
│   └── security-and-confidence.md
├── examples/
│   └── hermes-mcp-server.yaml
├── experiments/
│   ├── README.md
│   └── results.json
├── scripts/
│   ├── run_arbiter_experiment.py
│   └── validate_repository.py
└── skills/
    └── bounded-decision-arbiter/SKILL.md
```

## Licencia y alcance

Este repositorio documenta una integración y una experiencia operativa. El bridge y Arbiter pertenecen a sus respectivos proyectos upstream. Revisa sus licencias antes de redistribuir código o componentes.
