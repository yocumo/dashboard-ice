from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import requests
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


from helpers.helpers import (
    filtrar_df_por_fecha,
    calcular_tecnicos_activos_periodo,
    calcular_dias_laborables_mes,
    get_semanas_del_mes,
    calcular_dias_laborables,
)


# API_URL = "http://localhost:8000/api"
API_URL = "https://overtimetest-api.eiasa.com.co/api"


current_staffs = (
    "ESTEBAN CALVO ELIZONDO",
    "GERARDO MORA GRANADOS",
    "CHRISTOPHER CEDEÑO ORTEGA",
    "JONATHAN ANDREY FERNANDEZ PICADO",
    "MARCELINO SANCHEZ ZUÑIGA",
    "LEYNER BARROZO VARGAS",
    "RANDALL CAMACHO ROJAS",
    "PABLO MENDEZ MASIS",
)


# Function to get data from API
def get_updated_tasks():
    try:
        response = requests.get(f"{API_URL}/tasks/")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error al obtener datos de la API: {e}")
        return []


def crear_graficos_cumplimiento(df, fecha_inicio, fecha_fin):
    META_DIARIA_TECNICO = 250
    TOTAL_CUADRILLAS_ACTIVAS = len(calcular_tecnicos_activos_periodo(df))
    dias_laborables = calcular_dias_laborables(fecha_inicio, fecha_fin)
    META_TOTAL = TOTAL_CUADRILLAS_ACTIVAS * META_DIARIA_TECNICO * dias_laborables

    dias_laborables_mes = calcular_dias_laborables_mes(
        fecha_inicio.year, fecha_inicio.month
    )
    META_TOTAL_MES = (
        TOTAL_CUADRILLAS_ACTIVAS * META_DIARIA_TECNICO * dias_laborables_mes
    )

    if df.empty:
        fig_empty = go.Figure()
        fig_empty.update_layout(title="No hay datos disponibles para este período")
        return (
            fig_empty,
            fig_empty,
            fig_empty,
            {
                "tecnicos_activos": 0,
                "meta_total": META_TOTAL,
                "total_alcanzado": 0,
                "porcentaje_cumplimiento": 0,
                "dias_laborables": dias_laborables,
                "tecnicos_inactivos": list(current_staffs),
                "meta_total_mes": META_TOTAL_MES,
            },
        )

    df_valido = df[
        (df["status"] == "Completada")
        | ((df["status"] == "Devuelta") & (df["returned_well"] == 1))
    ]

    df_valido_agg = (
        df_valido.groupby("task_group")
        .agg(
            {
                "total": "sum",
                "staff": "last",
                "fecha": "last",
            }
        )
        .reset_index()
    )

    df_valido["fecha"] = pd.to_datetime(df_valido["fecha"])
    df_diario = (
        df_valido.groupby(df_valido["fecha"].dt.date)["total"].sum().reset_index()
    )
    df_diario["acumulado"] = df_diario["total"].cumsum()

    dias_transcurridos = len(df_diario)
    total_actual = df_diario["acumulado"].iloc[-1] if not df_diario.empty else 0

    fig_projection = go.Figure()

    x_mes = [fecha_inicio, fecha_fin]
    y_mes = [0, META_TOTAL_MES]
    fig_projection.add_trace(
        go.Scatter(
            x=x_mes,
            y=y_mes,
            name=f"Meta Mensual ({dias_laborables_mes} días)",
            line=dict(color="red", dash="dash"),
            text=["", f"${META_TOTAL_MES:,.0f}"],
            mode="lines+text",
            textposition="top right",
            textfont=dict(color="red"),
        )
    )

    fig_projection.add_trace(
        go.Scatter(
            x=x_mes,
            y=[0, META_TOTAL],
            name=f"Meta Período ({dias_laborables} días)",
            line=dict(color="gray", dash="dash"),
            text=["", f"${META_TOTAL:,.0f}"],
            mode="lines+text",
            textposition="bottom right",
            textfont=dict(color="gray"),
        )
    )

    if not df_diario.empty:
        text_labels = [""] * (len(df_diario) - 1) + [f"${total_actual:,.0f}"]
        fig_projection.add_trace(
            go.Scatter(
                x=df_diario["fecha"],
                y=df_diario["acumulado"],
                name=f"Progreso Actual ({dias_transcurridos} días)",
                line=dict(color="blue"),
                text=text_labels,
                mode="lines+text",
                textposition="middle right",
                textfont=dict(color="blue"),
            )
        )
    else:
        fig_projection.add_trace(
            go.Scatter(
                x=[fecha_inicio],
                y=[0],
                name="Progreso Actual (0 días)",
                line=dict(color="blue"),
            )
        )

    fig_projection.update_layout(
        title=f"Progreso vs. Metas ({dias_laborables_mes} días laborables en el mes)",
        xaxis_title="Fecha",
        yaxis_title="Monto ($)",
        showlegend=True,
    )

    promedio_diario_actual = (
        total_actual / dias_transcurridos if dias_transcurridos > 0 else 0
    )
    dias_restantes_mes = dias_laborables_mes - dias_transcurridos
    proyeccion_final = total_actual + (promedio_diario_actual * dias_restantes_mes)

    col11, col22 = st.columns(2)
    with col11:
        st.markdown(
            f"### 📅 Análisis de Proyección Mensual ({dias_laborables_mes} días laborables)"
        )
        st.markdown("#### Progreso:")
        st.write(f"• Monto actual: ${total_actual:,.2f}")
        st.write(
            f"• Porcentaje completado: {(total_actual/META_TOTAL_MES*100):.1f}% de la meta mensual"
        )
        st.write(f"• Meta mensual total: ${META_TOTAL_MES:,.2f}")
        st.write(f"• Días laborados: {dias_transcurridos} de {dias_laborables_mes}")
        st.write(f"• Promedio diario actual: ${promedio_diario_actual:,.2f}")

    with col22:
        st.markdown("#### 🎯 Proyección:")
        st.write(
            f"• Al ritmo actual se alcanzaría: ${proyeccion_final:,.2f} al final del mes"
        )
        st.write(
            f"• Meta diaria necesaria para objetivo mensual: ${(META_TOTAL_MES - total_actual) / dias_restantes_mes if dias_restantes_mes > 0 else 0:,.2f}"
        )

    tecnicos_activos = df_valido_agg["staff"].unique()
    tecnicos_inactivos = [
        tech for tech in current_staffs if tech not in tecnicos_activos
    ]

    if len(tecnicos_activos) == 0:
        fig_empty = go.Figure()
        fig_empty.update_layout(title="No hay datos disponibles para este período")
        return (
            fig_empty,
            fig_empty,
            fig_empty,
            {
                "tecnicos_activos": 0,
                "meta_total": META_TOTAL,
                "total_alcanzado": 0,
                "porcentaje_cumplimiento": 0,
                "dias_laborables": dias_laborables,
                "tecnicos_inactivos": tecnicos_inactivos,
                "meta_total_mes": META_TOTAL_MES,
            },
        )

    metricas_tecnicos = []
    for tecnico in tecnicos_activos:
        tareas_tecnico = df_valido[df_valido["staff"] == tecnico]
        ingresos_tecnico = tareas_tecnico["total"].sum()
        num_tareas = tareas_tecnico["task_group"].nunique()
        dias_trabajados = tareas_tecnico["fecha"].dt.date.nunique()
        meta_individual = META_DIARIA_TECNICO * dias_trabajados

        metricas_tecnicos.append(
            {
                "tecnico": tecnico,
                "ingresos": ingresos_tecnico,
                "num_tareas": num_tareas,
                "dias_trabajados": dias_trabajados,
                "meta_individual": meta_individual,
                "porcentaje_meta": (ingresos_tecnico / META_TOTAL * 100).round(1),
                "porcentaje_meta_individual": (
                    (ingresos_tecnico / meta_individual * 100).round(1)
                    if meta_individual > 0
                    else 0
                ),
            }
        )

    datos_pie = [
        f"{m['tecnico']}<br>Alcanzado: ${m['ingresos']:,.2f}<br>Tareas: {m['num_tareas']}<br>Días laborados: {m['dias_trabajados']}<br>Meta: ${m['meta_individual']:,.2f}<br>Porcentaje: {m['porcentaje_meta_individual']}%"
        for m in metricas_tecnicos
    ]
    fig_pie = go.Figure(
        data=[
            go.Pie(
                labels=datos_pie,
                values=[m["ingresos"] for m in metricas_tecnicos],
                hole=0.3,
                textposition="inside",
                textinfo="none",
                hovertemplate="<b>%{label}</b><extra></extra>",
            )
        ]
    )
    fig_pie.update_layout(
        title={
            "text": f"Contribución por Cuadrilla ({dias_laborables} días laborables)",
            "y": 0.95,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
        },
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.9, xanchor="center", x=0.5),
    )

    # total_alcanzado = df_valido["total"].sum()
    total_alcanzado = df_valido.groupby("task_group")["total"].sum().sum()
    porcentaje_cumplimiento = (total_alcanzado / META_TOTAL * 100).round(1)

    fig_barras = go.Figure()
    fig_barras.add_trace(
        go.Bar(
            x=["Meta"],
            y=[META_TOTAL],
            name="Meta del Período",
            marker_color="lightgray",
            text=[f"${META_TOTAL:,.2f}"],
            textposition="auto",
        )
    )
    fig_barras.add_trace(
        go.Bar(
            x=["Alcanzado"],
            y=[total_alcanzado],
            name=f"Alcanzado ({porcentaje_cumplimiento}%)",
            marker_color="rgb(0, 123, 255)",
            text=[f"${total_alcanzado:,.2f}"],
            textposition="auto",
        )
    )
    fig_barras.update_layout(
        title=f"Cumplimiento de Meta del Período ({dias_laborables} días laborables)",
        barmode="group",
        yaxis_title="Ingresos ($)",
        showlegend=True,
    )

    return (
        fig_pie,
        fig_barras,
        fig_projection,
        {
            "tecnicos_activos": len(tecnicos_activos),
            "meta_total": META_TOTAL,
            "total_alcanzado": total_alcanzado,
            "porcentaje_cumplimiento": porcentaje_cumplimiento,
            "dias_laborables": dias_laborables,
            "tecnicos_inactivos": tecnicos_inactivos,
            "meta_total_mes": META_TOTAL_MES,
        },
    )


