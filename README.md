def main():
 # # st.title("Dashboard de Productividad Técnicos")
    # tasks = get_updated_tasks()
    # if not tasks:
    #     st.warning("No se pudieron obtener datos de la API")
    #     return

    # df = pd.DataFrame(tasks)

    # df["fecha"] = pd.NaT

    # # Asignar "completed_time" si el estado es "Completada"
    # df.loc[df["status"] == "Completada", "fecha"] = pd.to_datetime(
    #     df.loc[df["status"] == "Completada", "completed_time"]
    # )

    # # Asignar "returnedwell_time" si el estado es "Devuelta" y returned_well es 1
    # df.loc[(df["status"] == "Devuelta") & (df["returned_well"] == 1), "fecha"] = (
    #     pd.to_datetime(
    #         df.loc[
    #             (df["status"] == "Devuelta") & (df["returned_well"] == 1),
    #             "returnedwell_time",
    #         ]
    #     )
    # )

    # df["returned_well"] = pd.to_numeric(df["returned_well"], errors="coerce").fillna(0)

    # col5, col6, col7, col8 = st.columns(4)
    # with col5:
    #     years = sorted(df["fecha"].dt.year.unique().tolist(), reverse=True)
    #     selected_year = st.selectbox("Seleccionar Año:", years)

    #     df = df[df["fecha"].dt.year == selected_year]

    # with col6:
    #     sites = ["Todos"] + sorted(df["site"].unique().tolist())
    #     selected_site = st.selectbox("Filtrar por Sitio:", sites)

    # with col7:
    #     events = ["Todos"] + sorted(df["event"].unique().tolist())
    #     selected_event = st.selectbox("Filtrar por Evento:", events)

    # with col8:
    #     estados = ["Todos", "Completadas", "Bien Devueltas"]
    #     selected_estado = st.selectbox("Filtrar por Estado:", estados)

    # # TODO:: -------------------------------------------- GRÁFICO DE CUMPLIMIENTO DE METAS ------------------------------
    # st.write("---")
    # st.subheader("Cumplimiento de Metas")

    # # Agregar filtros de fecha
    # fecha_inicio, fecha_fin = crear_filtros_fecha()
    # filtered_df = df.copy()

    # # Filtrar DataFrame
    # df_filtrado = filtrar_df_por_fecha(filtered_df, fecha_inicio, fecha_fin)

    # # Mostrar período seleccionado
    # if fecha_inicio and fecha_fin:
    #     st.info(
    #         f"Mostrando datos del período: {fecha_inicio.strftime('%d/%m/%Y')} al {fecha_fin.strftime('%d/%m/%Y')}"
    #     )

    # # Crear los gráficos con datos filtrados
    # fig_pie, fig_barras, fig_projection, metricas = crear_graficos_cumplimiento(
    #     df_filtrado, fecha_inicio, fecha_fin
    # )
    # # Mostrar mensaje de proyección
    # st.write("### Análisis de Proyección")
    # # st.write(metricas["mensaje_proyeccion"])

    # # Mostrar gráfico de proyección
    # st.plotly_chart(fig_projection, use_container_width=True)

    # # Mostrar métricas
    # col1, col2, col3, col4, col5 = st.columns(5)

    # if selected_site != "Todos":
    #     filtered_df = filtered_df[filtered_df["site"] == selected_site]
    # if selected_event != "Todos":
    #     filtered_df = filtered_df[filtered_df["event"] == selected_event]
    # if selected_estado != "Todos":
    #     if selected_estado == "Completadas":
    #         filtered_df = filtered_df[filtered_df["status"] == "Completada"]
    #     elif selected_estado == "Bien Devueltas":
    #         filtered_df = filtered_df[
    #             (filtered_df["status"] == "Devuelta")
    #             & (filtered_df["returned_well"] == 1)
    #         ]

    # with col1:
    #     st.metric("Meta del Período", f"${metricas['meta_total']:,.2f}")
    # with col2:
    #     st.metric("Total Alcanzado", f"${metricas['total_alcanzado']:,.2f}")
    # with col3:
    #     st.metric("% Cumplimiento", f"{metricas['porcentaje_cumplimiento']}%")
    # with col4:
    #     st.metric("Cuadrillas Activas", metricas["tecnicos_activos"])
    # with col5:
    #     st.metric("Días Laborables", metricas["dias_laborables"])

    # # Mostrar gráficos solo si hay datos
    # if fig_pie and fig_barras:
    #     col1, col2 = st.columns(2)
    #     with col1:
    #         st.plotly_chart(fig_barras, use_container_width=True)
    #     with col2:
    #         st.plotly_chart(fig_pie, use_container_width=True)
    #         if metricas["tecnicos_inactivos"]:
    #             st.write("##### Técnicos sin actividad en el período:")
    #             df_inactivos = pd.DataFrame(
    #                 metricas["tecnicos_inactivos"], columns=["Nombre"]
    #             )
    #             # Mostrar la tabla sin índice y con estilo personalizado
    #             st.dataframe(
    #                 df_inactivos,
    #                 hide_index=True,
    #                 use_container_width=True,
    #                 height=(len(metricas["tecnicos_inactivos"]) * 35 + 38),
    #             )
    # else:
    #     st.warning("No se encontraron datos para el período seleccionado.")