
# ─────────────────────────────────────
# 1. Imports
# ─────────────────────────────────────
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State, no_update
import numpy as np

# ─────────────────────────────────────
# 2. Data Loading & Preprocessing
# ─────────────────────────────────────
df = pd.read_csv("merged_global.csv")
df["Date"] = pd.to_datetime(df["year"].astype(str) + "-" + df["month"].astype(str).str.zfill(2) + "-15")
hemi_df = pd.read_csv("hemispheric_merged.csv")
hemi_df["Date"] = pd.to_datetime(hemi_df[["year", "month"]].assign(day=15))

def get_season(month):
    return {12: "DJF", 1: "DJF", 2: "DJF",
            3: "MAM", 4: "MAM", 5: "MAM",
            6: "JJA", 7: "JJA", 8: "JJA",
            9: "SON", 10: "SON", 11: "SON"}[month]

df["Season"] = df["month"].apply(get_season)
seasonal_avg = (
    df.groupby(["year", "Season"])
    .mean(numeric_only=True)
    .reset_index()
    .assign(Season_Order=lambda d: d["Season"].map({"DJF": 0, "MAM": 1, "JJA": 2, "SON": 3}))
    .sort_values(["year", "Season_Order"])
)

# ─────────────────────────────────────
# 3. App Initialization
# ─────────────────────────────────────
app = Dash(__name__, suppress_callback_exceptions=True)
app.title = "Climate Dashboard"

# ─────────────────────────────────────
# 4. Layout
# ─────────────────────────────────────
app.layout = html.Div([
    html.H1("Climate Dashboard", style={"textAlign": "center"}),

    html.Div([
        html.Label("Mode:"),
        dcc.RadioItems(id='theme-toggle', options=["Light", "Dark"], value="Light",
                       labelStyle={'display': 'inline-block', 'margin-right': '10px'})
    ], style={'textAlign': 'center', 'marginBottom': 20}),

    dcc.Tabs(id="tabs", value='global', children=[
        dcc.Tab(label='🌍 Global Trends', value='global'),
        dcc.Tab(label='🗭 NH vs SH Comparison', value='hemispheres')
    ]),
    html.Div(id='tabs-content'),
    dcc.Download(id="download-csv")
], style={
    "minWidth": "1100px",  "overflowX": "auto", "overflowY": "auto","height": "100vh", "padding": "10px"
})