# TODO:: Crea los filtros de fecha para el dashboard
def crear_filtros_fecha():

    st.write("Filtros de Fecha")

    # Obtener año y mes actual
    hoy = pd.Timestamp.now()

    # Crear lista de meses disponibles (desde enero hasta el mes actual)
    meses_disponibles = {
        i: mes
        for i, mes in enumerate(
            [
                "Enero",
                "Febrero",
                "Marzo",
                "Abril",
                "Mayo",
                "Junio",
                "Julio",
                "Agosto",
                "Septiembre",
                "Octubre",
                "Noviembre",
                "Diciembre",
            ],
            1,
        )
        if i <= hoy.month
    }

    col1, col2 = st.columns(2)

    with col1:
        mes_seleccionado = st.selectbox(
            "Seleccionar Mes:",
            options=list(meses_disponibles.keys()),
            format_func=lambda x: meses_disponibles[x],
            index=len(meses_disponibles) - 1,
        )

    # Generar lista de semanas para el mes seleccionado
    semanas = get_semanas_del_mes(hoy.year, mes_seleccionado)
    opciones_semanas = [
        f"Semana {sem[0]} ({sem[1].strftime('%d/%m')} - {sem[2].strftime('%d/%m')})"
        for sem in semanas
    ]
    opciones_semanas.insert(0, "Todas las semanas")

    with col2:
        semana_seleccionada = st.selectbox(
            "Seleccionar Semana:", options=opciones_semanas, index=0
        )

    # Crear lista de días disponibles
    # primer_dia = pd.Timestamp(year=hoy.year, month=mes_seleccionado, day=1)
    if mes_seleccionado == hoy.month:
        ultimo_dia = hoy.day
    else:
        ultimo_dia = (
            pd.Timestamp(year=hoy.year, month=mes_seleccionado + 1, day=1)
            - pd.Timedelta(days=1)
        ).day

    dias_disponibles = list(range(1, ultimo_dia + 1))
    dias_opciones = ["Todos los días"] + [f"{dia:02d}" for dia in dias_disponibles]

    col1, col2 = st.columns(2)

    with col1:
        # Deshabilitar selección de día si hay una semana seleccionada
        dia_seleccionado = st.selectbox(
            "Seleccionar Día:",
            options=dias_opciones,
            index=0,
            disabled=semana_seleccionada != "Todas las semanas",
        )

    # Crear las fechas de filtro
    year = hoy.year
    fecha_inicio = None
    fecha_fin = None

    if dia_seleccionado != "Todos los días":
        dia = int(dia_seleccionado)
        fecha_inicio = pd.Timestamp(
            year=year, month=mes_seleccionado, day=dia, hour=0, minute=0, second=0
        )
        fecha_fin = pd.Timestamp(
            year=year, month=mes_seleccionado, day=dia, hour=23, minute=59, second=59
        )
    elif semana_seleccionada != "Todas las semanas":
        # Filtro por semana
        semana_idx = opciones_semanas.index(semana_seleccionada) - 1
        fecha_inicio = semanas[semana_idx][1]
        fecha_fin = semanas[semana_idx][2]
    else:
        # Filtro por mes completo
        fecha_inicio = pd.Timestamp(year=year, month=mes_seleccionado, day=1)
        if mes_seleccionado == hoy.month:
            fecha_fin = hoy
        else:
            fecha_fin = pd.Timestamp(
                year=year, month=mes_seleccionado + 1, day=1
            ) - pd.Timedelta(days=1)

    return fecha_inicio, fecha_fin


