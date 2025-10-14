import shutil
import sqlite3
import traceback
from xmlrpc import client
from fastapi.responses import JSONResponse
from fastapi import FastAPI, HTTPException, status,Form, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
limiter = Limiter(key_func=get_remote_address)
from models.ClaseArrendatario import Arrendatario
from  recexamples import *
from fastapi.responses import FileResponse
import tempfile
import zipfile
import os

# Inicializar la app de FastAPI
app = FastAPI(title="Actividad Microsite API")


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

def calcular_servicios (WaterValue:int, LuzValue: int, AseoValue:int, GasValue:int, personas_por_arrendatario:int, headcounttotales_por_arr:int, Arrendatarios:int):

    valor_unitario = WaterValue / headcounttotales_por_arr
    PrecioAgua = valor_unitario * personas_por_arrendatario
  
    PrecioLuz = LuzValue / Arrendatarios
    PrecioAseo = AseoValue / Arrendatarios
    PrecioGas = GasValue / Arrendatarios

    return (PrecioAgua, PrecioLuz, PrecioAseo, PrecioGas)

def limpieza_files(paths: list):
    for p in paths: 
        try:  
            if os.path.isfile(p):
                os.remove(p)
            else: 
                os.path.isdir(p)
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
        cur.execute("SELECT nombre_arrendatario,nombre_ubicacion,direccion_ubicacion,personas_por_arrendatario  FROM arrendatarios_J0 WHERE nombre_ubicacion = ?", (nombre_ubicacion,))
        conn.commit()
        rows = cur.fetchall()
        conn.close()
        return {"data": [dict(row) for row in rows]}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error obteniendo arrendatarios: {e}")




@app.delete("/Arrendatarios/{arrendatario_id}")
def eliminar_arrendatario(arrendatario_id: int):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("DELETE * FROM arrendatarios_J0 WHERE id = ?", (arrendatario_id,))
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



@app.post("/GenerarComprobantes/")
def generar_comprobante_end_point(
    WaterValue: int = Form(...),
    LuzValue: int = Form(...),
    AseoValue: int = Form(...),
    GasValue: int = Form(...),
    Arrendatarios: int = Form(...),
    Selecionador: str = Form(...),
    backg = BackgroundTasks
):   
    temp= tempfile.mkdtemp(prefix="comprobantes_")


    archivos = []
    respuesta = obtener_arrendatario(Selecionador)

    arrendatario_data = respuesta["data"]  # recupera los datos del arrendatario seleccionado


    
    headcounttotales_por_arr = sum(arrendatario["personas_por_arrendatario"] for arrendatario in arrendatario_data)



    for arrendatario in arrendatario_data:  #Blucle para cada arrendatario y extraer sus datos
        nombre_arrendatario = arrendatario["nombre_arrendatario"]
        nombre_ubicacion = arrendatario["nombre_ubicacion"]
        direccion_ubicacion = arrendatario["direccion_ubicacion"]
        personas_por_arrendatario = arrendatario.get("personas_por_arrendatario")



       

        PrecioAgua, PrecioLuz, PrecioAseo, PrecioGas = calcular_servicios(
            WaterValue,LuzValue,AseoValue,GasValue,personas_por_arrendatario,headcounttotales_por_arr,Arrendatarios        )

        
        archivopdf = f"{nombre_arrendatario}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"  # Crea un archivo PDF único por arrendatario   

        GenerarComprobantes(WaterValue=PrecioAgua, LuzValue=PrecioLuz, AseoValue=PrecioAseo, GasValue=PrecioGas,nombre_arrendatario=nombre_arrendatario,
        nombre_ubicacion=nombre_ubicacion,
        direccion_ubicacion=direccion_ubicacion,personas_por_arrendatario=personas_por_arrendatario,Arrendatarios=Arrendatarios)


        archivos.append(archivopdf)
    zip_path = os.path.join(temp, zip_filename) 
    zip_filename = f"comprobantes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    

    with zipfile.ZipFile(zip_path, "w") as zipf:
            for archivo in archivos:
                zipf.write(archivo)

    backg.add_task(limpieza_files, [zip_path,temp,*archivos])            
    return FileResponse(zip_path,media_type="application/zip", filename=zip_path)


@app.get("/")  
def read_root():
    J0file = open("J0.html", "r", encoding="utf-8")
    return HTMLResponse(content=J0file.read(), status_code=200)