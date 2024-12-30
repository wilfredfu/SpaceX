# Import required libraries
import pandas as pd
import dash
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
import plotly.express as px

# Leer el dataset de SpaceX
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Crear la aplicación Dash
app = dash.Dash(__name__)

# Lista de sitios disponibles a partir del DataFrame
sites = spacex_df['Launch Site'].unique().tolist()

# Crear el layout de la aplicación
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard', style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # TASK 1: Agregar dropdown para selección de Launch Site
    dcc.Dropdown(
        id='site-dropdown',
        options=[{'label': 'All Sites', 'value': 'ALL'}] + [{'label': site, 'value': site} for site in sites],
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    html.Br(),

    # TASK 2: Gráfico de torta mostrando total de lanzamientos exitosos
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    
    # TASK 3: Agregar slider para seleccionar el rango de Payload
    dcc.RangeSlider(
        id='payload-slider',
        min=0, 
        max=10000, 
        step=1000,
        marks={0: '0',
               2500: '2500',
               5000: '5000',
               7500: '7500',
               10000: '10000'},
        value=[min_payload, max_payload]
    ),
    html.Br(),

    # TASK 4: Gráfico de dispersión (scatter) mostrando correlación entre payload y éxito
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2: Callback para actualizar el gráfico de pastel según el sitio seleccionado
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def update_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Agrupar por sitio y contar el número total de éxitos (class=1)
        df = spacex_df[spacex_df['class'] == 1].groupby('Launch Site', as_index=False).count()
        fig = px.pie(df, values='class', names='Launch Site', title='Total Success Launches by Site')
    else:
        # Filtrar por el sitio seleccionado
        df = spacex_df[spacex_df['Launch Site'] == entered_site]
        # Contar éxitos y fracasos
        df_counts = df['class'].value_counts().reset_index()
        df_counts.columns = ['class', 'count']
        fig = px.pie(df_counts, values='count', names='class', title=f"Total Success vs Failed Launches for site {entered_site}")
    return fig

# TASK 4: Callback para actualizar el gráfico scatter según el sitio seleccionado y el rango de payload
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    # Filtrar por rango de payload
    mask = (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)
    df_filtered = spacex_df[mask]
    
    if entered_site == 'ALL':
        fig = px.scatter(
            df_filtered, x='Payload Mass (kg)', y='class', 
            color="Booster Version Category", 
            title='Correlation between Payload and Success for all Sites'
        )
    else:
        # Filtrar por el sitio seleccionado
        df_site = df_filtered[df_filtered['Launch Site'] == entered_site]
        fig = px.scatter(
            df_site, x='Payload Mass (kg)', y='class', 
            color="Booster Version Category", 
            title=f'Correlation between Payload and Success for site {entered_site}'
        )
    return fig

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run_server()
