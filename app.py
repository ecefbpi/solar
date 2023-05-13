import dash
import pandas as pd
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
from layout import app_layout
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import json
import math
import plotly.express as px
import os
from myfunctions import amort_line_graph

# Define DATADIR
pwd = os.getcwd()
files = os.listdir('.')
if pwd == '/home/ecefbpi' and 'app.py' not in files:
    DATADIR = '/home/ecefbpi/mysite/figure_data_month/'
else:
    DATADIR = os.getcwd() + '/figure_data_month/'


load_figure_template('darkly')
dbc_css = (
    "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.4/dbc.min.css"
)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY, dbc_css])

server = app.server
app.layout = app_layout
MONTH_STR = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
             7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November',
             12: 'December'}
COLORS = px.colors.qualitative.Dark24

# ================================== #
# ================================== #
#            CALLBACKS               #
# ================================== #
# ================================== #

# ==== CALLBACKS FOR MODAL WINDOW ====
@app.callback(
    Output("modal", "is_open"),
    [Input("open", "n_clicks"),
     Input("close", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):

    if n1 or n2:
        return not is_open
    return is_open


# ==== CALLBACK FOR TRIGGERING INITIAL DATA LOADING ====
@app.callback([Output('figPlots', 'data'),
               Output('figTablesM', 'data'),
               Output('figTablesY', 'data'),
               Output('load_btn', 'disabled'),
               Output('pagination', 'active_page'),
               Output('pagination', 'style'),
               Output('kw', 'disabled'),
               Output('kw', 'value')],
               Input('load_btn', 'n_clicks'))
def on_load_btn_click(n):
    if n == 1:
        fig_dict = dict()
        tablesM = dict()
        tablesY = dict()

        for j in range(5):
            fig_dict[j+1] = list()
            for i in range(12):
                with open(DATADIR + '/figProdReal{}kw_{}.json'.format(j+1, MONTH_STR[i+1])) as fplot:
                    fig_dict[j+1].append(json.load(fplot))

        for i in range(5):
            tablesM[i+1] = pd.read_json(DATADIR + '/dfTableM{}kw.json'.format(i+1)).to_dict()
            tablesY[i+1] = pd.read_json(DATADIR + '/dfTableY{}kw.json'.format(i + 1)).to_dict()

        return [fig_dict, tablesM, tablesY, True, 1, dict(), False, '1']
    else:
        raise dash.exceptions.PreventUpdate

# ==== CALLBACKS FOR GENERATING MAIN GRAPHS ====
@app.callback(Output('main-graphs', 'figure'),
              Output('load_tag', 'children'),
              Input('pagination', 'active_page'),
              Input('kw', 'value'),
              State('figPlots', 'data'),
              prevent_initial_call=True)
def generate_main_graph(page, kw, data):
    return go.Figure(data[str(kw)][page-1]), 'Data loaded!'


@app.callback(Output('main-graphs', 'style'),
              Input('main-graphs', 'figure'),
              prevent_initial_call=True)
def show_main_graph(figure):
    if figure is not None:
        if len(figure) != 0:
            return dict()

    return dict(visibility='hidden')

# ==== CALLBACKS FOR GENERATING DATA TABLES ====
@app.callback(Output('tableM-container', 'children'),
              Output('tableY-container', 'children'),
              Input('kw', 'value'),
              State('figTablesM', 'data'),
              State('figTablesY', 'data'),
              prevent_initial_call=True)
def generate_tables(kw, tableM, tableY):
    dfM = pd.DataFrame(tableM[kw])
    dfY = pd.DataFrame(tableY[kw])
    dfM['newCol']= dfM['Month'].apply(lambda x: [k for k, v in MONTH_STR.items() if v == x][0])
    dfM.sort_values(by=['newCol'], inplace=True)
    dfM.drop(columns=['newCol'], inplace=True)

    return dbc.Table.from_dataframe(dfM, striped=True, bordered=True, hover=True, color='success'), \
           dbc.Table.from_dataframe(dfY, striped=True, bordered=True, hover=True, color='success')

# ==== CALLBACKS FOR GENERATING AMORTIZATION GRAPHS ====
@app.callback(Output('amort-graph', 'figure'),
              Input('amort_btn', 'n_clicks'),
              State('kw-cost', 'value'),
              State('kw', 'value'),
              State('figTablesY', 'data'),
              prevent_initial_call=True)
def generate_amort_graph(n, kw_cost, kw, tableY):
    if n != 0:
        fig = amort_line_graph(kw_cost, kw, tableY)
    else:
        raise dash.exceptions.PreventUpdate

    return fig


@app.callback(Output('amort-graph', 'style'),
              Input('amort-graph', 'figure'),
              prevent_initial_call=True)
def show_amort_graph(figure):
    if figure is not None:
        if len(figure) != 0:
            return dict()

    return dict(visibility='hidden')

if __name__ == "__main__":
    app.run_server(debug=False, host="127.0.0.1")