import streamlit as st
import pandas as pd
import requests
import json
import time

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Agente de IA - Deserción Estudiantil",
    page_icon="🤖",
    layout="wide"
)

# Título del Dashboard
st.title("🤖 Centro de Comando del Agente de IA")
st.markdown("Carga el reporte de alumnos para que el agente analice el riesgo y tome acciones.")

# URL de nuestra API (Backend) que está corriendo en http://127.0.0.1:8000
API_URL = "http://127.0.0.1:8000/analyze_student"

# --- Paso 1: Carga del Archivo ---
st.header("Paso 1: Cargar Reporte de Alumnos")
uploaded_file = st.file_uploader("Selecciona un archivo CSV", type="csv")

if uploaded_file is not None:
    try:
        # Leer el CSV
        df = pd.read_csv(uploaded_file)
        st.success(f"Archivo '{uploaded_file.name}' cargado exitosamente.")
        st.dataframe(df.head(), use_container_width=True)

        # --- Paso 2: Botón de Activación ---
        st.header("Paso 2: Activar el Agente")
        if st.button("🚨 Iniciar Agente", type="primary"):
            
            students_data = json.loads(df.to_json(orient='records'))
            total_students = len(students_data)
            st.write(f"Iniciando análisis para {total_students} estudiantes...")

            progress_bar = st.progress(0, text="Analizando...")
            results = []
            
            # --- Paso 3: Llamar a la API para CADA estudiante ---
            for i, student in enumerate(students_data):
                try:
                    response = requests.post(API_URL, json=student)
                    if response.status_code == 200:
                        results.append(response.json())
                    else:
                        st.error(f"Error al analizar a {student.get('Student_Name', 'N/A')}: {response.text}")
                        results.append({
                            "student_name": student.get('Student_Name', 'N/A'),
                            "prediction_label": "Error de Análisis",
                            "risk_probability": 0, "diagnostic": response.text, "action_taken": "N/A"
                        })
                except Exception as e:
                    st.error(f"Error de conexión con la API al procesar a {student.get('Student_Name', 'N/A')}: {e}")
                    results.append({
                        "student_name": student.get('Student_Name', 'N/A'),
                        "prediction_label": "Error de Conexión",
                        "risk_probability": 0, "diagnostic": str(e), "action_taken": "N/A"
                    })

                percent_complete = (i + 1) / total_students
                progress_bar.progress(percent_complete, text=f"Analizando: {student.get('Student_Name', 'N/A')}")
                time.sleep(0.01)

            progress_bar.empty()
            st.success("¡Análisis completado! El agente ha tomado acciones.")

            # --- Paso 4: Mostrar Resultados (CON RIESGO MEDIO) ---
            st.header("Paso 3: Revisar Resultados y Diagnósticos")
            
            results_df = pd.DataFrame(results)
            results_df = results_df.sort_values(by="risk_probability", ascending=False)

            # --- Lógica de Estilo (con colores fuertes) ---
            try:
                with open("models/threshold_95.txt", 'r') as f:
                    HIGH_RISK_THRESHOLD = float(f.read()) # ~0.865
            except FileNotFoundError:
                st.warning("No se encontró 'models/threshold_95.txt'. Usando umbral por defecto (86.5%).")
                HIGH_RISK_THRESHOLD = 0.865 

            MEDIUM_RISK_THRESHOLD = 0.70 # Tu 70%

            def define_risk_level(prob):
                if prob >= HIGH_RISK_THRESHOLD:
                    return "Alto Riesgo"
                if prob >= MEDIUM_RISK_THRESHOLD:
                    return "Riesgo Medio"
                return "Bajo Riesgo"

            # --- INICIO DE LA CORRECCIÓN DE COLOR ---
            def style_risk_rows(row):
                prob = row['risk_probability']
                if prob >= HIGH_RISK_THRESHOLD:
                    # Rojo más fuerte
                    return ['background-color: #ef9a9a'] * len(row) 
                if prob >= MEDIUM_RISK_THRESHOLD:
                    # Naranja/Amarillo más fuerte
                    return ['background-color: #ffb74d'] * len(row) 
                return [''] * len(row)
            # --- FIN DE LA CORRECCIÓN DE COLOR ---

            results_df['Nivel de Riesgo'] = results_df['risk_probability'].apply(define_risk_level)
            
            columns_order = [
                'student_name', 'Nivel de Riesgo', 'risk_probability', 
                'action_taken', 'diagnostic'
            ]
            final_columns = [col for col in columns_order if col in results_df.columns]
            results_df_display = results_df[final_columns]

            # Objeto de estilo
            styled_df = results_df_display.style.apply(style_risk_rows, axis=1)\
                                              .format({"risk_probability": "{:.2%}"})

            # Usamos st.table() que SÍ respeta los estilos de fondo.
            st.table(styled_df)

            # --- Extra: Expanders para diagnósticos ---
            st.subheader("Diagnósticos de Alumnos en Riesgo:")
            
            at_risk_students = results_df[
                (results_df["Nivel de Riesgo"] == "Alto Riesgo") |
                (results_df["Nivel de Riesgo"] == "Riesgo Medio")
            ]
            
            if at_risk_students.empty:
                st.info("No se encontraron estudiantes con riesgo Alto o Medio en este reporte.")
            else:
                for _, row in at_risk_students.iterrows():
                    icon = "🚨" if row['Nivel de Riesgo'] == "Alto Riesgo" else "⚠️"
                    with st.expander(f"{icon} **{row['student_name']}** - {row['Nivel de Riesgo']} ({row['risk_probability']:.2%})"):
                        st.write(f"**Diagnóstico del Agente:** {row['diagnostic']}")
                        st.write(f"**Acción Tomada:** {row['action_taken']}")

    except Exception as e:
        st.error(f"Error al leer el archivo CSV. Asegúrate de que el formato sea correcto. Detalle: {e}")