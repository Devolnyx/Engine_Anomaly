import os
import pandas as pd
import dash
import numpy as np
from dash import dcc, html, dash_table, callback_context
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from tensorflow.keras import models

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from sdk import SedmaxHeader


# Create a dash application
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MATERIA]) #, assets_folder=assets_path

normal_path = './data/normal/'
imbalanced_path = './data/imbalanced/'
misalignment_path = './data/misalignment/'
ball_path = './data/ball_fault/'
cage_path = './data/cage_fault/'
outer_path = './data/outer_fault/'



#model = models.load_model('model_underhang/') #1
model = models.load_model('model_sound/') #7
#model = models.load_model('model/') #4

def load_data(path):
    data = pd.read_csv(path, header = None)
    data = np.array(data[7]).reshape(-1, 1000)
    return data

def plot_data(true, pred, label):

    errors = abs(pd.DataFrame(true) - pd.DataFrame(pred)).mean(axis=1)
    error_counts = errors.round(3).value_counts()
    error_counts = ((error_counts // 5) * 5).to_dict()
    true = np.array(true).flatten()
    pred = np.array(pred).flatten()

    statistics = {'STD': errors.std(),
                  'Skewness': errors.skew(),
                  'IQR': errors.quantile(.75) - errors.quantile(.25),
                  'Mean': errors.mean(),
                  'Median': errors.median(),
                  '90th Perc.': errors.quantile(.9),
                  }

    fig = make_subplots(rows=2, cols=2, shared_xaxes=True, vertical_spacing=0.07, row_width=[0.2, 0.3],
                        specs=[[{"colspan": 2}, None], [{}, {}]], )
    fig.add_trace(go.Scatter(y=true, mode='lines', line=dict(color='steelblue', width=2), name='Показания'),
                  row=1, col=1)
    fig.add_trace(go.Scatter(y=pred, mode='lines', line=dict(color='salmon', width=2), name='Выходные данные'),
                  row=1, col=1)

    #fig.add_trace(go.Histogram(x=errors, name='Распределение ошибок'),row=2, col=1),
    fig.add_trace(
        go.Bar(x=list(error_counts), y=list(error_counts.values()), name='Стат. показатели ошибок', orientation='v'),
        row=2, col=1)

    fig.add_trace(
        go.Bar(y=list(statistics), x=list(statistics.values()), name='Стат. показатели ошибок', orientation='h'),
        row=2, col=2)

    fig.update_layout(height=900,
                      yaxis=dict(range=[-1, 1]),
                      yaxis2=dict(range=[0, 40]),
                      xaxis2=dict(range=[0,.25]),
                      xaxis3=dict(range=[0,.5]),

                      paper_bgcolor="rgba(100,149,237,0.05)",
                      title_text=label,
                      title={'font': {'size': 20}},
                      title_y=0.98,
                      title_x=0.5,
                      hovermode="x unified",
                      #plot_bgcolor="rgba(100,149,237,0.5)",
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                      margin=dict(l=20, r=20, b=30, t=100, pad=1),
                      )


    return fig


# Create an app layout
body = dbc.Container([
        html.Br(),
        dbc.Row([
            dbc.Col([dcc.Graph(id='normal_engine', animate=True, animation_options=dict(traces = [0])),
            html.Button('Исправный', className="btn btn-lg btn-secondary", id='btn1', n_clicks=0,
                        style={'margin': '14px', 'background-color': "rgba(100,149,237,0.1))", 'box-shadow': '0 0 5px rgba(0,0,0,0.5)'}),
            ]),
            dbc.Col([dcc.Graph(id='fault_engine', animate=True, animation_options=dict(traces = [0,1])),
            html.Button('Неисправный', className="btn btn-lg btn-secondary", id='btn2', n_clicks=0,
                        style={'margin': '14px', 'background-color': "rgba(100,149,237,0.1))", 'box-shadow': '0 0 5px rgba(0,0,0,0.5)'}),
            ]),
        ], style = {'display':'flex', 'flex-flow': 'row nowrap'}),

        html.Br(),
        dcc.Link(html.Button('Подробнее о данных', className="btn btn-sm btn-secondary", id="collapse-button",
                 style={'margin': '14px', 'background-color': "rgba(100,149,237,0.1))", 'box-shadow': '0 0 5px rgba(0,0,0,0.5)'}),
                 href='http://www02.smt.ufrj.br/~offshore/mfs/page_01.html'),

        dbc.Collapse(
            dbc.Card(dbc.CardBody([html.Div(html.Img(src='assets/image.png', style={'height': '100%', 'width': '100%'})),
                                html.Div(html.Img(src='assets/bearing.png',
                                style={'height': '30%', 'width': '30%',
                                        'margin-left': 'auto', 'margin-right': 'auto', 'display':'block'}))]
                                  )),
            id="collapse",
            is_open=False,
        ),

    ], fluid=True, style = {'background-color': '#fff' }) #'#5f8dab'


app.layout = html.Div(children=[
    dcc.Store(id='memory_normal'),
    dcc.Store(id='memory_fault'),
    html.Div(
    SedmaxHeader(title='Анализ вибрации синхронного двигателя', color='#323232'),
    style={'box-shadow': '0 0 10px rgba(0,0,0,0.5)', 'display': 'grid'}),
    body,

])


@app.callback(Output(component_id='memory_normal', component_property='data'),
              Input(component_id='btn1', component_property='n_clicks'))

def normal_data(n):
    path = normal_path + np.random.choice(os.listdir(normal_path))
    data = load_data(path)
    pred = model.predict(data)
    label = 'Normal'
    return [data, pred, label]

@app.callback(Output(component_id='memory_fault', component_property='data'),
              Input(component_id='btn2', component_property='n_clicks'))


def fault_data(n):
    path = np.random.choice([imbalanced_path, misalignment_path, ball_path, cage_path, outer_path])
    if path == imbalanced_path:
        label = 'Imbalanced'
    elif path == misalignment_path:
        label = 'Misalignment'
    elif path == ball_path:
        label = 'Ball Fault'
    elif path == cage_path:
        label = 'Cage Fault'
    elif path == outer_path:
        label = 'Outer Fault'

    path = path + np.random.choice(os.listdir(path))
    data = load_data(path)
    pred = model.predict(data)
    return [data, pred, label]


@app.callback([Output(component_id='normal_engine', component_property='figure'),
               Output(component_id='fault_engine', component_property='figure')],
              [Input(component_id='memory_normal', component_property='data'),
               Input(component_id='memory_fault', component_property='data')]
              )

def update_chart(normal_data, fault_data):


    fig1 = plot_data(normal_data[0], normal_data[1], normal_data[2])
    fig2 = plot_data(fault_data[0], fault_data[1], fault_data[2])

    return [fig1, fig2]


@app.callback(
    Output("collapse", "is_open"),
    [Input("collapse-button", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


if __name__ == "__main__":
    app.run_server(debug=True)