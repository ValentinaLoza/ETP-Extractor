# Hallazgos confirmados

## Aplicación

- Nombre: ETP Offline Premium / ETP Premium
- Versión observada: 3.3.1
- Arquitectura: Electron + Angular + backend local
- Proceso backend: `etp-api.exe`
- Servidor local: HTTPS sobre `127.0.0.1`
- Puerto observado: `13374` en una ejecución
- El puerto puede ser dinámico y debe detectarse por PID

## Frontend

El servidor local entrega:

- `index.html`
- `main-es2015...js`
- `runtime-es2015...js`
- `scripts...js`
- hojas de estilo y assets

## Paquetes offline

- `etp.db`: RocksDB/LevelDB
- `graphics.zip`: recursos gráficos
- Parte del contenido aparece almacenado en forma codificada/cifrada
- El cliente oficial puede mostrarlo

## Rutas observadas en bundles

Pendiente de validación funcional:

- `/api/library`
- `/api/manual`
- `/api/manual/toc`
- `/api/content/`
- `/api/search/`
- `/api/attachments`
- `/api/bookmarks`
- `/api/config`

## Advertencia

Las rutas directas sin el contexto del cliente recibieron redirección HTTP 302 al portal de P&WC. Puede existir un interceptor, cookie, header o estado de sesión obligatorio.
