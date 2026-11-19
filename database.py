import sqlite3
import pandas as pd

DB_NAME = "alerta_temprana.db"

def init_db():
    """Crea la tabla de estudiantes e intervenciones si no existen."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Tabla principal de estudiantes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS estudiantes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            legajo TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            carrera TEXT NOT NULL,
            trabaja TEXT NOT NULL,
            horas_laborales INTEGER NOT NULL,
            personas_a_cargo TEXT NOT NULL,
            dispositivo TEXT NOT NULL,
            materias_adeudadas INTEGER NOT NULL,
            dificultades TEXT,
            estado_seguimiento TEXT DEFAULT 'Sin contactar',
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Intento de agregar la columna si la tabla existía previamente
    try:
        cursor.execute("ALTER TABLE estudiantes ADD COLUMN estado_seguimiento TEXT DEFAULT 'Sin contactar'")
    except sqlite3.OperationalError:
        pass
        
    # Tabla de intervenciones tutoriales (HU07)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS intervenciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            legajo TEXT NOT NULL,
            tutor_nombre TEXT NOT NULL,
            observaciones TEXT NOT NULL,
            acciones_tomadas TEXT NOT NULL,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (legajo) REFERENCES estudiantes(legajo)
        )
    ''')
    conn.commit()
    conn.close()

def guardar_estudiante(legajo, nombre, carrera, trabaja, horas_laborales, personas_a_cargo, dispositivo, materias_adeudadas, dificultades):
    """Inserta las respuestas de la encuesta en la base de datos."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO estudiantes (legajo, nombre, carrera, trabaja, horas_laborales, personas_a_cargo, dispositivo, materias_adeudadas, dificultades)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (legajo, nombre, carrera, trabaja, horas_laborales, personas_a_cargo, dispositivo, materias_adeudadas, dificultades))
        conn.commit()
        return True, "Sus datos han sido guardados exitosamente en el sistema."
    except sqlite3.IntegrityError:
        return False, "El número de Legajo / DNI ingresado ya se encuentra registrado en el sistema."
    finally:
        conn.close()

def obtener_estudiantes():
    """Recupera todos los registros de la base de datos."""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT legajo, nombre, carrera, trabaja, horas_laborales, personas_a_cargo, dispositivo, materias_adeudadas, dificultades, estado_seguimiento, fecha_registro FROM estudiantes", conn)
    conn.close()
    return df

def actualizar_estado_estudiante(legajo, nuevo_estado):
    """Actualiza el estado manual de acompañamiento del estudiante (HU08)."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE estudiantes SET estado_seguimiento = ? WHERE legajo = ?', (nuevo_estado, legajo))
    conn.commit()
    conn.close()

def guardar_intervencion(legajo, tutor_nombre, observaciones, acciones_tomadas):
    """Registra una entrevista u observación tutorial (HU07)."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO intervenciones (legajo, tutor_nombre, observaciones, acciones_tomadas)
        VALUES (?, ?, ?, ?)
    ''', (legajo, tutor_nombre, observaciones, acciones_tomadas))
    conn.commit()
    conn.close()

def obtener_intervenciones(legajo):
    """Recupera el historial de intervenciones de un estudiante determinado."""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT fecha_registro as Fecha, tutor_nombre as Tutor, observaciones as Observaciones, acciones_tomadas as 'Acciones Acordadas' FROM intervenciones WHERE legajo = ? ORDER BY fecha_registro DESC", conn, params=(legajo,))
    conn.close()
    return df