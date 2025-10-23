import joblib
import pandas as pd
from fastapi import FastAPI, Request, BackgroundTasks
from contextlib import asynccontextmanager

# --- INICIO DE LA ACTUALIZACIÓN ---
# Importamos nuestros propios módulos, AÑADIENDO los de riesgo medio
from api.features import create_features
from api.notifications import (
    send_teacher_alert, 
    send_student_support,
    send_teacher_medium_alert,  # <-- NUEVA IMPORTACIÓN
    send_student_medium_support # <-- NUEVA IMPORTACIÓN
)
from api.schemas import StudentData, AnalysisResponse
# --- FIN DE LA ACTUALIZACIÓN ---


# --- 1. Lógica de Diagnóstico (Sin cambios) ---
def get_diagnostic_and_resource(data_row: pd.Series) -> (str, str):
    """
    Analiza las features de un estudiante en riesgo y devuelve
    un diagnóstico y un recurso de apoyo.
    """
    if data_row.get("fe_mora_flag") == 1:
        diagnostic = "Alto riesgo detectado. Causa principal: **Mora en los pagos**."
        resource = "Link a la Oficina de Bienestar Financiero para discutir opciones de pago."
        return diagnostic, resource

    if data_row.get("fe_pct_aprob_1", 1) < 0.5:
        diagnostic = "Alto riesgo detectado. Causa principal: **Bajo rendimiento en el Semestre 1**."
        resource = "Link al portal de Tutorías Académicas para reforzar cursos."
        return diagnostic, resource
        
    if data_row.get("fe_delta_grade_2_1", 0) < -2:
        diagnostic = "Alto riesgo detectado. Causa principal: **Caída notable en las notas** del Sem1 al Sem2."
        resource = "Link para agendar una cita con Consejería Académica."
        return diagnostic, resource

    diagnostic = "Alto riesgo detectado (combinación de factores)."
    resource = "Link al Manual de Bienestar Estudiantil y Apoyo Psicológico."
    return diagnostic, resource


