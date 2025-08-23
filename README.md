# Trabajo Remoto - Gestor (Windows)

Aplicación de escritorio para que un supervisor asigne un único día remoto por semana a cada empleado, con validaciones de negocio y una interfaz moderna.

## Características
- Un registro por semana por empleado (evita duplicados).
- No permite lunes ni fines de semana.
- Advierte si intenta repetir el mismo día que la semana anterior (permite continuar si se confirma).
- Vista semanal con botones por día; se marca automáticamente el día registrado.
- Lista de empleados con indicación de si ya registraron esta semana.
- Persistencia local en SQLite (sin servidor). Logs locales.

## Requisitos
- Windows 10/11
- Python 3.11+ (solo para desarrollo). Para usuarios finales, se distribuye `.exe`.

## Estructura
- `ui/` Interfaz (PyQt6), estilos QSS e iconos.
- `services/` Reglas de negocio (validaciones de semana y día).
- `data/` Acceso a SQLite, creación de esquema, repositorios.
- `scripts/` Utilidades para preparar datos y build.

## Ejecutar en desarrollo
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Scripts de QA
- Reset DB y recrear esquema:
```bash
python scripts/reset_db.py
```
- Sembrar demo: 10 empleados, 5 con registro semana pasada y 5 hace dos semanas:
```bash
python scripts/seed_mixed_weeks.py
```

## Build (.exe) con PyInstaller
- PowerShell:
```bash
pwsh -NoProfile -File scripts/build.ps1
```
Genera `dist/TrabajoRemoto.exe` e incluye `ui/resources/style.qss` y `ui/resources/icons` dentro del bundle.

## Notas de diseño
- Tema oscuro con QSS personalizado.
- Iconografía SVG con `currentColor` para heredar colores del tema.
- Soporte High-DPI habilitado.

## Logs y base de datos
- DB y logs se guardan en `%LOCALAPPDATA%/TrabajoRemoto/`.
- Logs diarios: `logs/YYYY-MM-DD.log`.

## Licencia
MIT