from pydantic import BaseModel, EmailStr
from typing import Optional

# Este es el "molde" de los datos que SIMULAMOS recibir de la universidad
# Se basa en las columnas de tu notebook + los campos de simulación
# Usamos 'Optional' para ser flexibles si algunos datos no vienen
# El modelo los necesita, pero el preprocesamiento los manejará (fillna)

class StudentData(BaseModel):
    # --- Datos para la simulación (Agente Activo) ---
    Student_Name: str
    Student_Email: EmailStr  # Pydantic valida que sea un email
    Teacher_Email: EmailStr  # Pydantic valida que sea un email
    
    # --- Datos Reales del Modelo (basado en el notebook) ---
    # Usamos 'Optional[float] = None' para permitir valores nulos
    # El modelo de tu notebook ('pre') ya sabe cómo imputarlos
    
    Marital_status: Optional[int] = None
    Application_mode: Optional[int] = None
    Application_order: Optional[int] = None
    Course: Optional[int] = None
    Daytime_evening_attendance: Optional[int] = None
    Previous_qualification: Optional[int] = None
    Previous_qualification_grade: Optional[float] = None
    Nacionality: Optional[int] = None
    Mothers_qualification: Optional[int] = None
    Fathers_qualification: Optional[int] = None
    Mothers_occupation: Optional[int] = None
    Fathers_occupation: Optional[int] = None
    Admission_grade: Optional[float] = None
    Displaced: Optional[int] = None
    Educational_special_needs: Optional[int] = None
    Debtor: Optional[int] = None
    Tuition_fees_up_to_date: Optional[int] = None
    Gender: Optional[int] = None
    Scholarship_holder: Optional[int] = None
    Age_at_enrollment: Optional[int] = None
    International: Optional[int] = None
    Curricular_units_1st_sem_credited: Optional[int] = None
    Curricular_units_1st_sem_enrolled: Optional[int] = None
    Curricular_units_1st_sem_evaluations: Optional[int] = None
    Curricular_units_1st_sem_approved: Optional[int] = None
    Curricular_units_1st_sem_grade: Optional[float] = None
    Curricular_units_1st_sem_without_evaluations: Optional[int] = None
    Curricular_units_2nd_sem_credited: Optional[int] = None
    Curricular_units_2nd_sem_enrolled: Optional[int] = None
    Curricular_units_2nd_sem_evaluations: Optional[int] = None
    Curricular_units_2nd_sem_approved: Optional[int] = None
    Curricular_units_2nd_sem_grade: Optional[float] = None
    Curricular_units_2nd_sem_without_evaluations: Optional[int] = None
    Unemployment_rate: Optional[float] = None
    Inflation_rate: Optional[float] = None
    GDP: Optional[float] = None

# Este es el "molde" de la respuesta que nuestra API enviará
class AnalysisResponse(BaseModel):
    student_name: str
    risk_probability: float
    prediction_label: str  # (Ej: "Alto Riesgo" o "Bajo Riesgo")
    action_taken: str      # (Ej: "Emails enviados" o "Monitoreo")
    diagnostic: str        # (Ej: "Bajo rendimiento en Sem1")