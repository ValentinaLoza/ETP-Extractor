# Sprint 2 — Session Bridge

## Objetivo

Ejecutar consultas de lectura desde la propia ventana autenticada de ETP sin exponer el token.

## Método

1. ETP se inicia con `--remote-debugging-port=9222`.
2. PowerShell consulta los targets de Chrome DevTools.
3. Se selecciona la ventana Angular de ETP.
4. Mediante `Runtime.evaluate`, la ventana ejecuta:
   - `window.ipc.getToken()`
   - `fetch(...)` con el token como query parameter.
5. Solo se devuelve el status, content type y cuerpo de la respuesta.
6. El valor del token no se incluye en el resultado.

## Pruebas previstas

- `/api/library`
- `/api/manual/toc?partno=3075744&revision=23&lang=en&media=html`

## Resultado esperado

Obtener la primera respuesta real estructurada de la biblioteca y luego del TOC del IPC PT6A-140.
