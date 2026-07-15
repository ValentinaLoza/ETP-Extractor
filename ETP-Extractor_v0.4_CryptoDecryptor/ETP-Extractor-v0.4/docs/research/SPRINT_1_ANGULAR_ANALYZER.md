# Sprint 1 — Angular Analyzer

## Resultado

El análisis se ejecutó contra los bundles reales suministrados de ETP Premium y contra la extracción de `app.asar`.

### Autenticación confirmada

El interceptor Angular aplica esta lógica:

```javascript
const requestWithToken =
  auth.state.token && !request.params.get("token")
    ? request.clone({
        params: request.params.append("token", auth.state.token)
      })
    : request;
```

Por lo tanto, las llamadas directas sin `token` son redirigidas por el backend.

### Origen y almacenamiento del token

El flujo confirmado es:

```text
Angular AuthStore
    │ getToken()
    ▼
Electron preload
    │ IPC: get-token
    ▼
Electron main process
    │ Helpers singleton (memoria)
    ▼
Electron callback
    │ IPC: token-callback
    ▼
Angular AuthStore
    │ interceptor agrega ?token=...
    ▼
API local
```

Canales IPC confirmados:

- `get-token`
- `set-token`
- `token-callback`

El token se mantiene en memoria del proceso principal de Electron mediante `Helpers.getInstance().token`. No se encontró evidencia de que el valor se guarde en un archivo de configuración común.

### Rutas detectadas

Se detectaron **10 rutas `/api/...`** en el bundle:

```text
/api/attachments
/api/auth
/api/bookmarks
/api/config/
/api/content/
/api/library
/api/manual
/api/manual/toc
/api/search/
/api/shopping/
```

## Implicación para el próximo sprint

El API Client debe obtener una sesión válida desde el proceso Electron o usar un mecanismo legítimo de sesión expuesto por la propia aplicación. No alcanza con reproducir las rutas usando `curl` sin token.

## Próximo objetivo

Construir el **Session Bridge**:

1. localizar una forma de consultar el token mediante el IPC ya expuesto por Electron;
2. evitar modificar o deshabilitar controles de autenticación;
3. usar el token únicamente contra la instalación local autorizada;
4. validar `/api/library`;
5. validar `/api/manual/toc`;
6. guardar una primera respuesta estructurada del IPC PT6A-140.
