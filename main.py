import shutil
import sqlite3
import traceback
from xmlrpc import client
from fastapi.responses import JSONResponse
from fastapi import FastAPI, HTTPException, status,Form, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter
from slowapi.util import get_remote_address
limiter = Limiter(key_func=get_remote_address)
from models.ClaseArrendatario import Arrendatario, ArrendatarioUpdate, PDFData, PersonaEditada, Concepto
from  recexamples import *
from fastapi.responses import FileResponse
import tempfile
import zipfile
import os

# Inicializar la app de FastAPI
app = FastAPI(title="Actividad Microsite API")
app.mount("/services", StaticFiles(directory="services"), name="services")

# Aplicar el limiter a la app (opcional, para tenerlo disponible globalmente)
app.state.limiter = limiter




# Ajusta orígenes según donde sirvas el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500", "http://localhost:3000", "http://127.0.0.1:8000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_FILE = "data/J0BaseDatos.db"


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def Db_Arrendatarios() -> None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS arrendatarios_J0 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_arrendatario TEXT NOT NULL,
            nombre_ubicacion TEXT NOT NULL,
            direccion_ubicacion TEXT NOT NULL,
            personas_por_arrendatario INTEGER,
            telefono TEXT,
            email TEXT
        )
    """)
    
    
    conn.commit()
    conn.close()

def total_personas(nombre_ubicacion:str):

    try :
        con = get_conn()
        cur = con.cursor()
        cur.execute("SELECT SUM(personas_por_arrendatario) as total FROM arrendatarios_J0 WHERE nombre_ubicacion = ?", (nombre_ubicacion,))
        row = cur.fetchone()
        con.close()
        return row["total"] if row["total"] is not None else 1
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error obteniendo total de personas: {e}")

def calcular_servicios(WaterValue: int, LuzValue: int, AseoValue: int, GasValue: int, 
                       personas_por_arrendatario: int, 
                        nombre_ubicacion: str, cantidad_arrendatarios: int):
                       
    headcount = max(1,total_personas(nombre_ubicacion))              # Total de personas en esa ubicación
    valor_unitario = WaterValue / headcount                   # Costo por persona
    PrecioAgua = valor_unitario * personas_por_arrendatario   # Costo de este apartamen
    
    div = max(1, cantidad_arrendatarios)
    PrecioLuz = LuzValue / div
    PrecioAseo = AseoValue / div
    PrecioGas = GasValue / div
    
    return (PrecioAgua, PrecioLuz, PrecioAseo, PrecioGas)

def limpieza_files(paths: list):
    for p in paths:
        try:
            if os.path.isfile(p):
                os.remove(p)
            elif os.path.isdir(p):
                shutil.rmtree(p)
        except Exception as e:
            print(f"Error eliminando {p}: {e}")

    

@app.on_event("startup")
def startup():
    Db_Arrendatarios()
    


@app.get("/Arrendatarios/")
def obtener_arrendatarios():
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM arrendatarios_J0")
        rows = cur.fetchall()
        conn.close()
        return {"data": [dict(row) for row in rows]}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error obteniendo arrendatarios: {e}")
    


@app.post("/Arrendatarios/", status_code=status.HTTP_201_CREATED)
def crear_proyecto(Arrendatario: Arrendatario):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO arrendatarios_J0 (nombre_arrendatario, nombre_ubicacion, direccion_ubicacion,personas_por_arrendatario, telefono, email)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (Arrendatario.nombre_arrendatario, Arrendatario.nombre_ubicacion, Arrendatario.direccion_ubicacion,Arrendatario.personas_por_arrendatario, Arrendatario.telefono, Arrendatario.email)
        )
        conn.commit()
        new_id = cur.lastrowid
        conn.close()
        return {"message": "Proyecto creado correctamente", "id": new_id, "data": Arrendatario.dict()}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error creando proyecto: {e}")



    
@app.get("/Arrendatarios/{nombre_ubicacion}")
def obtener_arrendatario(nombre_ubicacion: str):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, nombre_arrendatario,nombre_ubicacion,direccion_ubicacion,personas_por_arrendatario  FROM arrendatarios_J0 WHERE nombre_ubicacion = ?", (nombre_ubicacion,))
        conn.commit()
        rows = cur.fetchall()
        conn.close()
        return {"data": [dict(row) for row in rows]}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error obteniendo arrendatarios: {e}")


@app.put("/api/v1/update_data_db/")
def actualizar_arrendatario(arrendatario_id: int, datos: ArrendatarioUpdate):
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute ('SELECT * FROM arrendatarios_J0 WHERE id = ?', (arrendatario_id,))
        exists= cursor.fetchone()

        if not exists:
            raise HTTPException(status_code=404, detail="Arrendatario no encontrado")
        
        cursor.execute(
            """
            UPDATE arrendatarios_J0 
            SET nombre_arrendatario = ?, nombre_ubicacion = ?, direccion_ubicacion = ?, personas_por_arrendatario = ?, telefono = ?, email = ?
            WHERE id = ?
            """,
            (datos.nombre_arrendatario, datos.nombre_ubicacion, datos.direccion_ubicacion, datos.personas_por_arrendatario, datos.telefono, datos.email, arrendatario_id)
        )
        conn.commit()
        conn.close()
        return {"message": "Arrendatario actualizado correctamente"}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error actualizando arrendatario: {e}")

@app.delete("/Arrendatarios/{arrendatario_id}")
def eliminar_arrendatario(arrendatario_id: int):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("DELETE  FROM arrendatarios_J0 WHERE id = ?", (arrendatario_id,))
        conn.commit()
        affected = cur.rowcount
        conn.close()
        if affected == 0:
            raise HTTPException(status_code=404, detail="Arrendatario no encontrado")
        return {"message": "Arrendatario eliminado correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error eliminando arrendatario: {e}")

#Json Reutilizable para preview y Generacion PDF 
def build_preview(WaterValue : int, LuzValue : int, AseoValue : int, GasValue: int, Seleccionador : str) -> dict:
    respuesta = obtener_arrendatario(Seleccionador)
    arrendtario_data = respuesta["data"]  # lista de dicts
    cantidad_arrendatarios = len(arrendtario_data)

    prev_itms = []
    suma_total = 0

    for arr in arrendtario_data: 
        arrendatario_id = arr["id"]
        nombre_arrendatario = arr["nombre_arrendatario"]
        nombre_ubicacion = arr["nombre_ubicacion"]
        direccion_ubicacion = arr["direccion_ubicacion"] 
        personas_por_arrendatario = int(arr.get("personas_por_arrendatario") or 1)

        PrecioAgua, PrecioLuz, PrecioAseo, PrecioGas = calcular_servicios(
            WaterValue, LuzValue,AseoValue, GasValue,
              personas_por_arrendatario,nombre_ubicacion, cantidad_arrendatarios)

        total = PrecioAgua + PrecioLuz + PrecioAseo + PrecioGas
        suma_total += total 
        prev_itms.append({
            "id": arrendatario_id,
            "nombre_arrendatario": nombre_arrendatario,
            "nombre_ubicacion": nombre_ubicacion,
            "direccion_ubicacion": direccion_ubicacion,
            "personas_por_arrendatario": personas_por_arrendatario,
            "servicios": {
                "agua": round(PrecioAgua, 2),
                "luz": round(PrecioLuz, 2),
                "aseo": round(PrecioAseo, 2),
                "gas": round(PrecioGas, 2)
            },
            "total": total
        })

    return {
            "ubicacion" : Seleccionador,
             "arrendatarios" : prev_itms,
             "sum_total"  : suma_total
        }
        

@app.post("/PreviewComprobantes/")
def preview_comprobante_end_point(
    WaterValue: int = Form(...),
    LuzValue: int = Form(...),
    AseoValue: int = Form(...),
    GasValue: int = Form(...),
    Selecionador: str = Form(...)
):

    data = build_preview(WaterValue, LuzValue, AseoValue, GasValue, Selecionador)
    return JSONResponse(content=data) 

@app.post("/api/v1/generar_pdf_editado/")
def generar_pdf_editado(datos: PDFData,    
                        backg : BackgroundTasks = BackgroundTasks()
):
    temp = tempfile.mkdtemp(prefix="comprobantes_")

    zip_filename = f'comprobantes_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
    zip_path = os.path.join(temp, zip_filename)
    archivos = []
    
    for persona in datos.personas:
        #  Acceso directo como atributo (no .get())
        servicios = persona.servicios
        
        #  Convertir lista de objetos Concepto a diccionario
        servicios_dict = {}
        for servicio in servicios:
            descripcion = servicio.descripcion.lower()  #  Atributo directo
            valor = servicio.valor  #  Atributo directo
            servicios_dict[descripcion] = valor
        
        print(f" Servicios para {persona.nombre}: {servicios_dict}")  # 
        
        #  Acceso directo a atributos
        pdf_pth = GenerarComprobantes(
            servicios_dict=servicios_dict,
            nombre_arrendatario=persona.nombre,  # 
            nombre_ubicacion=persona.ubicacion,  # 
            direccion_ubicacion=persona.direccion,  # 
            personas_por_arrendatario=persona.personas_por_arrendatario or 1,  #  s
            output_path=temp    
        )
    
        if not (pdf_pth and os.path.exists(pdf_pth)):
            print(f"PDF faltante para {persona.nombre}: {pdf_pth}")
            continue 

        archivos.append(pdf_pth)
            
    

     # crear zip en temp y añadir archivos existentes


    with zipfile.ZipFile(zip_path, "w") as zipf:
        for file_path in archivos:
            zipf.write(file_path, arcname=os.path.basename(file_path))

    # programar limpieza del directorio temporal completo (zip + pdfs)
    if backg:
        backg.add_task(limpieza_files, [temp])

    return FileResponse(zip_path, media_type="application/zip", filename=zip_filename)




@app.post("/GenerarComprobantes/")
def generar_comprobante_end_point(
    WaterValue: int = Form(...),
    LuzValue: int = Form(...),
    AseoValue: int = Form(...),
    GasValue: int = Form(...),
    Selecionador: str = Form(...), 
    backg : BackgroundTasks = BackgroundTasks()
):   
    temp = tempfile.mkdtemp(prefix="comprobantes_")

    zip_filename = f'comprobantes_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
    zip_path = os.path.join(temp, zip_filename)
    archivos = []

    preview = build_preview(WaterValue, LuzValue, AseoValue, GasValue, Selecionador)


    for entry in preview["arrendatarios"]:
        nombre_arrendatario = entry["nombre_arrendatario"]
        nombre_ubicacion = entry["nombre_ubicacion"]
        direccion_ubicacion = entry["direccion_ubicacion"]
        personas_por_arrendatario = int(entry.get("personas_por_arrendatario") or 1)
        servicios = entry["servicios"]  # ← Ya es un diccionario

        #  CAMBIO: Convertir diccionario de servicios (asegurarse de que tenga descripciones)
        servicios_dict = {
            'agua': servicios.get('agua', 0),
            'luz': servicios.get('luz', 0),
            'aseo': servicios.get('aseo', 0),
            'gas': servicios.get('gas', 0)
        }
        
        print(f"Servicios para {nombre_arrendatario}: {servicios_dict}")

        #  LLAMAR CON servicios_dict (parámetros NUEVOS)
        pdf_path = GenerarComprobantes(
            servicios_dict=servicios_dict,      # CAMBIO PRINCIPAL
            nombre_arrendatario=nombre_arrendatario,
            nombre_ubicacion=nombre_ubicacion,
            direccion_ubicacion=direccion_ubicacion,
            personas_por_arrendatario=personas_por_arrendatario,
            output_path=temp
        )

        # sólo añadir al ZIP si el archivo existe
        if not (pdf_path and  os.path.exists(pdf_path)):
            print(f"PDF faltante para {nombre_arrendatario}: {pdf_path}")
            return
        archivos.append(pdf_path)

    # crear zip en temp y añadir archivos existentes
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for file_path in archivos:
            zipf.write(file_path, arcname=os.path.basename(file_path))

    # programar limpieza del directorio temporal completo (zip + pdfs)
    if backg:
        backg.add_task(limpieza_files, [temp])

    return FileResponse(zip_path, media_type="application/zip", filename=zip_filename)


@app.get("/")  
def read_root():
    J0file = open("J0.html", "r", encoding="utf-8")
    return HTMLResponse(content=J0file.read(), status_code=200)