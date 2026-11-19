import streamlit as st
import pandas as pd
from database import (
    init_db, guardar_estudiante, obtener_estudiantes, 
    actualizar_estado_estudiante, guardar_intervencion, obtener_intervenciones
)
from modelo_ia import evaluar_riesgo

# Configuración inicial de la página
st.set_page_config(page_title="Sistema de Alerta Temprana", page_icon="🎓", layout="wide")

# Inicializar la base de datos SQLite
init_db()

# Barra lateral para navegación
st.sidebar.title("Navegación del Sistema")
rol = st.sidebar.radio("Seleccione su Perfil:", ["Estudiante", "Tutor (Acceso Restringido)"])

# ---------------------------------------------------------
# PANTALLA 1: ESTUDIANTE (HU01)
# ---------------------------------------------------------
if rol == "Estudiante":
    st.title("📝 Formulario de Situación Académica y Socioeconómica")
    st.info("Complete sus datos para que el equipo de tutorías pueda brindarle un mejor acompañamiento.")
    
    with st.form("formulario_ingreso"):
        st.subheader("1. Datos Personales y Académicos")
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre y Apellido *")
            carrera = st.selectbox("Carrera *", ["Ciencia de Datos", "Análisis de Sistemas", "Otra"])
        with col2:
            legajo = st.text_input("Número de Legajo / DNI *")
            
        st.subheader("2. Situación Socioeconómica, Laboral y Tecnológica")
        col3, col4 = st.columns(2)
        with col3:
            trabaja = st.radio("¿Trabaja actualmente?", ["No", "Sí"])
            personas_a_cargo = st.radio("¿Tiene personas a cargo? (hijos, familiares, etc.)", ["No", "Sí"])
        with col4:
            horas_laborales = st.number_input("Horas laborales semanales", min_value=0, max_value=80, value=0)
            dispositivo = st.selectbox(
                "Dispositivo principal para estudiar *",
                ["PC de escritorio / Notebook", "Solo teléfono celular", "Tablet / Otro"]
            )
            
        st.subheader("3. Situación Académica y Dificultades")
        materias_adeudadas = st.number_input("Materias adeudadas (secundario o correlativas) *", min_value=0, max_value=20, value=0)
        dificultades = st.text_area("Dificultades percibidas (Ej. tiempos de traslado, falta de hábito de estudio, mala conectividad)")
        
        st.markdown("*Campos obligatorios")
        
        submit = st.form_submit_button("Enviar Datos y Registrarse")
        
        if submit:
            if not nombre or not legajo:
                st.error("⚠️ Por favor, complete todos los campos obligatorios (Nombre y Legajo).")
            else:
                exito, mensaje = guardar_estudiante(
                    legajo=legajo,
                    nombre=nombre,
                    carrera=carrera,
                    trabaja=trabaja,
                    horas_laborales=horas_laborales,
                    personas_a_cargo=personas_a_cargo,
                    dispositivo=dispositivo,
                    materias_adeudadas=materias_adeudadas,
                    dificultades=dificultades
                )
                if exito:
                    st.success(f"✅ ¡Gracias {nombre}! {mensaje}")
                else:
                    st.warning(f"⚠️ {mensaje}")

