from datetime import datetime, timedelta
import pandas as pd
import requests
import streamlit as st

from example_one import get_updated_tasks

# API_URL = "http://localhost:8000/api/tasks/byfilters/"
API_URL = "https://ice-productividad-production.up.railway.app/api/tasks/byfilters/"


# Función para obtener tareas desde la API
def get_tasks(code=None, staff=None, status=None, date_start=None, date_end=None):
    url = API_URL
    params = {}

    if code:
        params["code"] = code
    if staff:
        params["staff"] = staff
    if status:
        params["status"] = status
    if date_start:
        params["date_start"] = date_start
    if date_end:
        params["date_end"] = date_end
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error al obtener las tareas: {response.status_code}")
        return []


# Obtener lista de técnicos únicos
def get_staff_list():
    tasks = get_tasks()
    if tasks:
        return sorted(list(set(task["staff"] for task in tasks if task["staff"])))
    return []


def main():

    # st.title("Balance Histórico de Tareas")

    # Filtros en la barra lateral
    st.sidebar.header("Filtros")

    # Filtro por Código
    code_filter = st.sidebar.text_input("Filtrar por Código", "")

    # Filtro por Cuadrilla (selección)
    staff_list = get_staff_list()
    staff_filter = st.sidebar.selectbox("Filtrar por Cuadrilla", ["Todos"] + staff_list)

    # Filtro por Estado
    status_options = ["Todos", "Completada", "Devuelta", "MAL DEVUELTA"]
    status_filter = st.sidebar.selectbox("Filtrar por Estado", status_options)

    # Filtro por Rango de Fechas
    today = datetime.today()
    default_start = today - timedelta(days=30)
    date_start = st.sidebar.date_input("Fecha Inicio", default_start)
    date_end = st.sidebar.date_input("Fecha Fin", today)

    # Obtener tareas según los filtros
    tasks = get_tasks(
        code=code_filter if code_filter else None,
        staff=staff_filter if staff_filter != "Todos" else None,
        status=status_filter if status_filter != "Todos" else None,
        date_start=date_start.strftime("%Y-%m-%d") if date_start else None,
        date_end=date_end.strftime("%Y-%m-%d") if date_end else None,
    )

    if not tasks:
        st.warning("No se encontraron tareas con los filtros aplicados.")
        return

    # Convertir a DataFrame y formatear fechas
    df = pd.DataFrame(tasks)
    for col in ["datedelivery_time", "completed_time", "returnedwell_time"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col]).dt.strftime("%Y-%m-%d %H:%M:%S")

    # Calcular métricas
    total = sum(task["total"] for task in tasks if task["total"] is not None)
    total_discount = sum(
        task["discount"] for task in tasks if task["discount"] is not None
    )
    total_without_discount = sum(
        task["priceunit"] for task in tasks if task["priceunit"] is not None
    )
    times_returned = sum(
        task["returned_well"] for task in tasks if task["returned_well"] is not None
    )

    # Mostrar métricas en columnas
    st.subheader("Resumen")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total (con descuentos)", f"${total:.2f}")
    col2.metric("Total Descontado", f"${total_discount:.2f}")
    col3.metric("Total sin Descuentos", f"${total_without_discount:.2f}")
    col4.metric("N° Devoluciones", times_returned)

    # Mostrar tabla con el resto de la información
    st.subheader("Detalles de Tareas")

    # Renombrar columnas visualmente
    column_names = {
        "code": "Código",
        "task_group": "Grupo de Tarea",
        "event": "Evento",
        "priceunit": "Precio Unitario",
        "documenter": "Documentador",
        "customer": "Cliente",
        "staff": "Cuadrilla",
        "status": "Estado",
        "datedelivery_time": "Fecha de Entrega",
        "completed_time": "Fecha de Completitud",
        "returnedwell_time": "Fecha de Devolución",
        "ejecution_time": "Tiempo de Ejecución (h)",
        "site": "Sitio",
    }
    available_columns = [col for col in column_names.keys() if col in df.columns]
    df_display = df[available_columns].rename(columns=column_names)

    st.dataframe(df_display, use_container_width=True)


main()
