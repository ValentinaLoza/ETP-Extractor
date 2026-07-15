# Arquitectura

## 1. Angular Analyzer

Responsable de analizar los bundles JavaScript de la aplicación ETP.

Funciones previstas:

- localizar rutas `/api/...`
- detectar servicios Angular
- identificar interceptores HTTP
- extraer nombres de parámetros
- buscar referencias a manuales, TOC, contenido y figuras
- generar un informe JSON

## 2. API Client

Cliente HTTP local de solo lectura.

Funciones previstas:

- detectar puerto del proceso `etp-api.exe`
- gestionar HTTPS local
- reproducir solicitudes observadas
- guardar respuestas y encabezados
- manejar sesiones, cookies y headers requeridos

## 3. Package Reader

Lectura de paquetes offline y metadatos locales.

Funciones previstas:

- inspeccionar ZIP
- identificar `etp.db`
- leer índices RocksDB cuando sea posible
- catalogar `graphics.zip`
- relacionar publicación, revisión e idioma

## 4. Content Parser

Normalización de contenido técnico.

Funciones previstas:

- HTML/XML
- IPC
- MM
- S1000D
- tablas
- figuras y referencias cruzadas

## 5. Consumables Builder

Clasificación de consumibles:

- O-RING
- PACKING
- GASKET
- SEAL
- FILTER
- WASHER
- COTTER PIN
- LOCKWIRE
- ADHESIVE
- LUBRICANT
- COMPOUND

## 6. Database

Base SQLite inicial con posibilidad de migrar a PostgreSQL.

Entidades principales:

- Publication
- ManualRevision
- ATAChapter
- Figure
- Item
- Part
- Consumable
- AlternatePart
- Inspection
- Task
- SourceReference

## 7. Exporters

- CSV
- Excel
- JSON
- SQLite
