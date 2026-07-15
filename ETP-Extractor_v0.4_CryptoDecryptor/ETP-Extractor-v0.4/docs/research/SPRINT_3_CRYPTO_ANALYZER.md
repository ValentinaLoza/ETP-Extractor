# Sprint 3 — Crypto Analyzer

## Resultado confirmado

El contenido del ETP Offline Premium puede descifrarse localmente con los archivos que ya instala la aplicación.

Flujo identificado:

1. Cada `etp.db` contiene un registro JSON titulado `aeskey`.
2. `aeskey.content` contiene 256 bytes cifrados con RSA.
3. La clave privada RSA se encuentra en `server/pkr`.
4. RSA PKCS#1 v1.5 devuelve una passphrase ASCII de 32 bytes.
5. Los campos `content` y las leyendas gráficas usan el formato CryptoJS/OpenSSL:
   - prefijo `Salted__`
   - derivación compatible con `EVP_BytesToKey` usando MD5
   - AES-256-CBC
   - padding PKCS#7
6. El resultado es HTML UTF-8 legible.

## Validación real

Se descifraron correctamente 158 módulos del IPC PT6A-140 P/N 3075744 Rev. 23, incluido el HTML de tablas IPC.

## Impacto

Ya es posible desarrollar:

- extractor completo de módulos;
- parser de tablas IPC;
- catálogo de partes;
- clasificador de consumibles;
- validación del kit PT6A-140;
- extracción posterior del Maintenance Manual.
