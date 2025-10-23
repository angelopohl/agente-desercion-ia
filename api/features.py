import pandas as pd
import numpy as np

def create_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Toma un DataFrame con los datos en crudo de la universidad y
    crea las características (features) de ingeniería que el modelo espera.
    
    Esta función AHORA USA LOS NOMBRES "LIMPIOS" de la API (ej. 'Age_at_enrollment')
    """
    # Hacemos una copia para evitar advertencias de SettingWithCopyWarning
    Xn = df.copy()

    # --- Creación de Características (Lógica del Notebook) ---
    # Usamos .get() en caso de que la columna sea opcional en el JSON
    
    # 1. Porcentaje de aprobación Semestre 1
    # Nota: pd.Series(1) es diferente de int(1). Usamos .get con un default Series.
    # La forma más segura es verificar la columna primero.
    
    if "Curricular_units_1st_sem_approved" in Xn and "Curricular_units_1st_sem_enrolled" in Xn:
        Xn["fe_pct_aprob_1"] = Xn["Curricular_units_1st_sem_approved"] / Xn["Curricular_units_1st_sem_enrolled"]
    else:
        Xn["fe_pct_aprob_1"] = 0

    # 2. Porcentaje de aprobación Semestre 2
    if "Curricular_units_2nd_sem_approved" in Xn and "Curricular_units_2nd_sem_enrolled" in Xn:
        Xn["fe_pct_aprob_2"] = Xn["Curricular_units_2nd_sem_approved"] / Xn["Curricular_units_2nd_sem_enrolled"]
    else:
        Xn["fe_pct_aprob_2"] = 0

    # 3. Diferencia de notas Semestre 2 vs 1
    if "Curricular_units_2nd_sem_grade" in Xn and "Curricular_units_1st_sem_grade" in Xn:
        Xn["fe_delta_grade_2_1"] = Xn["Curricular_units_2nd_sem_grade"] - Xn["Curricular_units_1st_sem_grade"]
    else:
        Xn["fe_delta_grade_2_1"] = 0

    # 4. Total de unidades aprobadas
    # (Esta lógica busca 'approved' en los nombres limpios, lo cual no funcionará)
    # La rehacemos para que sea explícita:
    apro_cols = [
        "Curricular_units_1st_sem_approved", 
        "Curricular_units_2nd_sem_approved"
    ]
    # Sumamos solo las columnas que SÍ existen en el DataFrame
    Xn["fe_total_aprob"] = Xn[Xn.columns.intersection(apro_cols)].sum(axis=1)


    # 5. Indicador de Mora (Deuda)
    if "Tuition_fees_up_to_date" in Xn:
        Xn["fe_mora_flag"] = (Xn["Tuition_fees_up_to_date"] == 0).astype(int)
    else:
        Xn["fe_mora_flag"] = 0 # Asumimos no mora si no hay datos

    # 6. Columna 'fe_z_Age at enrollment' que el modelo espera.
    Xn["fe_z_Age at enrollment"] = 0


    # Reemplazamos infinitos (creados por división 0/0) con 0
    # y NaNs (creados por 0/0 u operaciones con NaNs) con 0.
    Xn.replace([np.inf, -np.inf], 0, inplace=True)
    Xn.fillna(0, inplace=True)
    
    return Xn