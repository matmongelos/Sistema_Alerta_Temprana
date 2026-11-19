def evaluar_riesgo(trabaja, horas_laborales, personas_a_cargo, dispositivo, materias_adeudadas):
    
    """
    Evalúa el nivel de riesgo de deserción (Alto, Medio, Bajo) 
     e incluye tolerancia a fallos y contingencia (HU06).
    """
    try:
        
    
        # Conversión y validación defensiva de tipos de datos
        horas_laborales = int(horas_laborales) if horas_laborales is not None else 0
        materias_adeudadas = int(materias_adeudadas) if materias_adeudadas is not None else 0
        
        factores = []
        puntuacion_riesgo = 0

        # 1. Carga laboral
        if horas_laborales >= 30:
            puntuacion_riesgo += 3
            factores.append("Alta carga laboral (≥30 hs/semana)")
        elif horas_laborales > 0:
            puntuacion_riesgo += 1
            factores.append("Carga laboral moderada")

        # 2. Responsabilidades familiares
        if personas_a_cargo == "Sí":
            puntuacion_riesgo += 2
            factores.append("Personas a cargo (responsabilidades de cuidado)")

        # 3. Equipamiento / Brecha digital
        if dispositivo == "Solo teléfono celular":
            puntuacion_riesgo += 3
            factores.append("Limitación tecnológica (Estudio exclusivo en Smartphone)")
        elif dispositivo == "Tablet / Otro":
            puntuacion_riesgo += 1

        # 4. Situación académica previa
        if materias_adeudadas >= 2:
            puntuacion_riesgo += 2
            factores.append(f"Rezago académico alto ({materias_adeudadas} materias adeudadas)")
        elif materias_adeudadas == 1:
            puntuacion_riesgo += 1
            factores.append("Adeuda 1 materia")

        # Clasificación final
        if puntuacion_riesgo >= 4:
            nivel = "Alto"
        elif puntuacion_riesgo >= 2:
            nivel = "Medio"
        else:
            nivel = "Bajo"
            if not factores:
                factores.append("Sin factores de riesgo críticos detectados")

        return nivel, ", ".join(factores)

    except Exception:
        # Contingencia ante cualquier fallo o inconsistencia de datos (HU06)
        return "No disponible", "Predicción no disponible temporalmente"