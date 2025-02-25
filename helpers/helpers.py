from datetime import timedelta

import pandas as pd
import pytz

import streamlit as st

# TODO:: Establecer un rando de fechas
def get_week_range(date):
    start_of_week = date - timedelta(days=date.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    return start_of_week.strftime("%d %B"), end_of_week.strftime("%d %B")


"""
    Filtra el DataFrame por rango de fechas, considerando el día completo.
    Args:
        df: DataFrame con los datos
        fecha_inicio: Timestamp con la fecha inicial
        fecha_fin: Timestamp con la fecha final
    """


# def filtrar_df_por_fecha(df, fecha_inicio, fecha_fin):

#     if fecha_inicio is None or fecha_fin is None:
#         return df

#     # Asegurarse de que las fechas del DataFrame tengan zona horaria
#     if df["fecha"].dt.tz is None:
#         df["fecha"] = df["fecha"].dt.tz_localize(pytz.UTC)

#     # Agregar zona horaria a las fechas de filtro si no la tienen
#     if fecha_inicio.tz is None:
#         fecha_inicio = fecha_inicio.tz_localize(pytz.UTC)
#     if fecha_fin.tz is None:
#         fecha_fin = fecha_fin.tz_localize(pytz.UTC)

#     # Si fecha_inicio y fecha_fin son el mismo día, ajustar fecha_fin al final del día
#     if fecha_inicio.date() == fecha_fin.date():
#         fecha_fin = fecha_fin.replace(hour=23, minute=59, second=59, microsecond=999999)

#     # Filtrar el DataFrame
#     df_filtrado = df[
#         (df["fecha"] >= fecha_inicio)
#         & (
#             df["fecha"] <= fecha_fin
#         )  # Cambiado a <= para incluir el último segundo del día
#     ]


#     return df_filtrado
# def filtrar_df_por_fecha(df, fecha_inicio, fecha_fin):
#     if fecha_inicio is None or fecha_fin is None:
#         return df

#     # Filtrar filas donde "fecha" no es NaT antes de operar con .dt
#     df = df[df["fecha"].notna()].copy()

#     # Asegurarse de que las fechas del DataFrame tengan zona horaria
#     if df["fecha"].dt.tz is None:
#         df["fecha"] = df["fecha"].dt.tz_localize(pytz.UTC)

#     # Agregar zona horaria a las fechas de filtro si no la tienen
#     if fecha_inicio.tz is None:
#         fecha_inicio = fecha_inicio.tz_localize(pytz.UTC)
#     if fecha_fin.tz is None:
#         fecha_fin = fecha_fin.tz_localize(pytz.UTC)

#     # Si fecha_inicio y fecha_fin son el mismo día, ajustar fecha_fin al final del día
#     if fecha_inicio.date() == fecha_fin.date():
#         fecha_fin = fecha_fin.replace(hour=23, minute=59, second=59, microsecond=999999)

#     # Filtrar el DataFrame
#     df_filtrado = df[(df["fecha"] >= fecha_inicio) & (df["fecha"] <= fecha_fin)]

#     return df_filtrado


# def filtrar_df_por_fecha(df, fecha_inicio, fecha_fin):
#     """
#     Filtra el DataFrame por fecha, contando correctamente los eventos
#     de devolución y completado como eventos separados con sus propios valores.
#     """
#     if fecha_inicio is None or fecha_fin is None:
#         return df

#     # Crear un DataFrame para eventos de completado
#     df_completadas = df[df["status"] == "Completada"].copy()
#     df_completadas["fecha_evento"] = pd.to_datetime(df_completadas["completed_time"])
#     df_completadas["tipo_evento"] = "Completada"

#     # Crear DataFrame para eventos de devolución correcta
#     df_devueltas = df[(df["status"] == "Devuelta") & (df["returned_well"] == 1)].copy()
#     df_devueltas["fecha_evento"] = pd.to_datetime(df_devueltas["returnedwell_time"])
#     df_devueltas["tipo_evento"] = "Devuelta Bien"

#     # Combinar ambos tipos de eventos
#     df_eventos = pd.concat([df_completadas, df_devueltas])

#     # Filtrar por el rango de fechas
#     df_filtrado = df_eventos[
#         (df_eventos["fecha_evento"] >= fecha_inicio)
#         & (df_eventos["fecha_evento"] <= fecha_fin)
#     ]
#     print("Event", df_completadas)

#     return df_filtrado


def filtrar_df_por_fecha(df, fecha_inicio, fecha_fin):
    """
    Filtra el DataFrame por fecha, contando correctamente los eventos
    de devolución y completado como eventos separados con sus propios valores.
    """
    if fecha_inicio is None or fecha_fin is None:
        return df

    # Crear un DataFrame para eventos de completado
    df_completadas = df[df["status"] == "Completada"].copy()
    df_completadas["fecha_evento"] = pd.to_datetime(
        df_completadas["completed_time"], utc=True, errors="coerce"
    )
    df_completadas["tipo_evento"] = "Completada"

    # Crear DataFrame para eventos de devolución correcta
    df_devueltas = df[(df["status"] == "Devuelta") & (df["returned_well"] == 1)].copy()
    df_devueltas["fecha_evento"] = pd.to_datetime(
        df_devueltas["returnedwell_time"], utc=True, errors="coerce"
    )
    df_devueltas["tipo_evento"] = "Devuelta Bien"

    # Combinar ambos tipos de eventos
    df_eventos = pd.concat([df_completadas, df_devueltas])

    # Filtrar filas con fechas válidas
    df_eventos = df_eventos[df_eventos["fecha_evento"].notna()].copy()

    # Asegurarse de que las fechas tengan zona horaria UTC
    if df_eventos["fecha_evento"].dt.tz is None:
        df_eventos["fecha_evento"] = df_eventos["fecha_evento"].dt.tz_localize(pytz.UTC)

    # Asegurarse de que fecha_inicio y fecha_fin estén en UTC
    if fecha_inicio.tz is None:
        fecha_inicio = fecha_inicio.tz_localize(pytz.UTC)
    if fecha_fin.tz is None:
        fecha_fin = fecha_fin.tz_localize(pytz.UTC)

    # Filtrar por el rango de fechas
    df_filtrado = df_eventos[
        (df_eventos["fecha_evento"] >= fecha_inicio)
        & (df_eventos["fecha_evento"] <= fecha_fin)
    ]

    # Depuración
    # st.write("Datos filtrados en filtrar_df_por_fecha:")
    # st.write(df_filtrado[["task_group", "fecha_evento", "total", "tipo_evento"]])

    return df_filtrado


# TODO:: Calcula los técnicos activos basado en tareas completadas o bien devueltas durante el período filtrado.
def calcular_tecnicos_activos_periodo(df):
    # Convertir a datetime si no lo es
    if not pd.api.types.is_datetime64_any_dtype(df["fecha"]):
        df["fecha"] = pd.to_datetime(df["fecha"])

    # Asegurarse de que las fechas en el DataFrame tengan zona horaria
    if df["fecha"].dt.tz is None:
        df["fecha"] = df["fecha"].dt.tz_localize(pytz.UTC)

    # Filtrar técnicos que han tenido actividad en el período
    tecnicos_activos = df[
        (df["status"] == "Completada")
        | ((df["status"] == "Devuelta") & (df["returned_well"] == 1))
    ]["staff"].unique()

    return tecnicos_activos


# TODO:: Calcula los días laborables (lunes a sábado) para un mes específico
def calcular_dias_laborables_mes(year, month):

    primer_dia = pd.Timestamp(year=year, month=month, day=1)
    if month == 12:
        siguiente_mes = pd.Timestamp(year=year + 1, month=1, day=1)
    else:
        siguiente_mes = pd.Timestamp(year=year, month=month + 1, day=1)
    ultimo_dia = siguiente_mes - pd.Timedelta(days=1)

    dias_laborables = 0
    fecha_actual = primer_dia

    while fecha_actual <= ultimo_dia:
        if fecha_actual.dayofweek < 6:  # 0-5 son lunes a sábado
            dias_laborables += 1
        fecha_actual += pd.Timedelta(days=1)

    return dias_laborables


def get_semanas_del_mes(year, month):
    primer_dia = pd.Timestamp(year=year, month=month, day=1)
    if month == pd.Timestamp.now().month:
        ultimo_dia = pd.Timestamp.now()
    else:
        ultimo_dia = pd.Timestamp(year=year, month=month + 1, day=1) - pd.Timedelta(
            days=1
        )

    semanas = []
    fecha_actual = primer_dia
    num_semana = 1

    while fecha_actual <= ultimo_dia:
        inicio_semana = fecha_actual
        if fecha_actual.dayofweek > 0:
            dias_al_lunes = fecha_actual.dayofweek
            inicio_semana = fecha_actual - pd.Timedelta(days=dias_al_lunes)

        fin_semana = inicio_semana + pd.Timedelta(days=5)
        if fin_semana > ultimo_dia:
            fin_semana = ultimo_dia

        if inicio_semana.month != month:
            inicio_semana = primer_dia

        semanas.append((num_semana, inicio_semana, fin_semana))
        fecha_actual = inicio_semana + pd.Timedelta(days=7)
        num_semana += 1

    return semanas


# """
# Calcula el número de días laborables (lunes a sábado) entre dos fechas
# """
def calcular_dias_laborables(fecha_inicio, fecha_fin):

    dias_laborables = 0
    fecha_actual = fecha_inicio

    while fecha_actual <= fecha_fin:
        if fecha_actual.dayofweek < 6:  # 0-5 son lunes a sábado
            dias_laborables += 1
        fecha_actual += pd.Timedelta(days=1)

    return dias_laborables
