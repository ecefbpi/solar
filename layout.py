from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import plotly.express as px

COLORS = px.colors.qualitative.Plotly
# ==== NAV BAR WITH LOGO AND INFO MODAL BUTTON ====

INFO_MODAL = "This tool is designed to give information about cost vs benefit of installing solar photovoltaic plant in my building.\n" \
             "The consumption data is real data for the whole 2022 measured every hour while the production data is also real data from a solar photovoltaic plant of a friend at his house. While production might vary quite a lot depending on many factors, this is the most accurate way I found to make predictions on cost vs savings for my own installation.\n" \
             "The first tab shows (blue line) the average electricity consumption per hour during the day for every month (in kwh) versus the simulated production line (red line) based on a real production system. Besides, the shadowed red area is the amount of generated electricity that would be consumed. It is also shown as a percentage on the top right corner of the graph.\n" \
             "The second tab shows a table with a per month set of figures like amount of electricity produced, consumed, the excess that would be sent back to the grid and finally the costs figures for the changed electricity, the price that the excess would have been paid and so, the difference on the electricity bill with and without the solar photovoltaic plant installed.\n" \
             "Finally on the third tab we can see a graph in which we can check how much costs savings are generated per month versus the installation costs of the solar photovoltaic plant so we can find out the break in point in which the installation costs are compensated by the savings (in number of years).\n" \
             "The graphs and the table data can be updated by the controls options, which are the peak power installed (in number of kw, from 1 to 5) and the price of installation per peak kw (in euros, from 500 to 3500).\n"


MODAL = html.Div(
    [
        dbc.Button("INFO", id="open", color='success', class_name='float-end'),
        dbc.Modal(
            [
                dbc.ModalHeader("Solar photovoltaic plant study"),
                dbc.ModalBody(INFO_MODAL),
                dbc.ModalFooter(
                    dbc.Button("Close", id="close", color='success', class_name="ml-auto")
                ),
            ],
            id="modal",
            size='lg',
            scrollable=True,
            style={'white-space': 'pre-line'}
        ),
    ]
)

ICON_HUB = html.Div(
    [
        html.A(
            [
                html.Img(src='./assets/github.png',
                         className="logo ml-1 mx-auto d-block",
                         style={'height': '60%', 'width': '60%'}
                         )
            ],
            href="https://github.com/ecefbpi",
            target="_blank"
        ),
    ]
)

ICON_IN = html.Div(
    [
        html.A(
            [
                html.Img(src='./assets/linkedin.png',
                         className="logo ml-1",
                         style={'height': '60%', 'width': '60%'}
                         )
            ],
            href="https://www.linkedin.com/in/fausto-blasco-9265381/",
            target="_blank"
        ),
    ]
)

NAVBAR = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(
                            html.A([
                                html.Img(src='./assets/dash-logo-new.png',
                                             className="logo ml-2",
                                             style={'height': '90%', 'width': '90%'})],
                                    href="https://plot.ly"),
                            width=3),
                        dbc.Col(dbc.NavbarBrand("Solar photovoltaic plant study", class_name="ml-5"),width=7),
                    ],
                    align="center",
                    class_name="g-1",
                ),
            ),
            dbc.Row(
                [
                    dbc.Col([MODAL], width={"size": 2, "offset": 8}),
                    dbc.Col([ICON_HUB], width=1),
                    dbc.Col([ICON_IN], width=1)
                ],
                align="center",
                class_name='g-0'
            )
        ],
    ),
    color="dark",
    dark=True,
    class_name="mb-2"
)

# ==== LEFT COLUMN  ====


LOAD_BUTTON = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(dbc.Button("Load Data", color='success', id="load_btn", className="me-2", n_clicks=0, disabled=False), width='auto'),
                dbc.Col(html.Span(id="load_tag", style={"verticalAlign": "middle"}), width = 'auto')
            ],
            class_name='mt-3 mb-3'
        )

    ]
)
labelsKw = [
    {
        "label": html.Span([str(i+1)], style={'color': 'black'}),
        "value": str(i+1),
    } for i in range(5)
]

KW_SELECTION = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(html.Span(children='Select Peak Kw: ', style={"verticalAlign": "middle"}), width='auto'),
                dbc.Col(dcc.Dropdown(labelsKw, placeholder = '-', id='kw', clearable=False, disabled=True), width='auto')
            ],
            class_name='mt-3 mb-3'
        )
    ]
)

KW_PRICE1 = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(html.Span(children='Installation Cost per Kw: ', style={"verticalAlign": "middle"}), width='auto'),
            ],
            class_name='mt-3 mb-1'
        )
    ]
)

