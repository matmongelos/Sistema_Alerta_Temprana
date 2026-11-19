import pytest
from modelo_ia import evaluar_riesgo

# ---------------------------------------------------------
# 1. PARTICIONES DE EQUIVALENCIA (CAJA NEGRA - HU05)
# ---------------------------------------------------------

def test_riesgo_alto_por_carga_laboral_y_brecha_digital():
    # Partición: Alta carga laboral (>=30 hs) + estudio solo en celular
    nivel, factores = evaluar_riesgo(
        trabaja="Sí",
        horas_laborales=35,
        personas_a_cargo="Sí",
        dispositivo="Solo teléfono celular",
        materias_adeudadas=2
    )
    assert nivel == "Alto"
    assert "Alta carga laboral" in factores
    assert "Limitación tecnológica" in factores

def test_riesgo_medio_por_responsabilidades_familiares():
    # Partición: Sin trabajo pero con personas a cargo (puntuación = 2 -> Medio)
    nivel, factores = evaluar_riesgo(
        trabaja="No",
        horas_laborales=0,
        personas_a_cargo="Sí",
        dispositivo="PC de escritorio / Notebook",
        materias_adeudadas=0
    )
    assert nivel == "Medio"
    assert "Personas a cargo" in factores

def test_riesgo_bajo_dedicacion_exclusiva():
    # Partición: Estudiante sin factores críticos (puntuación = 0 -> Bajo)
    nivel, factores = evaluar_riesgo(
        trabaja="No",
        horas_laborales=0,
        personas_a_cargo="No",
        dispositivo="PC de escritorio / Notebook",
        materias_adeudadas=0
    )
    assert nivel == "Bajo"
    assert "Sin factores de riesgo críticos detectados" in factores

# ---------------------------------------------------------
# 2. ANÁLISIS DE VALORES LÍMITE (BORDES DE REGLAS)
# ---------------------------------------------------------

def test_valor_limite_exacto_30_horas_laborales():
    # Borde superior: exactamente 30 horas suma 3 puntos + 1 materia (1 pt) = 4 pts (Alto)
    nivel, factores = evaluar_riesgo(
        trabaja="Sí",
        horas_laborales=30,
        personas_a_cargo="No",
        dispositivo="PC de escritorio / Notebook",
        materias_adeudadas=1
    )
    assert nivel == "Alto"
    assert "Alta carga laboral (≥30 hs/semana)" in factores

def test_valor_limite_29_horas_laborales():
    # Justo debajo del límite (29 hs suma 1 punto + 1 materia 1 pt = 2 pts -> Medio)
    nivel, factores = evaluar_riesgo(
        trabaja="Sí",
        horas_laborales=29,
        personas_a_cargo="No",
        dispositivo="PC de escritorio / Notebook",
        materias_adeudadas=1
    )
    assert nivel == "Medio"
    assert "Carga laboral moderada" in factores

# ---------------------------------------------------------
# 3. CONTINGENCIA Y TOLERANCIA A FALLOS (CAJA BLANCA - HU06)
# ---------------------------------------------------------

def test_contingencia_hu06_datos_corruptos():
    # Entrada inválida (texto no numérico en horas) debe capturar excepción sin romper
    nivel, mensaje = evaluar_riesgo(
        trabaja="Sí",
        horas_laborales="dato_corrupto",
        personas_a_cargo="No",
        dispositivo="PC de escritorio / Notebook",
        materias_adeudadas=0
    )
    assert nivel == "No disponible"
    assert mensaje == "Predicción no disponible temporalmente"