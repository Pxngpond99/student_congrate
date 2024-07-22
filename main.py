from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import dash_bootstrap_components as dbc
from datas import province, api
from dash.long_callback import DiskcacheLongCallbackManager
import diskcache

app = Dash(external_stylesheets=[dbc.themes.LUMEN])

# cache = diskcache.Cache("./cache")
# long_callback_manager = DiskcacheLongCallbackManager(cache)
# mapbox_token = " "

app.layout = [
    html.Div(
        children=[
            html.H1(
                children="Dashboard จำนวนนักศึกษาที่จบมัธยมศึกษาปีที่ 6 ในปีการศึกษา 2566",
                style={
                    "textAlign": "center",
                    "color": "rgba(255,255,255,1)",
                    "font-weight": "700",
                    "padding-top": "2rem",
                },
            ),
            html.Div(
                html.Div(
                    children=dcc.Dropdown(
                        province.REGIONS,
                        value="southern_region",
                        id="dropdown-selection",
                        style={"width": "100%"},
                        clearable=False,
                    ),
                    style={
                        "justify-content": "center",
                        "display": "flex",
                        "width": "80%",
                    },
                ),
                style={"justify-content": "center", "display": "flex", "width": "100%"},
            ),
            html.Div(
                children=[dcc.Graph(id="graph-bar", style={"width": "100%"})],
                style={
                    "display": "flex",
                    "width": "100%",
                    "margin-top": "2rem",
                    # "justify-content": "space-around",
                },
            ),
            html.Div(
                children=[
                    dcc.Graph(
                        id="graph-map",
                        style={
                            "width": "100%",
                            "height": "100%",
                        },
                    ),
                    dcc.Graph(
                        id="graph-pie",
                        style={
                            "width": "100%",
                            "height": "100%",
                        },
                    ),
                ],
                style={
                    "width": "100%",
                    "height": "100%",
                    "margin-top": "2rem",
                    "display": "flex",
                    "gap": "2rem",
                    # "justify-content": "space-around",
                },
            ),
        ],
        style={
            "background": "rgb(148,243,244)",
            "background": "radial-gradient(circle, rgba(148,243,244,1) 8%, rgba(255,255,255,1) 18%, rgba(70,173,223,1) 32%, rgba(155,178,219,1) 45%, rgba(15,10,116,1) 58%, rgba(84,208,192,1) 70%, rgba(4,1,62,1) 87%)",
            "width": "100%",
        },
    )
]


@callback(Output("graph-bar", "figure"), Input("dropdown-selection", "value"))
def update_bar_graph(value):
    df = api.get_std_2566()
    region_name = province.PROVINCES[value]

    provinces = [region_name[k]["name"] for k in region_name]
    df = df[df["schools_province"].isin(provinces)]
    value_region = province.REGIONS[value]
    fig = px.bar(
        df,
        x="schools_province",
        y=["totalmale", "totalfemale"],
        title=f"กราฟแสดงข้อมูลจำนวนนักเรียนที่จบการศึกษาในภาค {value_region}",
        barmode="group",
    )
    fig.update_traces(
        textposition="outside",
    )
    fig.update_layout(
        # margin={"r": 25, "t": 35, "l": 25, "b": 25},
        paper_bgcolor="rgba(255,255,255,0.5)",
    )
    return fig


@callback(
    Output("graph-map", "figure"),
    Input("dropdown-selection", "value"),
    # prevent_initial_call=True,
)
def update_map_graph(value):
    df = api.get_std_2566()
    region_name = province.PROVINCES[value]

    provinces = [region_name[k]["name"] for k in region_name]
    lat = [region_name[k]["lat"] for k in region_name]
    long = [region_name[k]["long"] for k in region_name]
    df = df[df["schools_province"].isin(provinces)]
    df["lat"] = 0
    df["lon"] = 0
    for idx, row in df.iterrows():
        for k, v in region_name.items():
            if row["schools_province"] == region_name[k]["name"]:
                df["lat"][idx] = region_name[k]["lat"]
                df["lon"][idx] = region_name[k]["long"]
                # print(type(region_name[k]["long"]))
                # print(df["lat"][idx], df["lon"][idx])
                break
    value_region = province.REGIONS[value]

    fig = px.scatter_mapbox(
        df,
        lat="lat",
        lon="lon",
        hover_name="schools_province",
        hover_data=["totalmale", "totalfemale"],
        # color_discrete_sequence=["fuchsia"],
        zoom=5,
    )
    fig.update_layout(
        mapbox_style="open-street-map", title=f"แผนที่แสดงตำแหน่งจังหวัดในภาค {value_region}"
    )
    fig.update_layout(
        # margin={"r": 25, "t": 35, "l": 25, "b": 25},
        paper_bgcolor="rgba(255,255,255,0.5)",
    )
    return fig


@callback(Output("graph-pie", "figure"), Input("dropdown-selection", "value"))
def update_pie_graph(value):
    df = api.get_std_2566()
    region_name = province.PROVINCES[value]

    provinces = [region_name[k]["name"] for k in region_name]
    df = df[df["schools_province"].isin(provinces)]
    value_region = province.REGIONS[value]
    fig = px.pie(
        df,
        values="totalstd",
        names="schools_province",
        title=f"กราฟวงกลมแสดงสัดส่วนของนักเรียนที่จบการศึกษาในภาค {value_region}",
        hover_data=["totalmale", "totalfemale"],
    )
    fig.update_layout(
        # margin={"r": 25, "t": 35, "l": 25, "b": 25},
        paper_bgcolor="rgba(255,255,255,0.5)",
    )
    return fig


if __name__ == "__main__":
    app.run(debug=True)
