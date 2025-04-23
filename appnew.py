
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output

# Load normalized dataset
df = pd.read_csv("combined_climate_data_normalized.csv")

# App init
app = Dash(__name__, suppress_callback_exceptions=True)
app.title = "Climate Dashboard"

# Layout
app.layout = html.Div([
    html.H1("Climate Dashboard", style={"textAlign": "center"}),

    dcc.Tabs(id="tabs", value='global', children=[
        dcc.Tab(label='🌍 Global Trends', value='global'),
        dcc.Tab(label='🧭 NH vs SH Comparison', value='hemispheres')
    ]),

    html.Div(id='tabs-content')
])

# Tab render
@app.callback(Output('tabs-content', 'children'), Input('tabs', 'value'))
def render_tab(tab):
    if tab == 'global':
        return html.Div([
            html.Div([
                html.Label("Select Indicators:"),
                dcc.Checklist(
                    id='global-checklist',
                    options=[
                        {'label': 'CO₂ Emissions (GtCO₂)', 'value': 'CO2'},
                        {'label': 'Global Temperature Anomaly (°C)', 'value': 'Global_Temp_Anomaly'},
                        {'label': 'Sea Level (m)', 'value': 'Sea_Level'},
                    ],
                    value=['CO2', 'Global_Temp_Anomaly'],
                    labelStyle={'display': 'block'}
                )
            ], style={'width': '25%', 'display': 'inline-block', 'padding': '20px'}),

            html.Div([
                dcc.Graph(id='global-graph'),
                dcc.RangeSlider(
                    id='global-slider',
                    min=df['Year'].min(),
                    max=df['Year'].max(),
                    value=[1993, df['Year'].max()],
                    marks={str(y): str(y) for y in range(df['Year'].min(), df['Year'].max()+1, 5)},
                    step=1
                ),
                html.P("Key events: Kyoto Protocol (1997), Paris Agreement (2015), COVID-19 (2020)",
                       style={"fontSize": "12px", "color": "gray", "marginTop": "10px"})
            ], style={'width': '70%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '20px'})
        ])

    elif tab == 'hemispheres':
        return html.Div([
            html.Label("NH vs SH + Emissions + Sea Level (Animated View)", style={'fontSize': 16}),
            dcc.Graph(id='hemi-animation', figure=build_hemi_animation())
        ])

# Global tab callback
@app.callback(
    Output('global-graph', 'figure'),
    Input('global-checklist', 'value'),
    Input('global-slider', 'value')
)
def update_global(selected, year_range):
    dff = df[(df['Year'] >= year_range[0]) & (df['Year'] <= year_range[1])]
    fig = px.line(
        dff, x='Year', y=selected,
        labels={"value": "Normalized Value", "variable": "Indicator"},
        color_discrete_sequence=['#0072B2', '#D55E00', '#56B4E9'],
        title="Climate Trends Over Time (Normalized)"
    )
    for year, label in {1997: "Kyoto Protocol", 2015: "Paris Agreement", 2020: "COVID Drop"}.items():
        if year_range[0] <= year <= year_range[1]:
            fig.add_vline(x=year, line_dash="dash", line_color="gray")
            fig.add_annotation(x=year, y=1, text=label, showarrow=True, ax=20, ay=-40, font=dict(size=10))

    fig.update_layout(
        template="plotly_white",
        hovermode="x unified",
        legend=dict(orientation="h", y=-0.3)
    )
    return fig

# NH vs SH animated view
def build_hemi_animation():
    indicators = ["CO2", "Sea_Level", "NH_Temp_Anomaly", "SH_Temp_Anomaly"]
    years = df['Year'].unique()

    fig = go.Figure()

    color_map = {
        "CO2": "#0072B2",               # Blue
        "Sea_Level": "#56B4E9",         # Sky Blue
        "NH_Temp_Anomaly": "#CC79A7",   # Purple
        "SH_Temp_Anomaly": "#000000"    # Black
    }

    # Add static traces (needed for legend and color persistence)
    for indicator in indicators:
        fig.add_trace(go.Scatter(x=[], y=[], mode="lines+markers", name=indicator,
                                line=dict(color=color_map[indicator])))

    # Build animation frames
    frames = []
    for year in years:
        data = []
        for indicator in indicators:
            data.append(go.Scatter(
                x=df[df['Year'] <= year]["Year"],
                y=df[df['Year'] <= year][indicator],
                mode="lines+markers",
                name=indicator,
                line=dict(color=color_map[indicator])
            ))
        frames.append(go.Frame(data=data, name=str(year)))

    fig.frames = frames

    fig.update_layout(
        title="NH vs SH + CO2 + Sea Level Over Time",
        xaxis_title="Year",
        yaxis_title="Normalized Value",
        template="plotly_white",
        hovermode="x unified",
        updatemenus=[{
            "buttons": [
                {"args": [None, {"frame": {"duration": 500, "redraw": True}, "fromcurrent": True}],
                 "label": "▶ Play", "method": "animate"},
                {"args": [[None], {"frame": {"duration": 0}, "mode": "immediate"}],
                 "label": "⏸ Pause", "method": "animate"}
            ],
            "direction": "left", "pad": {"r": 10, "t": 87},
            "showactive": False, "type": "buttons", "x": 0.1, "xanchor": "right", "y": 0, "yanchor": "top"
        }],
        sliders=[{
            "steps": [
                {"args": [[str(year)], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate"}],
                 "label": str(year), "method": "animate"}
                for year in years
            ],
            "transition": {"duration": 0},
            "x": 0.05, "len": 0.9, "xanchor": "left", "y": -0.3, "yanchor": "top"
        }]
    )

    return fig

# Run app
if __name__ == '__main__':
    app.run(debug=True)
