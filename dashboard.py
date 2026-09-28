"""Dashboard interactivo de retrasos de vuelos (tarea).

Ejecutar en desarrollo:
    python dashboard.py        ->  http://127.0.0.1:8050

Ejecutar en produccion (lo hace la plataforma de despliegue):
    gunicorn dashboard:server  ->  usa el objeto WSGI `server` de este modulo
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
from plotly.graph_objects import Figure
from dash import Dash, Input, Output, dcc, html

# --------------------------------------------------------------------- datos
DATA_FILE = Path(__file__).with_name("airline_data.csv")

df = pd.read_csv(
    DATA_FILE,
    encoding="ISO-8859-1",
    dtype={
        "Div1Airport": str,
        "Div1TailNum": str,
        "Div2Airport": str,
        "Div2TailNum": str,
    },
)

app = Dash(__name__)

# -------------------------------------------------------------------- layout
# TODO 1: Estructura del layout con H1, Input y los 5 Graphs obligatorios
app.layout = html.Div(children=[
    html.H1(
        "Análisis del Promedio de Retrasos de Vuelos por Causa",
        style={"textAlign": "center", "marginBottom": "20px"}
    ),
    
    html.Div([
        html.Label("Seleccione el Año: ", style={"fontSize": "18px", "marginRight": "10px"}),
        dcc.Input(
            id="input-year",
            type="number",
            value=2010,
            style={"height": "35px", "fontSize": "16px"}
        ),
    ], style={"textAlign": "center", "marginBottom": "30px"}),

    # Distribución en contenedores flexibles (RF10)
    html.Div([
        html.Div([dcc.Graph(id="carrier-plot")], style={"width": "50%"}),
        html.Div([dcc.Graph(id="weather-plot")], style={"width": "50%"}),
    ], style={"display": "flex"}),

    html.Div([
        html.Div([dcc.Graph(id="nas-plot")], style={"width": "50%"}),
        html.Div([dcc.Graph(id="security-plot")], style={"width": "50%"}),
    ], style={"display": "flex"}),

    html.Div([
        html.Div([dcc.Graph(id="late-plot")], style={"width": "100%"}),
    ], style={"display": "flex", "justifyContent": "center"})
])


# ------------------------------------------------------------------ calculos
def compute_info(datos, entered_year):
    """Devuelve 5 tablas (una por causa de retraso) para el año pedido."""
    # TODO 2: Filtrar por año y agrupar por Month y Reporting_Airline sacando el promedio
    df_year = datos[datos["Year"] == int(entered_year)]
    
    carrier_data = df_year.groupby(["Month", "Reporting_Airline"])["CarrierDelay"].mean().reset_index()
    weather_data = df_year.groupby(["Month", "Reporting_Airline"])["WeatherDelay"].mean().reset_index()
    nas_data = df_year.groupby(["Month", "Reporting_Airline"])["NASDelay"].mean().reset_index()
    sec_data = df_year.groupby(["Month", "Reporting_Airline"])["SecurityDelay"].mean().reset_index()
    late_data = df_year.groupby(["Month", "Reporting_Airline"])["LateAircraftDelay"].mean().reset_index()
    
    return carrier_data, weather_data, nas_data, sec_data, late_data


# ------------------------------------------------------------------ callback
# TODO 3: Un único callback que recibe el año y retorna las 5 figuras
@app.callback(
    [
        Output("carrier-plot", "figure"),
        Output("weather-plot", "figure"),
        Output("nas-plot", "figure"),
        Output("security-plot", "figure"),
        Output("late-plot", "figure"),
    ],
    Input("input-year", "value")
)
def get_graph(entered_year):
    # RF5: Manejo de errores/casos inválidos
    if entered_year is None or str(entered_year).strip() == "":
        fig_empty = Figure()
        fig_empty.update_layout(title="Ingrese un año válido para mostrar datos")
        return fig_empty, fig_empty, fig_empty, fig_empty, fig_empty

    try:
        entered_year = int(entered_year)
    except ValueError:
        fig_empty = Figure()
        fig_empty.update_layout(title="El valor ingresado no es numérico")
        return fig_empty, fig_empty, fig_empty, fig_empty, fig_empty

    carrier_df, weather_df, nas_df, sec_df, late_df = compute_info(df, entered_year)

    if carrier_df.empty:
        fig_empty = Figure()
        fig_empty.update_layout(title=f"Sin datos disponibles para el año {entered_year}")
        return fig_empty, fig_empty, fig_empty, fig_empty, fig_empty

    # Generación de las 5 gráficas de líneas (RF7)
    carrier_fig = px.line(
        carrier_df, x="Month", y="CarrierDelay", color="Reporting_Airline",
        title=f"Promedio de Retraso por Transportista ({entered_year})",
        labels={"Month": "Mes", "CarrierDelay": "Retraso Promedio (minutos)", "Reporting_Airline": "Aerolínea"}
    )
    weather_fig = px.line(
        weather_df, x="Month", y="WeatherDelay", color="Reporting_Airline",
        title=f"Promedio de Retraso por Clima ({entered_year})",
        labels={"Month": "Mes", "WeatherDelay": "Retraso Promedio (minutos)", "Reporting_Airline": "Aerolínea"}
    )
    nas_fig = px.line(
        nas_df, x="Month", y="NASDelay", color="Reporting_Airline",
        title=f"Promedio de Retraso por NAS ({entered_year})",
        labels={"Month": "Mes", "NASDelay": "Retraso Promedio (minutos)", "Reporting_Airline": "Aerolínea"}
    )
    sec_fig = px.line(
        sec_df, x="Month", y="SecurityDelay", color="Reporting_Airline",
        title=f"Promedio de Retraso por Seguridad ({entered_year})",
        labels={"Month": "Mes", "SecurityDelay": "Retraso Promedio (minutos)", "Reporting_Airline": "Aerolínea"}
    )
    late_fig = px.line(
        late_df, x="Month", y="LateAircraftDelay", color="Reporting_Airline",
        title=f"Promedio de Retraso por Aeronave Tardía ({entered_year})",
        labels={"Month": "Mes", "LateAircraftDelay": "Retraso Promedio (minutos)", "Reporting_Airline": "Aerolínea"}
    )

    return carrier_fig, weather_fig, nas_fig, sec_fig, late_fig


# --------------------------------------------------------------- produccion
server = app.server

if __name__ == "__main__":
    app.run(debug=True, port=8050)