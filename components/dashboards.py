from dash import html, dcc
from datetime import datetime, date, timedelta
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from app import *
from globals import *

card_icon = {
    'color': 'white',
    'textAlign': 'center',
    'fontSize': 30,
    'margin': 'auto'
}

graph_margin = dict(l=25, r=25, t=25, b=0)

layout = dbc.Col([
    dbc.Row([
        # Saldo Total
        dbc.Col([
            dbc.CardGroup([
                dbc.Card([
                    html.Legend('Saldo'),
                    html.H5('R$ 5000', id='p-saldo-dashboard', style={})
                ], style={'padding-left': '20px', 'padding-top': '10px'}),
                dbc.Card(
                    html.Div(className='fa fa-university', style=card_icon),
                    color='warning',
                    style={'maxWidth': 75, 'height': 100, 'margin-left': '-10px'})
            ])
        ], width=4),
        
        # Receita
        dbc.Col([
            dbc.CardGroup([
                dbc.Card([
                    html.Legend('Receita'),
                    html.H5('R$ 4600', id='p-receita-dashboard', style={})
                ], style={'padding-left': '20px', 'padding-top': '10px'}),
                dbc.Card(
                    html.Div(className='fa fa-smile-o', style=card_icon),
                    color='success',
                    style={'maxWidth': 75, 'height': 100, 'margin-left': '-10px'})
            ])
        ], width=4),
        
        # Despesa
        dbc.Col([
            dbc.CardGroup([
                dbc.Card([
                    html.Legend('Despesa'),
                    html.H5('R$ 2800', id='p-despesa-dashboard', style={})
                ], style={'padding-left': '20px', 'padding-top': '10px'}),
                dbc.Card(
                    html.Div(className='fa fa-meh-o', style=card_icon),
                    color='danger',
                    style={'maxWidth': 75, 'height': 100, 'margin-left': '-10px'})
            ])
        ], width=4),
    ], style={'margin': '10px'}),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                html.Legend('Filtrar lançamentos', className='card-title'),
                html.Label('Categoria de receitas'),
                html.Div(
                    dcc.Dropdown(
                        id='dropdown-receita',
                        clearable=False,
                        style={'width': '100%'},
                        persistence=True,
                        persistence_type='session',
                        multi=True
                    )
                ),
                
                html.Label('Categorias das Despesas'),
                html.Div(
                    dcc.Dropdown(
                        id='dropdown-despesa',
                        clearable=False,
                        style={'width': '100%'},
                        persistence=True,
                        persistence_type='session',
                        multi=True
                    )
                ),
                
                html.Legend('Período de Análise', style={'margin-top': '10px'}),
                dcc.DatePickerRange(
                    month_format='Do MM YY',
                    end_date_placeholder_text='Data...',
                    start_date=datetime.today() - timedelta(days=30),
                    end_date=datetime.today() + timedelta(days=30),
                    updatemode='singledate',
                    id='date-picker-config',
                    style={'z-index': '100'},
                )
            ], style={'height': '100%', 'padding': '20px'})
        ], width=4),
        
        dbc.Col(
            dbc.Card(dcc.Graph(id='graph1'), style={'heigth': '100%', 'padding': '10px'}), width=8
        )
    ], style={'margin': '10px'}),
    
    dbc.Row([
        dbc.Col(dbc.Card(dcc.Graph(id='graph2'), style={'padding': '10px'}), width=6),
        dbc.Col(dbc.Card(dcc.Graph(id='graph3'), style={'padding': '10px'}), width=3),
        dbc.Col(dbc.Card(dcc.Graph(id='graph4'), style={'padding': '10px'}), width=3)
    ])
])

# =================== Callbacks =================== #

# Dropdown receita
@app.callback(
    [
        Output('dropdown-receita', 'options'),
        Output('dropdown-receita', 'value'),
        Output('p-receita-dashboard', 'children')
    ],
    
    Input('store-receitas', 'data')
)
def populate_dropdown_values_receita(data):
    df = pd.DataFrame(data)
    valor = df['Valor'].sum()
    val = df.Categoria.unique().tolist()
    
    return ([{'label': x, 'value': x} for x in val], val, f'R$ {valor:,.2f}')

