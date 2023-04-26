import pandas as pd
import plotly.graph_objects as go
import math
import plotly.express as px
from dash_bootstrap_templates import load_figure_template

COLORS = px.colors.qualitative.Dark24
load_figure_template('darkly')

def amort_line_graph(kw_cost, kw, tableY):
    dfY = pd.DataFrame(tableY[kw])
    billed = dfY.iloc[0]['Billed']
    sim_billed = dfY.iloc[0]['Simulated Bill']
    diff = billed - sim_billed
    if diff > 0:
        savings = billed - sim_billed
    else:
        savings = billed - diff
    inst_price = int(kw) * kw_cost

    # for line graph
    #amort_years = math.ceil(inst_price / savings) + 2
    amort_years = 15
    x = [i + 1 for i in range(amort_years)]
    y_amort = [savings * i for i in range(amort_years)]
    y_inst = [inst_price] * amort_years

    # for bar graph
    projection_years = 15
    years = [i + 1 for i in range(projection_years)]
    earnings = [savings * i for i in range(projection_years)]
    installation = [inst_price] * projection_years

    net = [i - j for i, j in zip(earnings, installation)]
    colors = [COLORS[0] if value > 0 else 'red' for value in net]
    width = [0.3] * projection_years

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x,
        y=y_amort,
        line=dict(width=2, color=COLORS[0]),
        showlegend=True,
        name="Savings"
    )
    )
    fig.add_trace(go.Scatter(
        x=x,
        y=y_inst,
        line=dict(width=2, color='red'),
        showlegend=True,
        name='Inst. Cost'
    )
    )
    fig.add_trace(go.Bar(
        x=years,
        y=net,
        marker_color=colors,
        showlegend=True,
        name='Net worth',
        width=width
    )
    )
    fig.update_xaxes(title_text="Years")
    fig.update_yaxes(title_text="Euros")

    text_title = "Amortization Curve for " + kw + " kw Installation<br><b>- 15 Years Projection -</b>"
    fig['layout'].update(
        title={
            'text': text_title,
            'font_size': 18,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
        xaxis=dict(tickmode='linear'),
    )

    return fig
