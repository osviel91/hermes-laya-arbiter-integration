# Guía de uso de Laya/Arbiter

## Endpoint

```text
POST https://laya.osviel.duckdns.org/v1/systemone
```

Cabeceras:

```http
Content-Type: application/json
Authorization: Bearer <token>
```

El token debe llegar desde una variable de entorno o un gestor de secretos.

## Petición mínima

```json
{
  "model": "auto",
  "state": "Database restarted after OOM.",
  "questions": {
    "action": {
      "type": "choice",
      "instructions": "Choose the most appropriate operational response.",
      "criteria": {
        "ignore": "No action required",
        "investigate": "Investigate root cause",
        "escalate": "Immediate human escalation"
      }
    }
  }
}
```

## Modelos y aliases

- `laya-english`, `english`, `en`
- `laya-multilingual`, `multilingual`, `multi`
- `laya-typed-decisions`, `typed`, `typed-decisions`
- `auto`, `default`, `jev`, `laya`, `jev-latest`

Usa `auto` para routing automático y `typed` cuando quieras forzar el checkpoint de decisiones tipadas.

## Tipos de pregunta

### `choice`

Elige una alternativa entre opciones cerradas:

```json
{
  "type": "choice",
  "instructions": "Classify the operational response.",
  "criteria": {
    "ignore": "No action required",
    "investigate": "Investigate root cause",
    "escalate": "Immediate human escalation"
  }
}
```

### `score`

Puntúa una escala ordenada de menor a mayor:

```json
{
  "type": "score",
  "instructions": "Score operational severity.",
  "criteria": ["low", "medium", "high"]
}
```

### `noul`

Estima la probabilidad de una afirmación:

```json
{
  "type": "noul",
  "instructions": "This incident requires human intervention."
}
```

## Batching

Varias preguntas pueden compartir un mismo estado:

```json
{
  "questions": {
    "severity": { "type": "choice", "instructions": "Classify severity.", "criteria": {"low": "No impact", "high": "Severe impact"} },
    "needs_human": { "type": "noul", "instructions": "This incident requires human intervention." },
    "action": { "type": "choice", "instructions": "Choose response.", "criteria": {"ignore": "No action", "investigate": "Investigate", "escalate": "Escalate"} }
  }
}
```

La experiencia del nodo mostró que agrupar varias preguntas reduce la latencia media por pregunta.

## Interpretación

No uses solo `choice`. Conserva:

- `probabilities`;
- `confidence`;
- `routing`;
- `latency_ms`; y
- el margen `top1 - top2`.

Una opción top-1 con `confidence` baja o margen pequeño es una señal débil.

## Política conservadora

```text
confidence >= 0.50
  solo automatización de bajo riesgo y reversible

0.20 <= confidence < 0.50
  recomendación, no autorización

confidence < 0.20
  señal ambigua: pedir contexto, usar un modelo mayor o escalar
```

Son thresholds iniciales, no una calibración estadística del entorno.

## Errores esperables

- `401`: falta o invalidez del Bearer token.
- `422`: estructura o criterios inválidos.
- `529`: cola de inferencia saturada.
- timeout: nodo remoto no accesible o no listo.

## Regla de seguridad

Laya es un motor de decisiones estructuradas, no una autoridad de seguridad. Nunca ejecutes automáticamente una acción irreversible solo por la respuesta del modelo.
