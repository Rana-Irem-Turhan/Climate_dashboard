# pandas plus plotly
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
# Dash 
from dash import Dash, dcc, html, Input, Output, State, no_update
import numpy as np
import dash_bootstrap_components as dbc


# load and prep the data 
raw_global = pd.read_csv("merged_global.csv")
raw_global["Date"] = pd.to_datetime(raw_global[["year", "month"]].assign(day=15))
raw_hemi = pd.read_csv("hemispheric_merged.csv")
raw_hemi["Date"] = pd.to_datetime(raw_hemi[["year", "month"]].assign(day=15))
# getting the  seasons according to the month they belong
def tag_season(month):
    return {12: "DJF", 1: "DJF", 2: "DJF",
            3: "MAM", 4: "MAM", 5: "MAM",
            6: "JJA", 7: "JJA", 8: "JJA",
            9: "SON", 10: "SON", 11: "SON"}[month]

raw_global["Season"] = raw_global["month"].apply(tag_season)
# Donw a bit of aggregation for seasonal views ( useful for later)
seasonal_avg = (
    raw_global.groupby(["year", "Season"])
    .mean(numeric_only=True)
    .reset_index()
    .assign(Season_Order=lambda d: d["Season"].map({"DJF": 0, "MAM": 1, "JJA": 2, "SON": 3}))
    .sort_values(["year", "Season_Order"])
)
# intializing the dash app now 
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY], suppress_callback_exceptions=True)
app.title = "Climate Dashboard"

# deciding heading and structure of the top level layout of the dashboard
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Climate Dashboard", className="text-center my-3"), width=12)
    ]),

    dbc.Row([
        dbc.Col([
            html.Label("Mode:"),
            dcc.RadioItems(
                id='theme-toggle',options=["Light", "Dark"],value="Light",labelStyle={'display': 'inline-block', 'margin-right': '10px'})
        ], width=12, className="text-center mb-3")
    ]),
# Main tabbed content
    dbc.Row([
        dbc.Col([
            dcc.Tabs(id="tabs", value='global', children=[
                dcc.selected_tab(label='🌍 Global Trends', value='global'),
                dcc.selected_tab(label='🌍 NH vs SH Comparison', value='hemispheres')
            ]),
            html.Div(id='tabs-content')
        ], width=12)
    ]),
# for downloading the csv 
    dcc.Download(id="download-csv")
], fluid=True, style={"minWidth": "1100px", "height": "100vh", "padding": "10px"})


# to switch the tabs here it is logic
@app.callback(Output('tabs-content', 'children'), Input('tabs', 'value'))
def switch_tab(selected_tab):
    # note: global is the default tab
    if selected_tab == 'global':
        return dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("🔧 Indicator & View Settings"),
                    dbc.CardBody([
                        html.Label("Select Indicators:"),
                        dcc.Checklist(id='global-checklist', options=[
                            {'label': 'CO₂ Anomaly (Mt)', 'value': 'norm_co2'},
                            {'label': 'Land-Ocean Temp Anomaly (°C)', 'value': 'norm_land_ocean_temp'},
                            {'label': 'Land Temp Anomaly (°C)', 'value': 'norm_land_temp'},
                            {'label': 'Sea Level (mm)', 'value': 'norm_sea_level'},
                        ], value=['norm_co2', 'norm_land_ocean_temp'], labelStyle={'display': 'block'}),

                        html.Br(),
                        html.Label("Data View:"),
                        dcc.RadioItems(id='view-mode', options=["Monthly", "Seasonal"], value="Monthly"),

                        html.Br(),
                        html.Button("⬇ Download CSV", id="export-csv", className="btn btn-primary")
                    ])
                ])
            ], width=3),

            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("📊 What You’re Seeing"),
                    dbc.CardBody(id="explanation-box", style={
                        "backgroundColor":"#eef2f3",
                        "borderRadius": "6px",
                        "fontSize": "15px"
                    })
                ]),
                dcc.Graph(id='global-graph'),

                dcc.RangeSlider(
                    id='global-slider',
                    min=raw_global['year'].min(), max=raw_global['year'].max(),
                    value=[1993, raw_global['year'].max()],
                    marks={str(y): str(y) for y in range(raw_global['year'].min(), raw_global['year'].max()+1, 5)},
                    step=1
                ),

                html.Div(id="summary-panel", style={
                    "backgroundColor": "#f9f9f9", "padding": "10px", "marginTop": "10px",
                    "borderRadius": "10px", "boxShadow": "0 2px 5px rgba(0,0,0,0.1)"
                }),

                html.P(
                    "Tooltips show normalized trends; hover to see original values. "
                    "It demonstrates that the higher CO₂ often leads to increased temp & sea level rise.",
                    style={"fontSize": "12px", "color": "gray", "marginTop": "10px"}
                )
            ], width=9)
        ])