# Dropdown despesa
@app.callback(
    [
        Output('dropdown-despesa', 'options'),
        Output('dropdown-despesa', 'value'),
        Output('p-despesa-dashboard', 'children')
    ],
    
    Input('store-despesas', 'data')
)
def populate_dropdown_values_despesa(data):
    df = pd.DataFrame(data)
    valor = df['Valor'].sum()
    val = df.Categoria.unique().tolist()
    
    return ([{'label': x, 'value': x} for x in val], val, f'R$ {valor:,.2f}')

# Card topo Total
@app.callback(
    Output('p-saldo-dashboard', 'children'),
    [
        Input('store-despesas', 'data'),
        Input('store-receitas', 'data')
    ]
)
def saldo_total(despesas, receitas):
    df_despesas = pd.DataFrame(despesas)
    df_receitas = pd.DataFrame(receitas)
    
    valor = df_receitas['Valor'].sum() - df_despesas['Valor'].sum()
    
    return f'RS {valor:,.2f}'

# Grafico 1
@app.callback(
    Output('graph1', 'figure'),
    [
        Input('store-despesas', 'data'),
        Input('store-receitas', 'data'),
        Input('dropdown-despesa', 'value'),
        Input('dropdown-receita','value')
    ]
)
def update_graph1(data_despesa, data_receita, despesa, receita):
    
    df_despesas = pd.DataFrame(data_despesa).set_index('Data')[['Valor']]
    df_ds = df_despesas.groupby('Data').sum().rename(columns={'Valor': 'Despesa'})

    df_receitas = pd.DataFrame(data_receita).set_index('Data')[['Valor']]
    df_rc = df_receitas.groupby('Data').sum().rename(columns={'Valor': 'Receita'})

    df_acum = df_ds.join(df_rc, how='outer').fillna(0)
    df_acum['Acum'] = df_acum['Receita'] - df_acum['Despesa']
    df_acum['Acum'] = df_acum['Acum'].cumsum()

    fig = go.Figure()

    fig.add_trace(go.Scatter(name='Fluxo de caixa', x=df_acum.index, y=df_acum['Acum'], mode='lines'))
    fig.update_layout(margin=graph_margin, height=362)
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

    return fig

# Grafico 2
@app.callback(
    Output('graph2', 'figure'),
    [
        Input('store-receitas', 'data'),
        Input('store-despesas', 'data'),
        Input('dropdown-receita', 'value'),
        Input('dropdown-despesa', 'value'),
        Input('date-picker-config', 'start-date'),
        Input('date-picker-config', 'end-date')
    ]
)
def update_graph2(data_despesa, data_receita, despesa, receita, start_date, end_date):
    df_ds = pd.DataFrame(data_despesa)
    df_rc = pd.DataFrame(data_receita)
    dfs = [df_ds, df_rc]
    
    df_ds['Output'] = 'Despesas'
    df_rc['Output'] = 'Receitas'
    df_final = pd.concat(dfs)
    
    mask = (df_final['Data'] >= start_date) & (df_final['Data'] <= end_date) 
    df_final = df_final.loc[mask]

    df_final = df_final[df_final['Categoria'].isin(receita) | df_final['Categoria'].isin(despesa)]

    fig = px.bar(df_final, x="Data", y="Valor", color='Output', barmode="group")        
    fig.update_layout(margin=graph_margin, height=300)
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    
    return fig

#Graph 3
@app.callback(
    Output('graph3', 'figure'),
    [
        Input('store-receitas', 'data'),
        Input('dropdown-receita', 'value')
    ]
)
def pie_receita(data_receita, receita):
    df = pd.DataFrame(data_receita)
    df = df[df['Categoria'].isin(receita)]
    
    fig = px.pie(df, values=df.Valor, names=df.Categoria, hole=.2)
    fig.update_layout(title={'text': 'Receitas'})
    fig.update_layout(margin=graph_margin, height=300)
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    
    return fig

# Graph 4
@app.callback(
    Output('graph4', 'figure'),
    [
        Input('store-despesas', 'data'),
        Input('dropdown-despesa', 'value')
    ]
)
def pie_despesa(data_despesa, despesa):
    df = pd.DataFrame(data_despesa)
    df = df[df['Categoria'].isin(despesa)]
    
    fig = px.pie(df, values=df.Valor, names=df.Categoria, hole=.2)
    fig.update_layout(title={'text': 'Despesas'})
    fig.update_layout(margin=graph_margin, height=300)
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    
    return fig
