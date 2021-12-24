import os
import pandas as pd
import dash
import numpy as np
from dash import dcc, html, dash_table, callback_context
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from tensorflow.keras import models

from graphs import dg_graph, temp_graph, dg_graph_mini, temp_graph_mini

from sdk import SedmaxHeader
#assets_path = ''

# Create a dash application
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY]) #, assets_folder=assets_path

normal_path = './data/normal/'
imbalanced_path = './data/imbalanced/'
normal_cases = os.listdir(normal_path)
imbalanced_cases = os.listdir(imbalanced_path)

model = models.load_model('model/')

def load_data(path):
    data = pd.read_csv(path, header = None)
    data = np.array(data[4]).reshape(-1, 1000)
    return data


# Create an app layout
body = dbc.Container([
        dbc.Row([ dcc.Graph(id='normal_engine', animate=True)
        ]),
        dbc.Row([ dcc.Graph(id='fault_engine', animate=True)
        ]),
html.Div([
    html.Button('Исправный', id='btn1', n_clicks=0),
    html.Button('Несправный', id='btn2', n_clicks=0),
])
    ], fluid=True, style = {'background-color': '#5f8dab'})


app.layout = html.Div(children=[
    SedmaxHeader(title='Анализ вибрации синхронного двигателя'),
    body,
])


@app.callback(Output(component_id='memory-output', component_property='data'),
              [Input(component_id='interval-component', component_property='n_intervals'),
               Input(component_id='slider_1', component_property='value'),
               Input(component_id='slider_2', component_property='value')]

              )
def update_global_var(n, days, minutes):
   return load_data_new(days, minutes)

@app.callback(
    [Output(component_id='normal_engine', component_property='figure')],
    [Input(component_id='btn1', component_property='n_clicks')]
 )
def normal_chart(n):

    path = normal_path + np.random.choice(os.listdir(normal_path))
    data = load_data(path)
    pred = model.predict(data)

    #вставать график

    return fig1

@app.callback(
    [Output(component_id='fault_engine', component_property='figure')],
    [Input(component_id='btn2', component_property='n_clicks')]
 )
def fault_chart(n):
    el_archive = pd.read_json(data[0])
    rtd_archive = pd.read_json(data[1])
    rtd = pd.read_json(data[2])

    fig1 = dg_graph([el_archive, rtd_archive], n)
    fig2 = temp_graph(rtd_archive, n)
    fig3 = dg_graph_mini(rtd)
    fig4 = temp_graph_mini(rtd)

    return fig1

@app.callback(
    Output("offcanvas", "is_open"),
    Input("open-offcanvas", "n_clicks"),
    [State("offcanvas", "is_open")],
)
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open