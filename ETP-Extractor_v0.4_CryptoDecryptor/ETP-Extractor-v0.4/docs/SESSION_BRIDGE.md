# Session Bridge v0.3

Este módulo consulta la API local desde la propia ventana oficial de ETP.

## Seguridad del diseño

- No imprime el token.
- No guarda el token.
- No modifica `app.asar`.
- No modifica `etp.db`.
- No desactiva la autenticación.
- El token solo se usa dentro de la sesión local abierta por ETP.

## Primera prueba

1. Cerrá ETP si está abierto.
2. Ejecutá `Ejecutar_Session_Bridge_Library.bat`.
3. El script abrirá ETP con un puerto de depuración local.
4. Esperá a que cargue la aplicación.
5. El script consultará `/api/library`.
6. Se creará una carpeta `ETP_Session_Report_...`.

Comprimí y compartí esa carpeta.

## Segunda prueba

Cuando la biblioteca funcione, ejecutá:

`Ejecutar_Session_Bridge_PT6A140_TOC.bat`

Ese acceso intenta obtener el TOC del IPC 3075744 Rev. 23.

## Nota

El puerto 9222 se abre solamente en la interfaz local `127.0.0.1` del equipo. Cerrando ETP se finaliza la sesión de depuración.