# ─────────────────────────────────────
# 5. Tab Switching Callback
# ─────────────────────────────────────
@app.callback(Output('tabs-content', 'children'), Input('tabs', 'value'))
def render_tab(tab):
    if tab == 'global':
        return html.Div([
            html.Div([
                html.Label("Select Indicators:"),
                dcc.Checklist(id='global-checklist', options=[
                    {'label': 'CO₂ Anomaly (Mt)', 'value': 'norm_co2'},
                    {'label': 'Land-Ocean Temp Anomaly (°C)', 'value': 'norm_land_ocean_temp'},
                    {'label': 'Land Temp Anomaly (°C)', 'value': 'norm_land_temp'},                    
                    {'label': 'Sea Level (mm)', 'value': 'norm_sea_level'},
                ], value=['norm_co2', 'norm_land_ocean_temp'], labelStyle={'display': 'block'}),

                html.Label("View Mode:"),
                dcc.RadioItems(id='view-mode', options=["Monthly", "Seasonal"], value="Monthly"),

                html.Br(),
                html.Button("⬇ Export CSV", id="export-csv")
            ], style={'minWidth': '250px', 'flexShrink': 0, 'padding': '20px'}),
            html.Div([
                html.Div(id="explanation-box", style={"marginBottom": "10px", "padding": "10px", "backgroundColor": "#eef2f3", "borderRadius": "6px"}),
                dcc.Graph(id='global-graph'),
                dcc.RangeSlider(
                    id='global-slider',
                    min=df['year'].min(), max=df['year'].max(), value=[1993, df['year'].max()],
                    marks={str(y): str(y) for y in range(df['year'].min(), df['year'].max()+1, 5)}, step=1
                ),
                html.Div(id="summary-panel", style={
                    "backgroundColor": "#f9f9f9", "padding": "10px", "marginTop": "10px",
                    "borderRadius": "10px", "boxShadow": "0 2px 5px rgba(0,0,0,0.1)"
                }),
                html.P("Tooltips show normalized trends; hover to see original values. It demonstrates that the higher CO₂ often leads to increased temp & sea level rise",
                    style={"fontSize": "12px", "color": "gray", "marginTop": "10px"})
            ], style={'width': '70%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '20px'})
        ])

    elif tab == 'hemispheres':
        return html.Div([
            html.Div([
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
                dcc.Checklist(
                    id='hemi-checklist',
                    options=[],  # will be populated dynamically
                    value=[]
                )
            ], style={'width': '25%', 'display': 'inline-block', 'padding': '20px'}),
            html.Div([
                html.H4("🧭 What You’re Seeing – Hemisphere Comparison", style={"marginBottom": "10px"}),
                html.P("Use this section to analyze climate indicators separately for the Northern or Southern Hemisphere."),
                html.P("Select a hemisphere from the dropdown above. Then, choose indicators such as CO₂ anomaly, land or land-ocean temperature, and sea level."),
                html.P("Values are normalized (scaled between 0 and 1) for comparability, regardless of unit differences (°C, mm, Mt)."),
                html.P("Animation shows how these indicators evolved over time – helping you understand patterns like divergence between hemispheres."),
            ], style={
                "backgroundColor": "#f8f9fa",
                "border": "1px solid #ccc",
                "padding": "15px",
                "borderRadius": "8px",
                "margin": "20px 0",
                "fontSize": "14px"
            }),

            html.Div([
                dcc.Graph(id='hemi-animation')
            ], style={'width': '70%', 'display': 'inline-block', 'padding': '20px'})
    ])

@app.callback(
    Output("hemi-checklist", "options"),
    Output("hemi-checklist", "value"),
    Input("hemi-hemi-dropdown", "value")
)
def update_hemi_checklist(hemi):
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

# ─────────────────────────────────────
# 6. Global Graph and Summary
# ─────────────────────────────────────
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
    # Raw value mapping for hover tooltips
    raw_mapping = {
        'norm_co2': 'co2_anomaly',
        'norm_land_ocean_temp': 'land_ocean_anomaly',
        'norm_land_temp': 'land_anomaly',
        'norm_sea_level': 'msl_mm'
    }

    # Get correct time window
    dff = df[(df["year"] >= year_range[0]) & (df["year"] <= year_range[1])]
    dff_season = seasonal_avg[(seasonal_avg["year"] >= year_range[0]) & (seasonal_avg["year"] <= year_range[1])]
    use_df = dff.copy() if mode == "Monthly" else dff_season.copy()

    # Time axis
    use_df["X"] = use_df["Date"] if mode == "Monthly" else use_df["Season"] + " " + use_df["year"].astype(str)

    # Prepare hover tooltips with raw values
    hover_data = {}
    for col in selected:
        if col in raw_mapping and raw_mapping[col] in use_df.columns:
            hover_data[raw_mapping[col]] = True

    # Final filtered DataFrame for plotting
    plot_df = use_df[["X", "year"] + selected + [raw_mapping[c] for c in selected if c in raw_mapping]].dropna()

    # Create figure
    fig = px.line(
        plot_df,
        x="X",
        y=selected,
        labels={"value": "Normalized Value (0–1)", "variable": "Indicator"},
        color_discrete_sequence=['#0072B2', '#D55E00', '#009E73', '#CC79A7'],
        title=f"Climate Trends Over Time ({mode})",
        hover_data=hover_data
    )

    # Annotate global climate events
    policy_events = {1997: "Kyoto Protocol", 2015: "Paris Agreement", 2020: "COVID Drop"}
    if mode == "Monthly":
        for year, label in policy_events.items():
            if year_range[0] <= year <= year_range[1]:
                fig.add_vline(x=pd.to_datetime(f"{year}-01-01"), line_dash="dash", line_color="gray")
                fig.add_annotation(
                    x=pd.to_datetime(f"{year}-01-01"), y=1.05, yref="paper", text=label,
                    showarrow=True, ax=0, ay=-30, font=dict(size=10)
                )
    else:
        for year, label in policy_events.items():
            found = False
            for season in ["DJF", "MAM", "JJA", "SON"]:
                label_str = f"{season} {year}"
                if label_str in plot_df["X"].values:
                    fig.add_annotation(
                        x=label_str, y=1.05, yref="paper", text=label,
                        showarrow=True, ax=0, ay=-30, font=dict(size=10)
                    )
                    found = True
                    break
            if not found:
                continue

    # Layout styling
    fig.update_layout(
        template="plotly_dark" if theme == "Dark" else "plotly_white",
        hovermode="x unified",
        legend=dict(orientation="h", y=-0.3)
    )
    fig.update_xaxes(title_text="Date" if mode == "Monthly" else "Season-Year")

    # Explanation Box
   
    explanation = html.Div([
    html.P("You are viewing normalized values (range 0–1)."),
    html.P("➤ This helps compare indicators with different units, such as °C, mm, and Mt."),
    html.P("➤ Hover over the lines to view 'raw values' for each year.")
])


    # Correlation Text (normalized Pearson r)
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

# ─────────────────────────────────────
# 7. Export CSV
# ─────────────────────────────────────
@app.callback(
    Output("download-csv", "data"),
    Input("export-csv", "n_clicks"),
    State("global-slider", "value"),
    prevent_initial_call=True,
)
def export_csv(n_clicks, year_range):
    if n_clicks:
        filtered = df[(df['year'] >= year_range[0]) & (df['year'] <= year_range[1])]
        return dcc.send_data_frame(filtered.to_csv, "filtered_climate_data.csv")
    return no_update
# ─────────────────────────────────────
# 8. Hemisphere Animation Callback
# ─────────────────────────────────────
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

    hemi_df = pd.read_csv("hemispheric_merged.csv")
    #take mean of monthly data
    hemi_df_grouped = hemi_df.groupby([ "year"]).mean(numeric_only=True).reset_index()
       # Define variable name mapping for legend & tooltip
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
    # Step 1: Add initial visible traces from the first year
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
      
    # Step 2: Create animation frames   
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

# ─────────────────────────────────────
# 9. Run Server
# ─────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True)