# Show hemisphere tab content 
    elif selected_tab == 'hemispheres':
        return dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("🌎 Hemisphere & Indicators"),
                    dbc.CardBody([
                        html.Label("Select Hemisphere:"),
                        dcc.Dropdown(
                            id='hemi-hemi-dropdown',
                            options=[
                                {'label': 'Northern Hemisphere', 'value': 'north'},
                                {'label': 'Southern Hemisphere', 'value': 'south'}
                            ],
                            value='north'
                        ),
                        html.Br(),
                        html.Label("Select Indicators to Animate:"),
                        dcc.Checklist(id='hemi-checklist', options=[], value=[])
                    ])
                ])
            ], width=3),

            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(" What You’re Seeing – Hemisphere Comparison"),
                    dbc.CardBody([
                        html.P("Use this section to analyze climate indicators separately for the Northern or Southern Hemisphere."),
                        html.P("🌍 First, select a hemisphere using the dropdown above. Then, choose which indicators to animate."),
                        html.P("📈 Values are normalized (0–1) for comparability across different units."),
                        html.P("▶ The animated chart shows how each indicator evolves over time, year by year."),
                        html.P("This helps reveal differences and trends between hemispheres.")
                    ])
                ]),
                dcc.Graph(id='hemi-animation')
            ], width=9)
        ])


@app.callback(
    Output("hemi-checklist", "options"),
    Output("hemi-checklist", "value"),
    Input("hemi-hemi-dropdown", "value")
)
def refresh_hemi_checklist(hemi):
    if hemi is None:
        return [], []
    prefix = f"norm_{hemi}_"
    options_map = {
        f"{prefix}co2": "CO₂ Anomaly",
        f"{prefix}land": "Land Temp Anomaly",
        f"{prefix}land_ocean": "Land-Ocean Temp Anomaly",
        f"norm_msl_{hemi}": "Sea Level Anomaly" 
    }
    options = [{"label": label, "value": key} for key, label in options_map.items()]
    default_values = [opt["value"] for opt in options]
    return options, default_values