KW_PRICE2 = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(dbc.Input(id='kw-cost', type="number", min=500, max=3500, step=10, value=500), width='auto'),
                dbc.Col(html.Span(children='(500€-3500€)', style={"verticalAlign": "middle"}), width='auto')
            ],
            class_name='mt-1 mb-1'
        )
    ]
)

AMORTIZATION_BUTTON = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(dbc.Button("Generate Amortization Graph", color='success', id="amort_btn", className="me-2", n_clicks=0), width='auto'),
            ],
            class_name='mt-1 mb-3'
        )

    ]
)


LEFT_COLUMN = dbc.Card(
    [
        dbc.CardHeader(
            html.Div(
                [
                    html.H4(children="Controls", className="display-8 mt-1"),
                    html.Hr(className="my-2")
                ]
            )

        ),
        dbc.CardBody(
            dbc.Row(
                [
                    LOAD_BUTTON,
                    html.Hr(className="my-2"),
                    KW_SELECTION,
                    html.Hr(className="my-2"),
                    KW_PRICE1,
                    KW_PRICE2,
                    AMORTIZATION_BUTTON
                ]
            ),
        )
    ],
    class_name="w-100 h-100",
    style={'box-shadow': '0 0 5px rgba(255, 255, 255, 0.3)'}
)

# ==== RIGHT COLUMN: PLOTS  ====

GRAPHS_TAB = dbc.Tab(
    [
        dbc.Row(
            dbc.Col(
                html.Div(
                    [
                        dbc.Spinner(
                            children=[
                                dcc.Graph(id='main-graphs',
                                          style=dict(visibility='hidden'),
                                          # responsive = True causes the main dbc.Container loosing
                                          # its height when loading the graph, so you need to manually
                                          # resize the window to get it back
                                          # config=dict(responsive=True),
                                          )
                            ],
                        )
                    ],
                    className="p-4",
                    style={'height': '100%'}
                )
            )
        ),
        dbc.Row(
            dbc.Col(
                html.Div(
                    [
                        dbc.Pagination(id="pagination",
                                       max_value=12,
                                       first_last=True,
                                       previous_next=True,
                                       class_name='justify-content-center',
                                       style=dict(visibility='hidden')
                                       )
                    ]
                )
            ),
            justify="center"
        ),
    ],
    label="Graphs",
    tab_id="tab-graph"
    )

DATA_TAB = dbc.Tab(
    [
        dbc.Row(
            dbc.Col(
                html.Div(
                    [
                        dbc.Spinner(
                            children=[
                                        html.Div(id='tableM-container'),
                                        html.Div(id='tableY-container')
                            ],
                        )
                    ],
                )
            )
        )
    ],
    label="Data Tables",
    tab_id="tab-table"
)

AMORTIZATION_TAB = dbc.Tab(
    [
        dbc.Row(
            dbc.Col(
                html.Div(
                    [
                        dbc.Spinner(
                            children=[
                                dcc.Graph(id='amort-graph',
                                          style=dict(visibility='hidden'),
                                          # responsive = True causes the main dbc.Container loosing
                                          # its height when loading the graph, so you need to manually
                                          # resize the window to get it back
                                          # config=dict(responsive=True),
                                          #className='dbc'
                                          )
                            ],
                        )
                    ],
                    className="p-4",
                    style={'height': '100%'}
                )
            )
        )
    ],
    label="Amortization Graph",
    tab_id="tab-amort"
)


RIGHT_COLUMN_ROW_2 = dbc.Card(
        [
            dbc.Tabs(
                [
                    GRAPHS_TAB,
                    DATA_TAB,
                    AMORTIZATION_TAB,
                ],
                id='graph-tabs',
                active_tab='tab-graph'
            )
        ],
        #class_name="w-100 h-100",
        style={'box-shadow': '0 0 5px rgba(255, 255, 255, 0.3)'}
    )

# ==== BODY:  ====
# ==== ROW: LEFT COLUMN + RIGHT COLUMN + DBC STORE ====

BODY = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        LEFT_COLUMN
                    ],
                    md=3
                ),
                dbc.Col(
                    [
                        RIGHT_COLUMN_ROW_2
                    ],
                    md=9,
                    width=True
                ),
            ]
        ),
        html.Div([
            dcc.Store(id='figPlots', storage_type='session'),
            dcc.Store(id='figTablesM', storage_type='session'),
            dcc.Store(id='figTablesY', storage_type='session'),
        ])
    ],
    class_name="mt-12 mb-12 ml-3 mr-3",
    fluid=True
)

# ==== LAYOUT: NAV BAR + BODY  ====

app_layout = html.Div(children=[NAVBAR, BODY])