# TODO:: Dashboard de Productividad Cuadrillas
def main():

    tasks = get_updated_tasks()
    if not tasks:
        st.warning("No se pudieron obtener datos de la API")
        return

    df = pd.DataFrame(tasks)

    df["fecha"] = pd.NaT
    df.loc[df["status"] == "Completada", "fecha"] = pd.to_datetime(
        df.loc[df["status"] == "Completada", "completed_time"]
    )
    df.loc[(df["status"] == "Devuelta") & (df["returned_well"] == 1), "fecha"] = (
        pd.to_datetime(
            df.loc[
                (df["status"] == "Devuelta") & (df["returned_well"] == 1),
                "returnedwell_time",
            ]
        )
    )
    df["returned_well"] = pd.to_numeric(df["returned_well"], errors="coerce").fillna(0)

    col5, col6, col7, col8 = st.columns(4)
    with col5:
        years = sorted(df["fecha"].dt.year.unique().tolist(), reverse=True)
        selected_year = st.selectbox("Seleccionar Año:", years)
        df = df[df["fecha"].dt.year == selected_year]

    with col6:
        sites = ["Todos"] + sorted(df["site"].unique().tolist())
        selected_site = st.selectbox("Filtrar por Sitio:", sites)

    with col7:
        events = ["Todos"] + sorted(df["event"].unique().tolist())
        selected_event = st.selectbox("Filtrar por Evento:", events)

    with col8:
        estados = ["Todos", "Completadas", "Bien Devueltas"]
        selected_estado = st.selectbox("Filtrar por Estado:", estados)

    st.write("---")
    st.subheader("Cumplimiento de Metas")

    fecha_inicio, fecha_fin = crear_filtros_fecha()
    filtered_df = df.copy()
    df_filtrado = filtrar_df_por_fecha(filtered_df, fecha_inicio, fecha_fin)

    if fecha_inicio and fecha_fin:
        st.info(
            f"Mostrando datos del período: {fecha_inicio.strftime('%d/%m/%Y')} al {fecha_fin.strftime('%d/%m/%Y')}"
        )

    # Aplicar filtros adicionales
    if selected_site != "Todos":
        df_filtrado = df_filtrado[df_filtrado["site"] == selected_site]
    if selected_event != "Todos":
        df_filtrado = df_filtrado[df_filtrado["event"] == selected_event]
    if selected_estado != "Todos":
        if selected_estado == "Completadas":
            df_filtrado = df_filtrado[df_filtrado["status"] == "Completada"]
        elif selected_estado == "Bien Devueltas":
            df_filtrado = df_filtrado[
                (df_filtrado["status"] == "Devuelta")
                & (df_filtrado["returned_well"] == 1)
            ]

    fig_pie, fig_barras, fig_projection, metricas = crear_graficos_cumplimiento(
        df_filtrado, fecha_inicio, fecha_fin
    )

    st.write("### Análisis de Proyección")
    # st.plotly_chart(fig_projection, use_container_width=True)
    st.plotly_chart(fig_projection, use_container_width=True, key="projection_chart")

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Meta del Período", f"${metricas['meta_total']:,.2f}")
    with col2:
        st.metric("Total Alcanzado", f"${metricas['total_alcanzado']:,.2f}")
    with col3:
        st.metric("% Cumplimiento", f"{metricas['porcentaje_cumplimiento']}%")
    with col4:
        st.metric("Cuadrillas Activas", metricas["tecnicos_activos"])
    with col5:
        st.metric("Días Laborables", metricas["dias_laborables"])

    if fig_pie and fig_barras:
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig_barras, use_container_width=True, key="bar_chart")
        with col2:
            st.plotly_chart(fig_pie, use_container_width=True, key="pie_chart")
            if metricas["tecnicos_inactivos"]:
                st.write("##### Cuadrillas sin actividad en el período:")
                df_inactivos = pd.DataFrame(
                    metricas["tecnicos_inactivos"], columns=["Nombre"]
                )
                st.dataframe(
                    df_inactivos,
                    hide_index=True,
                    use_container_width=True,
                    height=(len(metricas["tecnicos_inactivos"]) * 35 + 38),
                )
    else:
        st.warning("No se encontraron datos para el período seleccionado.")


main()
