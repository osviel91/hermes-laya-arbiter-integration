# Configuración del MCP de Arbiter en Hermes

Esta guía configura el bridge oficial `integrations/mcp/arbiter_mcp.py` como un servidor MCP stdio llamado `arbiter`.

## Requisitos

- Hermes Agent instalado.
- Un entorno Python de Hermes donde `import mcp` funcione.
- Repositorio oficial de Arbiter clonado localmente.
- Servicio Laya/Arbiter remoto accesible por HTTPS.
- `LAYA_API_KEY` presente en el fichero `.env` efectivo de Hermes.

No se debe ejecutar `./run.sh setup` en el nodo de Hermes ni descargar checkpoints allí.

## Detectar rutas reales

```bash
hermes --version
hermes config path
hermes config env-path
hermes mcp list
```

El intérprete debe comprobarse explícitamente:

```bash
/path/to/python -c 'import sys, mcp; print(sys.executable); print(mcp.__file__)'
```

## Clonar el bridge

```bash
git clone https://github.com/0xBakeer/arbiter.git "$HOME/.hermes/arbiter"
```

El bridge utilizado es únicamente:

```text
$HOME/.hermes/arbiter/integrations/mcp/arbiter_mcp.py
```

## Configurar con Hermes CLI

No edites `config.yaml` manualmente. Sustituye las rutas por las detectadas en tu instalación:

```bash
HERMES_PYTHON="/absolute/path/to/hermes/python"
ARBITER_REPO="$HOME/.hermes/arbiter"

hermes config set mcp_servers.arbiter.command "$HERMES_PYTHON"
hermes config set mcp_servers.arbiter.args "['$ARBITER_REPO/integrations/mcp/arbiter_mcp.py']"
hermes config set mcp_servers.arbiter.env.ARBITER_URL 'https://laya.osviel.duckdns.org'
hermes config set mcp_servers.arbiter.env.ARBITER_MODEL auto
hermes config set mcp_servers.arbiter.env.ARBITER_API_KEY '${LAYA_API_KEY}'
hermes config set mcp_servers.arbiter.enabled true
```

Para un perfil nombrado:

```bash
hermes -p <profile> config set mcp_servers.arbiter.command "$HERMES_PYTHON"
```

Repite las claves restantes con el mismo selector `-p <profile>`.

## Validación

```bash
hermes config check
hermes config get mcp_servers.arbiter
hermes mcp test arbiter
```

Debe aparecer:

```text
✓ Connected
✓ Tools discovered: 5
```

Las tools esperadas son:

- `arbiter_check`
- `arbiter_classify`
- `arbiter_score`
- `arbiter_gate`
- `arbiter_decide`

## Seguridad

- Nunca escribas el token en `config.yaml`.
- No publiques `.env`.
- No incluyas cabeceras `Authorization` en capturas o logs.
- La referencia `${LAYA_API_KEY}` debe resolverse desde el `.env` del perfil.
- El bridge usa `ARBITER_API_KEY` internamente porque ese es el nombre que espera el código oficial.

## Activación

La configuración se valida mediante un proceso nuevo de `hermes mcp test`. Las sesiones y gateways ya arrancados pueden necesitar reinicio o una nueva sesión para descubrir las tools.
