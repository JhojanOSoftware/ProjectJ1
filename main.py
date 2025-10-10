import sqlite3
import traceback
from xmlrpc import client
from fastapi.responses import JSONResponse
from fastapi import FastAPI, HTTPException, status,Form
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
limiter = Limiter(key_func=get_remote_address)
from ClaseArrendatario import Arrendatario
from  recexamples import *
from fastapi.responses import FileResponse

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

DB_FILE = "J0BaseDatos.db"


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
            telefono TEXT,
            email TEXT
        )
    """)
    
    
    conn.commit()
    conn.close()


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
            INSERT INTO arrendatarios_J0 (nombre_arrendatario, nombre_ubicacion, direccion_ubicacion, telefono, email)
            VALUES (?, ?, ?, ?, ?)
            """,
            (Arrendatario.nombre_arrendatario, Arrendatario.nombre_ubicacion, Arrendatario.direccion_ubicacion, Arrendatario.telefono, Arrendatario.email)
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
        cur.execute("SELECT nombre_arrendatario,nombre_ubicacion,direccion_ubicacion  FROM arrendatarios_J0 WHERE nombre_ubicacion = ?", (nombre_ubicacion,))
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
        cur.execute("DELETE FROM arrendatarios_J0 WHERE id = ?", (arrendatario_id,))
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
def generar_comprobante(
    WaterValue: int = Form(...),
    LuzValue: int = Form(...),
    AseoValue: int = Form(...),
    GasValue: int = Form(...),
    Arrendatarios: int = Form(...),
    Selecionador: str = Form(...)
):
    respuesta = obtener_arrendatario(Selecionador)
    arrendatario_data = respuesta["data"][0]  # el primer resultado

    nombre_arrendatario = arrendatario_data["nombre_arrendatario"]
    nombre_ubicacion = arrendatario_data["nombre_ubicacion"]
    direccion_ubicacion = arrendatario_data["direccion_ubicacion"]
    GenerarComprobantes(WaterValue=WaterValue, LuzValue=LuzValue, AseoValue=AseoValue, GasValue=GasValue,nombre_arrendatario=nombre_arrendatario,
        nombre_ubicacion=nombre_ubicacion,
        direccion_ubicacion=direccion_ubicacion,Arrendatarios=Arrendatarios)
    return FileResponse("sample_receipt_advanced.pdf", media_type="application/pdf")


@app.get("/")  
def read_root():
    J0file = open("J0.html", "r", encoding="utf-8")
    return HTMLResponse(content=J0file.read(), status_code=200)