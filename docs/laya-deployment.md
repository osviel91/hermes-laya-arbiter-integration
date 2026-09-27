# Despliegue de Laya/Arbiter en Apple Silicon

Este documento resume el despliegue realizado en un nodo de inferencia Apple Silicon separado de Hermes.

## Objetivo

- Ejecutar Arbiter 0.2.0 con Laya y el engine nativo MLX.
- Mantener oMLX como servicio independiente.
- Exponer el servicio mediante HTTPS.
- Proteger `/v1/systemone` con Bearer token.
- Persistir el proceso mediante `launchd`.
- No instalar modelos ni Laya en el nodo que ejecuta Hermes.

## Topología

```text
Internet
  |
  | HTTPS :443
  v
laya.osviel.duckdns.org
  |
  v
OpenResty / reverse proxy
  |
  v
Arbiter :8010
  |
  v
Laya MLX
```

## Python y entorno

El Python del sistema era demasiado antiguo para la dependencia moderna de Arbiter. El despliegue utilizó Python 3.12 administrado por `uv`, sin Homebrew:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source "$HOME/.local/bin/env"
uv python install 3.12
uv python find 3.12
```

El repositorio se instaló bajo una ruta de servicios del usuario:

```bash
mkdir -p "$HOME/services"
git clone https://github.com/0xBakeer/arbiter.git "$HOME/services/arbiter"
cd "$HOME/services/arbiter"
```

## Instalación MLX

```bash
export PYTHON="$(uv python find 3.12)"
ARBITER_ENGINE=laya_mlx ./run.sh setup
```

Esto instala dependencias y checkpoints en el nodo de inferencia. No debe ejecutarse en el nodo de Hermes cuando solo se quiere utilizar el bridge MCP.

## Ejecución y validación

```bash
ARBITER_ENGINE=laya_mlx ./run.sh serve
ARBITER_ENGINE=laya_mlx ./run.sh status
ARBITER_ENGINE=laya_mlx ./run.sh smoke
ARBITER_ENGINE=laya_mlx ./run.sh bench
```

La validación observada incluyó:

- todos los casos del smoke test superados;
- routing inglés y multilingüe;
- decisiones tipadas;
- benchmark sin errores;
- batching con menor coste medio por pregunta.

## Autenticación

Configura el token fuera del repositorio:

```bash
export ARBITER_API_KEY='REPLACE_LOCALLY'
ARBITER_ENGINE=laya_mlx ARBITER_API_KEY="$ARBITER_API_KEY" ./run.sh serve
```

Sin un Bearer token válido, `/v1/systemone` debe devolver `401`. Una petición autenticada válida debe devolver `200`.

No copies el token en esta documentación, en un plist versionado ni en un ejemplo de curl publicado.

## HTTPS y reverse proxy

Se utilizó:

```text
https://laya.osviel.duckdns.org
```

No expongas directamente el puerto 8010 a Internet si el tráfico externo ya entra por el reverse proxy. Si el proxy está en el mismo host, enlaza Arbiter a `127.0.0.1`. Si está en otro nodo, restringe el acceso al origen del proxy mediante firewall.

## launchd

Usa `serve-foreground` para que `launchd` supervise el proceso real:

```xml
<key>ProgramArguments</key>
<array>
  <string>/absolute/path/to/arbiter/run.sh</string>
  <string>serve-foreground</string>
</array>
```

Las rutas, el usuario, el token y los logs deben generarse localmente. Valida el plist antes de cargarlo:

```bash
plutil -lint "$HOME/Library/LaunchAgents/com.example.arbiter.plist"
launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.example.arbiter.plist"
launchctl print "gui/$(id -u)/com.example.arbiter"
```

## Operación

```bash
curl -s http://127.0.0.1:8010/readyz
curl -s https://laya.osviel.duckdns.org/v1/models
```

La operación debe verificar readiness, autenticación, latencia, logs y persistencia después de reinicio. Las métricas publicadas en el artículo deben indicar que proceden de una ejecución concreta y no son una garantía universal.