# --- 2. Carga del Modelo (Sin cambios) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Carga el modelo y el umbral una sola vez y los guarda en 'app.state'.
    """
    print("Iniciando API...")
    model_path = "models/dropout_lgbm_calibrated.joblib"
    threshold_path = "models/threshold_95.txt"
    
    loaded_models = {}
    loaded_models["pipeline"] = joblib.load(model_path)
    with open(threshold_path, 'r') as f:
        loaded_models["threshold"] = float(f.read())
        
    app.state.models = loaded_models
    print("Modelo y Umbral cargados exitosamente.")
    yield
    app.state.models.clear()
    print("API detenida. Modelos limpiados.")


# --- 3. Creación de la Aplicación FastAPI (Sin cambios) ---
app = FastAPI(
    title="Agente de IA - Detección de Deserción",
    description="API para predecir el riesgo de deserción y tomar acciones.",
    version="1.0.0",
    lifespan=lifespan
)

# --- 4. El Endpoint de Predicción (¡ACTUALIZADO!) ---
@app.post("/analyze_student", response_model=AnalysisResponse)
async def analyze_student(student: StudentData, request: Request, background_tasks: BackgroundTasks):
    """
    Recibe los datos de UN estudiante, analiza su riesgo y toma acciones.
    """
    
    # 1. Obtener el modelo y los umbrales
    model = request.app.state.models["pipeline"]
    # Este es tu umbral de ~0.865
    HIGH_RISK_THRESHOLD = request.app.state.models["threshold"] 
    # Este es tu nuevo umbral de 70%
    MEDIUM_RISK_THRESHOLD = 0.70 

    # 2. Convertir los datos de entrada Pydantic a un DataFrame
    student_dict = student.model_dump()
    data_df = pd.DataFrame([student_dict])

    # 3. Aplicar la Ingeniería de Características
    data_with_features = create_features(data_df)

    # 3.5. Renombrar columnas para que coincidan con el modelo entrenado
    column_mapping = {
        'Marital_status': 'Marital status',
        'Application_mode': 'Application mode',
        'Application_order': 'Application order',
        'Daytime_evening_attendance': 'Daytime/evening attendance',
        'Previous_qualification': 'Previous qualification',
        'Previous_qualification_grade': 'Previous qualification (grade)',
        'Nacionality': 'Nacionality',
        'Mothers_qualification': "Mother's qualification",
        'Fathers_qualification': "Father's qualification",
        'Mothers_occupation': "Mother's occupation",
        'Fathers_occupation': "Father's occupation",
        'Admission_grade': 'Admission grade',
        'Educational_special_needs': 'Educational special needs',
        'Debtor': 'Debtor',
        'Tuition_fees_up_to_date': 'Tuition fees up to date',
        'Gender': 'Gender',
        'Scholarship_holder': 'Scholarship holder',
        'Age_at_enrollment': 'Age at enrollment',
        'International': 'International',
        'Curricular_units_1st_sem_credited': 'Curricular units 1st sem (credited)',
        'Curricular_units_1st_sem_enrolled': 'Curricular units 1st sem (enrolled)',
        'Curricular_units_1st_sem_evaluations': 'Curricular units 1st sem (evaluations)',
        'Curricular_units_1st_sem_approved': 'Curricular units 1st sem (approved)',
        'Curricular_units_1st_sem_grade': 'Curricular units 1st sem (grade)',
        'Curricular_units_1st_sem_without_evaluations': 'Curricular units 1st sem (without evaluations)',
        'Curricular_units_2nd_sem_credited': 'Curricular units 2nd sem (credited)',
        'Curricular_units_2nd_sem_enrolled': 'Curricular units 2nd sem (enrolled)',
        'Curricular_units_2nd_sem_evaluations': 'Curricular units 2nd sem (evaluations)',
        'Curricular_units_2nd_sem_approved': 'Curricular units 2nd sem (approved)',
        'Curricular_units_2nd_sem_grade': 'Curricular units 2nd sem (grade)',
        'Curricular_units_2nd_sem_without_evaluations': 'Curricular units 2nd sem (without evaluations)',
        'Unemployment_rate': 'Unemployment rate',
        'Inflation_rate': 'Inflation rate',
        'GDP': 'GDP'
    }

    data_to_predict = data_with_features.rename(columns=column_mapping, errors='ignore')

    # 4. Obtener la probabilidad de riesgo
    risk_prob = model.predict_proba(data_to_predict)[:, 1][0]
    
    # --- INICIO DE LA ACTUALIZACIÓN: Lógica de 3 niveles ---

    # Nivel 1: Alto Riesgo (Acción Urgente)
    if risk_prob >= HIGH_RISK_THRESHOLD:
        prediction_label = "Alto Riesgo"
        diagnostic, resource = get_diagnostic_and_resource(data_with_features.iloc[0])
        action_taken = "Acción: Emails de ALERTA enviados"
        
        background_tasks.add_task(
            send_teacher_alert,
            student_name=student.Student_Name,
            teacher_email=student.Teacher_Email,
            diagnostic_reason=diagnostic
        )
        background_tasks.add_task(
            send_student_support,
            student_name=student.Student_Name,
            student_email=student.Student_Email,
            support_resource=resource
        )
        
    # Nivel 2: Riesgo Medio (Acción Preventiva)
    elif risk_prob >= MEDIUM_RISK_THRESHOLD:
        prediction_label = "Riesgo Medio"
        diagnostic = "Monitoreo preventivo recomendado (Probabilidad: {:.1%})".format(risk_prob)
        action_taken = "Acción: Emails PREVENTIVOS enviados"
        
        background_tasks.add_task(
            send_teacher_medium_alert,
            student_name=student.Student_Name,
            teacher_email=student.Teacher_Email,
            risk_prob=risk_prob
        )
        background_tasks.add_task(
            send_student_medium_support,
            student_name=student.Student_Name,
            student_email=student.Student_Email
        )
        
    # Nivel 3: Bajo Riesgo (Solo Monitoreo)
    else:
        prediction_label = "Bajo Riesgo"
        diagnostic = "N/A"
        action_taken = "Acción: Monitoreo"
    # --- FIN DE LA ACTUALIZACIÓN ---

    # 6. Devolver la respuesta
    return AnalysisResponse(
        student_name=student.Student_Name,
        risk_probability=round(risk_prob, 4),
        prediction_label=prediction_label, # El dashboard ya no usa esto
        action_taken=action_taken,
        diagnostic=diagnostic
    )

@app.get("/")
def read_root():
    return {"status": "Agente de IA está activo y escuchando."}