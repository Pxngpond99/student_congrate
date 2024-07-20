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
            html.H1(children="Title of Dash App", style={"textAlign": "center"}),
            html.Div(
                html.Div(
                    children=dcc.Dropdown(
                        province.REGIONS,
                        value="southern_region",
                        id="dropdown-selection",
                        style={"width": "100%"},
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
                    # "justify-content": "space-around",
                },
            ),
            html.Div(
                children=[dcc.Graph(id="graph-map", style={"width": "100%"})],
                style={
                    "width": "100%",
                    "height": "100%",
                    # "justify-content": "space-around",
                },
            ),
        ]
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
    fig.update_traces(textposition="outside")
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
    # print(df)
    value_region = province.REGIONS[value]
    fig = go.Figure(
        data=go.Scattergeo(
            lon=long,
            lat=lat,
            text=df["schools_province"].astype(str)
            + " : "
            + df["totalstd"].astype(str)
            + " คน",
            mode="markers",
            # hoverinfo="schools_province",
            marker=dict(
                size=8,
                opacity=0.8,
                reversescale=True,
                autocolorscale=False,
                line=dict(width=1, color="rgba(102, 102, 102)"),
                colorscale="Blues",
                cmin=0,
                color=df["totalstd"],
                cmax=df["totalstd"].max(),
                colorbar_title="Incoming flights<br>February 2011",
            ),
        )
    )

    fig.update_layout(
        title="Most trafficked US airports<br>(Hover for airport names)",
        geo=dict(
            scope="asia",
            showland=True,
            landcolor="rgb(212, 212, 212)",
            countrywidth=0.5,
            subunitwidth=0.5,
            fitbounds="locations",
        ),
    )
    # fig = px.scatter_mapbox(
    #     df,
    #     lat="lat",
    #     lon="lon",
    #     hover_name="schools_province",
    #     color_discrete_sequence=["fuchsia"],
    #     zoom=5,
    #     height=300,
    # )
    # fig.update_layout(
    #     mapbox_style="white-bg",
    #     mapbox_layers=[
    #         {
    #             "below": "traces",
    #             "sourcetype": "raster",
    #             "sourceattribution": "United States Geological Survey",
    #             "source": [
    #                 "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
    #             ],
    #         },
    #         {
    #             "sourcetype": "raster",
    #             "sourceattribution": "Government of Canada",
    #             "source": [
    #                 "https://geo.weather.gc.ca/geomet/?"
    #                 "SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&BBOX={bbox-epsg-3857}&CRS=EPSG:3857"
    #                 "&WIDTH=1000&HEIGHT=1000&LAYERS=RADAR_1KM_RDBR&TILED=true&FORMAT=image/png"
    #             ],
    #         },
    #     ],
    #     # mapbox={
    #     #     "accesstoken": mapbox_token,
    #     # },
    # )
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig


if __name__ == "__main__":
    app.run(debug=True)
