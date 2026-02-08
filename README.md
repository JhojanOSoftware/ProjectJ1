# Smp1-Auto

Proyecto en Python para automatización y generación de documentos, con scripts y recursos web asociados.

## Estructura
- main.py: punto de entrada principal.
- Mysql_cn.py: conexión a base de datos MySQL.
- pdfgen.py: generación de PDFs.
- recexamples.py / recgenerator.py: ejemplos y generación de recibos.
- models/: modelos de datos.
- routes/: rutas (si aplica).
- services/: recursos estáticos (JS/CSS).
- data/: datos auxiliares.

## Requisitos
- Python 3.10+ (recomendado)
- Dependencias según el entorno del proyecto.

## Uso
1. Configura las variables de entorno necesarias (por ejemplo, credenciales de base de datos).
2. Ejecuta el proyecto:
   - Windows (PowerShell) o en CMD:
     - `python main.py`
     - `uvicorn main:app --reload --host 127.0.0.1 --port 8000`

## Notas
- Ajusta los paths y credenciales según tu entorno.

## Licencia
Ver [LICENCE.md](LICENCE.md).