# Updates global graph explanation box and summary panel in real time
@app.callback(
    Output('global-graph', 'figure'),
    Output('explanation-box', 'children'),
    Output('summary-panel', 'children'),
    Input('global-checklist', 'value'),
    Input('global-slider', 'value'),
    Input('view-mode', 'value'),
    Input('theme-toggle', 'value')
)
def update_global(selected, year_range, mode, theme):
    # Raw value mapping for users to see when they hover tooltips
    raw_mapping = {
        'norm_co2': 'co2_anomaly',
        'norm_land_ocean_temp': 'land_ocean_anomaly',
        'norm_land_temp': 'land_anomaly',
        'norm_sea_level': 'msl_mm'
    }

    # to get the correct time window i use filtering 
    dff = raw_global[(raw_global["year"] >= year_range[0]) & (raw_global["year"] <= year_range[1])]
    dff_season = seasonal_avg[(seasonal_avg["year"] >= year_range[0]) & (seasonal_avg["year"] <= year_range[1])]
    use_df = dff.copy() if mode == "Monthly" else dff_season.copy()

    # time axis for either the month view mode selected or the seasonal one
    use_df["X"] = use_df["Date"] if mode == "Monthly" else use_df["Season"] + " " + use_df["year"].astype(str)

    # setting up hover tooltips with raw values
    hover_data = {}
    for col in selected:
        if col in raw_mapping and raw_mapping[col] in use_df.columns:
            hover_data[raw_mapping[col]] = True

    # Final filtered DataFrame for plotting
    plot_df = use_df[["X", "year"] + selected + [raw_mapping[c] for c in selected if c in raw_mapping]].dropna()

    # Create the figure
    fig = px.line(
        plot_df,
        x="X",
        y=selected,
        labels={"X": "Year","value": "Normalized Value (0–1)", "variable": "Indicator"},
        color_discrete_sequence=['#0072B2', '#D55E00', '#009E73', '#CC79A7'],
        title=f"Climate Trends Over Time ({mode})",
        hover_data=hover_data
    )
    
    raw_global['Season_Order'] = raw_global['Season'].map({'DJF': 0, 'MAM': 1, 'JJA': 2, 'SON': 3})
    raw_global['X'] = raw_global['Season'] + ' ' + raw_global['year'].astype(str)

    

    # Annotating global climate events in both Monthly and Seasonal modes
    policy_events = {
        1997: {"label": "Kyoto Protocol", "month": 12},
        2015: {"label": "Paris Agreement", "month": 12},
        2020: {"label": "COVID Drop", "month": 4}
    }

    for year, event in policy_events.items():
        label = event["label"]
        month = event["month"]
        season = tag_season(month)
        season_label = f"{season} {year}"
        
        if mode == "Monthly":
            # Add annotation only if year is in selected range
            if year_range[0] <= year <= year_range[1]:
                date = pd.to_datetime(f"{year}-{month:02d}-01")
                fig.add_vline(x=date, line_dash="dash", line_color="gray")
                fig.add_annotation(
                    x=date,
                    y=1.05,
                    yref="paper",
                    text=label,
                    showarrow=True,
                    ax=0,
                    ay=-30,
                    font=dict(size=10)
                )
        else:  # Seasonal mode
            if season_label in plot_df["X"].values:
                fig.add_vline(x=season_label, line_dash="dash", line_color="gray")
                fig.add_annotation(
                    x=season_label,
                    y=1.05,
                    yref="paper",
                    text=label,
                    showarrow=True,
                    ax=0,
                    ay=-30,
                    font=dict(size=10)
                )
    # Explanation box to make it simpler to undertsand the data for users
    explanation = html.Div([

        html.P("🌍 This dashboard compares key climate indicators that reflect human impact on the Earth’s climate system."),
        html.Ul([
            html.Li(["🌱",html.B("CO₂ Emissions"),": Carbon dioxide ( e.g., from fossil fuels) traps heat in the atmosphere. More CO₂ → more warming."]),
            html.Li(["🌡️",html.B("Temperature Anomalies"),": How much temperatures deviate from historical normals, indicating warming trends."]),
            html.Li(["🌊",html.B("Sea Level Changes"),": Driven by ice melt and thermal expansion of seawater as it warms."])
        ]),

        html.P("You are viewing normalized values (range from 0 to 1), which means each climate indicator—CO₂ emissions (Mt), temperature anomalies (°C), and sea level (mm)—has been scaled to the same range for easy comparison."),
        html.P("➤ This allows you to directly compare trends, even though the original units are very different."),
        html.P("➤ Hover over the lines to see the actual (raw) values for each year."),
        html.P("➤ The graph highlights how these indicators have changed over time, focuses on the last 30 years."),
        html.P([
            "📍 Three key global events are marked on the chart:",
            html.Ul([
                html.Li([
                    html.B("Kyoto Protocol (Dec 1997): "),
                    "An international treaty committing industrialized countries to reduce emissions. You may notice a delayed but visible slowing in emission growth after this point."
                ]),
                html.Li([
                    html.B("Paris Agreement (Dec 2015): "),
                    "A global framework to limit warming to below 2°C. Although targets were set, the data shows only minor reductions or stabilization in trends after this agreement."
                ]),
                html.Li([
                    html.B("COVID Drop (Spring 2020): "),
                    "Global lockdowns may have led to temporary emissions drops and some irregularities in sea level due to the economic slowdown. These appear as short-term dips in the data."
                ]),
            ]),
            "These annotations help you connect major global actions or disruptions to changes in the data. Look for temporary changes or delayed responses in the trendlines near these years."
        ]),
        html.P("➤ You can use the legend side of the chart to show or hide each indicator.")
    ])
  # short correlation summary between the indciators  (normalized Pearson r)
    corr_texts = []
    norm_corr_df = plot_df[["X"] + selected].copy()
    for col in selected:
        norm_corr_df[col] = (norm_corr_df[col] - norm_corr_df[col].mean()) / norm_corr_df[col].std()

    for i in range(len(selected)):
        for j in range(i + 1, len(selected)):
            a, b = selected[i], selected[j]
            try:
                r = np.corrcoef(norm_corr_df[a], norm_corr_df[b])[0, 1]
                strength = "strong" if abs(r) > 0.7 else "moderate" if abs(r) > 0.4 else "weak"
                direction = "positive" if r > 0 else "negative"
                corr_texts.append(f"• {a} & {b}: r = {r:.2f} ({strength}, {direction} correlation)")
            except Exception:
                corr_texts.append(f"• {a} & {b}: correlation unavailable")

    return fig, explanation, html.Ul([html.Li(text) for text in corr_texts])

