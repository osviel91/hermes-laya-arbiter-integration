# Seguridad y confianza

## Separación de responsabilidades

```text
Hermes: comprensión, investigación, síntesis y orquestación.
Arbiter: decisiones cerradas, scores, checks y batching.
Políticas deterministas: límites de seguridad y permisos.
Humano: autorización de acciones críticas.
```

## No convertir una señal en una autorización

Una respuesta de Arbiter puede ser útil y aun así ser ambigua. La decisión final debe considerar:

- calidad y completitud del `state`;
- definición de las opciones;
- `probabilities`;
- `confidence`;
- margen entre las dos mejores opciones;
- reversibilidad;
- blast radius;
- políticas del sistema; y
- confirmación humana.

## Acciones que requieren cautela máxima

- borrar datos;
- cambios de producción;
- rotar credenciales o certificados;
- publicar información;
- cambios irreversibles;
- acciones de seguridad;
- comandos con gran blast radius.

## Datos y secretos

Nunca deben versionarse:

- `LAYA_API_KEY`;
- `ARBITER_API_KEY`;
- cabeceras Authorization;
- dumps de configuración efectivos;
- logs con tokens;
- datos privados de usuarios o clientes.

## Publicación de resultados

Al publicar benchmarks o casos de éxito:

- indica fecha y hardware;
- indica modelo y modo de routing;
- conserva latencia y errores;
- no presentes un caso aislado como garantía;
- separa resultado observado de conclusión general;
- explica incertidumbre y limitaciones.
