from dash import html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

from components import sidebar, extratos, dashboards
from app import *
from globals import *


# ========== Layout ========== #
content = html.Div(id='page_content')

app.layout = dbc.Container(children=[
    dcc.Store(id='store-receitas', data=df_receitas.to_dict()),
    dcc.Store(id='store-despesas', data=df_despesas.to_dict()),
    dcc.Store(id='store-cat-receitas', data=df_cat_receita.to_dict()),
    dcc.Store(id='store-cat-despesas', data=df_cat_despesa.to_dict()),
    
    dbc.Row([
        dbc.Col([
            dcc.Location(id='url'),
            sidebar.layout
        ], md=2, style={'height': '100vh'}),
        dbc.Col([
            content
        ], md=10, style={'height': '100vh'})
    ])
], fluid=True)

# ========== Callbacks ========== #
@app.callback(
    Output('page_content', 'children'),
    Input('url', 'pathname')
)
def render_page(pathname):
    if pathname in ['/', '/dashboards']:
        return dashboards.layout
    
    if pathname == '/extratos':
        return extratos.layout

# ========== Server ========== #
if __name__ == '__main__':
    app.run_server(port=8051, debug=True)
