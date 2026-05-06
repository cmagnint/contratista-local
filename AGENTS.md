# AGENTS.md

## Objetivo del repositorio
Este proyecto contiene un frontend Angular y un backend Django para una aplicación empresarial.
Estamos construyendo un catálogo de módulos para un chatbot interno que debe orientar usuarios dentro del sistema.

## Reglas generales
- No inventar rutas Angular.
- La fuente de verdad para rutas es `frontend/src/app/app.routes.ts`.
- El árbol de componentes sirve para detectar módulos y pantallas, pero no confirma por sí solo la ruta final.
- Si una ruta no puede verificarse, dejarla como `null` o marcarla como `needs_verification`.
- No renombrar archivos ni mover carpetas salvo que la tarea lo pida explícitamente.
- Hacer cambios pequeños y verificables.
- Antes de dar por terminada una tarea, resumir qué archivos fueron leídos y qué supuestos quedaron pendientes.

## Frontend
- El frontend está en `frontend/src/app`.
- Las pantallas principales están bajo `frontend/src/app/pages`.
- Priorizar lectura de `app.routes.ts`, `mother-layout.component.*` y componentes bajo `pages/mother-layout/`.

## Backend
- El backend Django debe recibir un catálogo de módulos verificable y editable por usuarios o administradores.
- Evitar lógica acoplada a nombres inventados desde IA.

## Para tareas de catálogo
- Generar catálogos en JSON o fixtures Django.
- Incluir para cada módulo:
  - `codigo`
  - `nombre`
  - `area`
  - `frontend_path`
  - `ruta_angular`
  - `estado_ruta`
  - `descripcion`
  - `palabras_clave`
- Usar `estado_ruta = "verified"` solo si la ruta está confirmada en `app.routes.ts`.
- Usar `estado_ruta = "needs_verification"` si solo se infiere por carpeta o nombre de componente.

## Criterio de terminado
- El resultado debe ser auditable.
- No deben quedar rutas inventadas presentadas como definitivas.