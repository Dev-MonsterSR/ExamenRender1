from flask import Flask, render_template, request, redirect, url_for
import os
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__, template_folder="templates", static_folder="static")

DEFAULT_DATABASE_URL = (
    "postgresql://test_evpi_user:gL9QBEDzoZ1RQkhHPfLDMjMXsdbPUK3i"
    "@dpg-d71v6ovdiees73c23ol0-a.oregon-postgres.render.com/test_evpi?sslmode=require"
)
DATABASE_URL = os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)


def conectar_db():
    return psycopg2.connect(DATABASE_URL)


def inicializar_tabla():
    query = """
    CREATE TABLE IF NOT EXISTS personas (
        id SERIAL PRIMARY KEY,
        dni VARCHAR(20) NOT NULL,
        nombre VARCHAR(100) NOT NULL,
        apellido VARCHAR(100) NOT NULL,
        direccion TEXT,
        telefono VARCHAR(20)
    );
    """
    with conectar_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
        conn.commit()


def crear_persona(dni, nombre, apellido, direccion, telefono):
    query = """
    INSERT INTO personas (dni, nombre, apellido, direccion, telefono)
    VALUES (%s, %s, %s, %s, %s)
    """
    with conectar_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (dni, nombre, apellido, direccion, telefono))
        conn.commit()


def obtener_registros():
    query = """
    SELECT id, dni, nombre, apellido, direccion, telefono
    FROM personas
    ORDER BY id DESC
    """
    with conectar_db() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query)
            return cursor.fetchall()


def eliminar_persona(persona_id):
    with conectar_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM personas WHERE id = %s", (persona_id,))
        conn.commit()


@app.route("/")
def index():
    mensaje = request.args.get("mensaje", "")
    return render_template("index.html", mensaje=mensaje)


@app.route("/registrar", methods=["POST"])
def registrar():
    dni = request.form.get("dni", "").strip()
    nombre = request.form.get("nombre", "").strip()
    apellido = request.form.get("apellido", "").strip()
    direccion = request.form.get("direccion", "").strip()
    telefono = request.form.get("telefono", "").strip()

    if not dni or not nombre or not apellido:
        return redirect(url_for("index", mensaje="Complete los campos obligatorios."))

    crear_persona(dni, nombre, apellido, direccion, telefono)
    return redirect(url_for("index", mensaje="Registro exitoso."))


@app.route("/administrar")
def administrar():
    registros = obtener_registros()
    return render_template("administrar.html", registros=registros)


@app.route("/eliminar/<int:persona_id>", methods=["POST"])
def eliminar_registro(persona_id):
    eliminar_persona(persona_id)
    return redirect(url_for("administrar"))


if __name__ == "__main__":
    inicializar_tabla()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
