# Experimentos

Esta carpeta contiene resultados reproducibles de pruebas del bridge MCP y del servicio remoto.

## Qué medir

- Conectividad MCP y descubrimiento de tools.
- Latencia de decisiones simples.
- Distribución de probabilidades.
- `confidence`.
- Margen entre las dos mejores alternativas.
- Diferencia entre una llamada individual y varias preguntas agrupadas.
- Comportamiento con texto en inglés y español.

## Cómo ejecutar

El script usa el intérprete Python del entorno de Hermes y obtiene `LAYA_API_KEY` del `.env` efectivo sin imprimirlo:

```bash
python scripts/run_arbiter_experiment.py
```

Para una prueba de conexión MCP:

```bash
hermes mcp test arbiter
```

Los resultados publicados deben conservar el contexto experimental, la fecha, el endpoint lógico, el modelo solicitado y las limitaciones. No deben incluir tokens, cabeceras `Authorization` ni prompts privados.