# to download the csv file to see the preprocessed dataset
@app.callback(
    Output("download-csv", "data"),
    Input("export-csv", "n_clicks"),
    State("global-slider", "value"),
    prevent_initial_call=True,
)
def export_csv(n_clicks, year_range):
    if not n_clicks:
        return no_update  # No button click, no download

    #filter the global data by year range
    try:
        export_df = raw_global[(raw_global['year'] >= year_range[0]) & (raw_global['year'] <= year_range[1])]
        return dcc.send_data_frame(export_df.to_csv, filename="filtered_climate_data.csv")
    except Exception as e:
        # incase failing to export the csv
        print(f"Export failed: {e}")
        return no_update

#  hemisphere animated graph callback to animaate over time 
@app.callback(
    Output('hemi-animation', 'figure'),
    Input('hemi-checklist', 'value'),
    Input('theme-toggle', 'value'),
    Input('hemi-hemi-dropdown', 'value')
)
def update_hemi_graph( selected_inds, theme , hemi):
    if not selected_inds:
        return go.Figure().update_layout(
            title="Please select at least one indicator to display.",
            template="plotly_dark" if theme == "Dark" else "plotly_white"
        )

    raw_hemi = pd.read_csv("hemispheric_merged.csv")
    #take mean of monthly data
    hemi_df_grouped = raw_hemi.groupby([ "year"]).mean(numeric_only=True).reset_index()
       # Defining variable name for legend and tooltip
    label_map = {
        "norm_north_co2": "CO₂ Anomaly (NH)",
        "norm_north_land": "Land Temp (NH)",
        "norm_north_land_ocean": "Land-Ocean Temp (NH)",
        "norm_msl_north": "Sea Level (NH)",
        "norm_south_co2": "CO₂ Anomaly (SH)",
        "norm_south_land": "Land Temp (SH)",
        "norm_south_land_ocean": "Land-Ocean Temp (SH)",
        "norm_msl_south": "Sea Level (SH)" 
    }

    color_map = {
        "norm_north_co2": "#0072B2", "norm_north_land": "#D55E00", "norm_north_land_ocean": "#009E73", "norm_msl_north": "#CC79A7",
        "norm_south_co2": "#0072B2", "norm_south_land": "#D55E00", "norm_south_land_ocean": "#009E73", "norm_msl_south": "#CC79A7"
    }

    fig = go.Figure()
    #  Add lines for firdy years data for initial display  
    initial_year = hemi_df_grouped["year"].min()
    for ind in selected_inds:
        subset = hemi_df_grouped[hemi_df_grouped["year"] <= initial_year]
        fig.add_trace(go.Scatter(
            x=subset["year"],
            y=subset[ind],
            mode="lines+markers",
            name=label_map.get(ind, ind),
            line=dict(color=color_map.get(ind, "#444")),
            hovertemplate="%{y:.2f} (normalized)<br>Year: %{x}"
        ))        
      
    #  Create animation frames progressively for each year   
    frames = []
    for year in hemi_df_grouped["year"]:
        data = []
        for ind in selected_inds:
            subset = hemi_df_grouped[hemi_df_grouped["year"] <= year]
            data.append(go.Scatter(
                x=subset["year"],
                y=subset[ind],
                mode="lines+markers",
                name=label_map.get(ind, ind),
                line=dict(color=color_map.get(ind, "#444"))         
           ))
        frames.append(go.Frame(data=data, name=str(year)))

    fig.frames = frames
# Layout of the play pause button andd slider 
    fig.update_layout(
        title=f"{hemi.upper()} Hemisphere – Normalized Indicators Over Time",
        xaxis_title="Year",
        yaxis_title="Normalized Value (0–1)",
        template="plotly_dark" if theme == "Dark" else "plotly_white",
        hovermode="x unified",
        updatemenus=[{
            "buttons": [
                {"args": [None, {"frame": {"duration": 500, "redraw": True}, "fromcurrent": True}],
                 "label": "▶ Play", "method": "animate"},
                {"args": [[None], {"frame": {"duration": 0}, "mode": "immediate"}],
                 "label": "⏸ Pause", "method": "animate"}
            ],
            "type": "buttons",
            "x": 0.8, "xanchor": "left",
            "y":1.15, "yanchor": "top",
        }],
        sliders=[{
            "steps": [
                {"args": [[str(year)], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate"}],
                 "label": str(year), "method": "animate"} for year in hemi_df_grouped["year"]
            ],
            "x": 0.05, "len": 0.9,
            "xanchor": "left", "y": -0.2, "yanchor": "bottom"
        }]
    )
    return fig
# to be deployed adding the server port accordingly docker 
server = app.server  

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=7860)