# ---------------------------------------------------------
# PANTALLAS 2 Y 3: TUTOR (HU02, HU03, HU04, HU05, HU07, HU08)
# ---------------------------------------------------------
elif rol == "Tutor (Acceso Restringido)":
    st.title("🛡️ Plataforma de Gestión y Seguimiento Tutorial")
    
    df_estudiantes = obtener_estudiantes()
    
    if df_estudiantes.empty:
        st.info("No hay estudiantes registrados en la base de datos hasta el momento.")
    else:
        # Calcular el Riesgo IA y Factores para cada estudiante
        riesgos = []
        factores_lista = []
        
        for idx, row in df_estudiantes.iterrows():
            nivel, factores = evaluar_riesgo(
                trabaja=row['trabaja'],
                horas_laborales=row['horas_laborales'],
                personas_a_cargo=row['personas_a_cargo'],
                dispositivo=row['dispositivo'],
                materias_adeudadas=row['materias_adeudadas']
            )
            riesgos.append(nivel)
            factores_lista.append(factores)
            
        df_estudiantes['Nivel de Riesgo (IA)'] = riesgos
        df_estudiantes['Factores Determinantes'] = factores_lista
        
        # --- BLOQUE DE BÚSQUEDA Y FILTRADO (HU03) ---
        st.subheader("👥 Listado General de Estudiantes")
        col_filtro1, col_filtro2, col_filtro3 = st.columns(3, vertical_alignment="bottom")
        with col_filtro1:
            busqueda = st.text_input("🔍 Buscar por Nombre o Legajo:")
        with col_filtro2:
            filtro_carrera = st.selectbox("Filtrar por Carrera:", ["Todas", "Ciencia de Datos", "Análisis de Sistemas", "Otra"])
        with col_filtro3:
            filtro_riesgo = st.selectbox("Filtrar por Nivel de Riesgo (IA):", ["Todos", "Alto", "Medio", "Bajo"])
            
        # Aplicar filtros
        df_filtrado = df_estudiantes.copy()
        
        if busqueda:
            df_filtrado = df_filtrado[
                df_filtrado['nombre'].str.contains(busqueda, case=False, na=False) | 
                df_filtrado['legajo'].str.contains(busqueda, case=False, na=False)
            ]
            
        if filtro_carrera != "Todas":
            df_filtrado = df_filtrado[df_filtrado['carrera'] == filtro_carrera]
            
        if filtro_riesgo != "Todos":
            df_filtrado = df_filtrado[df_filtrado['Nivel de Riesgo (IA)'] == filtro_riesgo]
            
        st.caption(f"Mostrando {len(df_filtrado)} de {len(df_estudiantes)} estudiantes registrados.")
        
        # Mostrar tabla interactiva (HU02)
        st.dataframe(
            df_filtrado[[
                'legajo', 'nombre', 'carrera', 'Nivel de Riesgo (IA)', 
                'estado_seguimiento', 'Factores Determinantes', 'trabaja', 
                'horas_laborales', 'personas_a_cargo', 'dispositivo'
            ]],
            use_container_width=True
        )
        
        st.markdown("---")
        
        # --- BLOQUE DE FICHA INDIVIDUAL Y SEGUIMIENTO (HU04, HU07, HU08) ---
        st.subheader("🔍 Ficha Individual del Estudiante y Registro de Seguimiento")
        
        # Selector de estudiante para ver detalle
        opciones_estudiantes = df_estudiantes.apply(lambda r: f"{r['legajo']} - {r['nombre']}", axis=1).tolist()
        estudiante_seleccionado = st.selectbox("Seleccione un estudiante para consultar o intervenir:", opciones_estudiantes)
        
        if estudiante_seleccionado:
            legajo_sel = estudiante_seleccionado.split(" - ")[0]
            est_data = df_estudiantes[df_estudiantes['legajo'] == legajo_sel].iloc[0]
            
            # Encabezado con datos generales
            st.markdown(f"### 👤 {est_data['nombre']} (Legajo: `{est_data['legajo']}`)")
            
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            col_m1.metric("Carrera", est_data['carrera'])
            col_m2.metric("Trabaja", f"{est_data['trabaja']} ({est_data['horas_laborales']} hs/sem)")
            col_m3.metric("Personas a Cargo", est_data['personas_a_cargo'])
            col_m4.metric("Dispositivo", est_data['dispositivo'])
            
           # Bloque de Alerta de IA (HU05 y HU06)
            nivel_r = est_data['Nivel de Riesgo (IA)']
            factores_r = est_data['Factores Determinantes']
            
            if nivel_r == "Alto":
                st.error(f"🚨 **ALERTA DE IA: NIVEL DE RIESGO ALTO**\n\n**Factores determinantes:** {factores_r}")
            elif nivel_r == "Medio":
                st.warning(f"⚠️ **ALERTA DE IA: NIVEL DE RIESGO MEDIO**\n\n**Factores determinantes:** {factores_r}")
            elif nivel_r == "Bajo":
                st.success(f"✅ **EVALUACIÓN DE IA: NIVEL DE RIESGO BAJO**\n\n**Factores determinantes:** {factores_r}")
            else:
                st.info(f"ℹ️ **ESTADO DE SERVICIO IA:** {factores_r}")
                
            st.markdown(f"**Dificultades reportadas por el estudiante:** {est_data['dificultades'] if est_data['dificultades'] else 'Ninguna declarada.'}")
            
            st.markdown("---")
            
            # Pestañas para Organización de Seguimiento (HU07 y HU08)
            tab1, tab2 = st.tabs(["📝 Registrar Nueva Intervención (HU07)", "⚙️ Actualizar Estado de Acompañamiento (HU08)"])
            
            with tab1:
                st.write("**Formulario de Registro de Entrevista / Contacto Tutorial**")
                with st.form("form_intervencion"):
                    tutor_nombre = st.text_input("Nombre del Tutor Responsable *", value="Lic. Laura Gómez")
                    observaciones = st.text_area("Observaciones de la entrevista / diagnóstico *")
                    acciones_tomadas = st.text_area("Acciones acordadas / Plan de trabajo *")
                    
                    submit_int = st.form_submit_button("Guardar Intervención")
                    if submit_int:
                        if not tutor_nombre or not observaciones or not acciones_tomadas:
                            st.error("⚠️ Complete todos los campos requeridos para guardar la intervención.")
                        else:
                            guardar_intervencion(legajo_sel, tutor_nombre, observaciones, acciones_tomadas)
                            st.success("✅ Intervención registrada exitosamente.")
                            st.rerun()
                            
                st.markdown("#### 📜 Historial de Intervenciones Registradas")
                df_intervenciones = obtener_intervenciones(legajo_sel)
                if df_intervenciones.empty:
                    st.info("No hay intervenciones registradas para este estudiante aún.")
                else:
                    st.dataframe(df_intervenciones, use_container_width=True)
                    
            with tab2:
                st.write("**Cambio Manual de Estado de Acompañamiento**")
                estados_posibles = ["Sin contactar", "En Plan de Acción", "En Seguimiento", "Acompañamiento Finalizado / Resuelto"]
                index_actual = estados_posibles.index(est_data['estado_seguimiento']) if est_data['estado_seguimiento'] in estados_posibles else 0
                
                nuevo_estado = st.selectbox("Seleccione el nuevo estado:", estados_posibles, index=index_actual)
                if st.button("Actualizar Estado"):
                    actualizar_estado_estudiante(legajo_sel, nuevo_estado)
                    st.success(f"✅ Estado del estudiante actualizado a: **{nuevo_estado}**")
                    st.rerun()