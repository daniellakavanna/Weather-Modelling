import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
import io
import base64
import logging
from pydantic import BaseModel, Field, ValidationError
from src.calculations import calculate_overnight_temp
from src.data_preperation import load_data_from_csv
from src.models import WeatherInput
import plotly.express as px
import plotly.graph_objects as go

# Initialize the Dash app with Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Layout of the app
def create_layout():
    return dbc.Container(
        [
            # Title Row
            dbc.Row(
                [
                    dbc.Col(
                        html.H1(
                            "Overnight Minimum Temperature Calculator",
                            className="text-center mb-4",
                        ),
                        width=12,
                    )
                ]
            ),
            # File Upload Row
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Label("Upload Input File (CSV)", className="mt-2"),
                            dcc.Upload(
                                id="upload-data",
                                children=dbc.Button("Upload CSV", color="primary"),
                                multiple=False,
                            ),
                            html.Div(id="upload-status", className="mt-3"),
                        ],
                        width=12,
                    )
                ],
                className="mb-3",
            ),
            # User Input Rows for manual entry
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Label("Midday Temperature (°C)", className="mt-2"),
                            dbc.Input(
                                id="midday-temp",
                                type="number",
                                value=18,
                                placeholder="Enter midday temperature",
                            ),
                        ],
                        width=6,
                    ),
                    dbc.Col(
                        [
                            html.Label("Dew Point Temperature (°C)", className="mt-2"),
                            dbc.Input(
                                id="dew-point-temp",
                                type="number",
                                value=10,
                                placeholder="Enter dew point temperature",
                            ),
                        ],
                        width=6,
                    ),
                ],
                className="mb-3",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Label("Wind Speed (Knots)", className="mt-2"),
                            dbc.Input(
                                id="wind-speed",
                                type="number",
                                value=15,
                                placeholder="Enter wind speed",
                            ),
                        ],
                        width=6,
                    ),
                    dbc.Col(
                        [
                            html.Label("Cloud Cover (Oktas)", className="mt-2"),
                            dbc.Input(
                                id="cloud-cover",
                                type="number",
                                min=0,
                                max=8,
                                value=3,
                                placeholder="Enter cloud cover (0-8)",
                            ),
                        ],
                        width=6,
                    ),
                ],
                className="mb-3",
            ),
            # Action Buttons Row
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Button(
                            "Calculate Overnight Min Temperature (°C)",
                            id="calculate-btn",
                            color="primary",
                            className="mt-3 mb-3",
                        ),
                        width={"size": 4},
                        className="d-flex justify-content-center",
                    )
                ]
            ),
            # Output for results
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(id="result-output", className="mt-4 text-center"),
                        width=12,
                    )
                ]
            ),
            # Scatter Graph for Midday Temp vs Overnight Min Temp
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Graph(id="midday-vs-overnight", style={"display": "none"}),
                        width=12,
                    )
                ]
            ),
            # Scatter Graph for Dew Point vs Overnight Min Temp
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Graph(
                            id="dew-point-vs-overnight", style={"display": "none"}
                        ),
                        width=12,
                    )
                ]
            ),
            # Correlation Heatmap
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Graph(id="correlation-heatmap", style={"display": "none"}),
                        width=12,
                    )
                ]
            ),
            # Download Forecast Button Row
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Button(
                            "Download Forecasts",
                            id="download-btn",
                            color="success",
                            className="mt-3 mb-3",
                            disabled=True,
                        ),
                        width={"size": 4},
                        className="d-flex justify-content-center",
                    )
                ]
            ),
            dcc.Download(id="download-data"),
        ],
        fluid=True,
    )

# Helper function to decode uploaded CSV content
def parse_uploaded_file(contents):
    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)
    return pd.read_csv(io.StringIO(decoded.decode("utf-8")))

# Global variable to store the forecast results
global_forecasts = None

# Core callback function to handle both file upload and manual data entry
@app.callback(
    [
        Output("result-output", "children"),
        Output("download-btn", "disabled"),
        Output("download-data", "data"),
        Output("midday-vs-overnight", "figure"),
        Output("midday-vs-overnight", "style"),
        Output("dew-point-vs-overnight", "figure"),
        Output("dew-point-vs-overnight", "style"),
        Output("correlation-heatmap", "figure"),
        Output("correlation-heatmap", "style"),
    ],
    [
        Input("upload-data", "contents"),
        Input("calculate-btn", "n_clicks"),
        Input("download-btn", "n_clicks"),
    ],
    [
        State("upload-data", "filename"),
        State("midday-temp", "value"),
        State("dew-point-temp", "value"),
        State("wind-speed", "value"),
        State("cloud-cover", "value"),
    ],
)
def handle_forecast(
    upload_contents,
    calc_clicks,
    download_clicks,
    filename,
    midday_temp,
    dew_point_temp,
    wind_speed,
    cloud_cover,
):
    global global_forecasts
    triggered_id = dash.callback_context.triggered_id

    # Initialize default values for all graphs
    empty_graph = go.Figure()
    empty_style = {"display": "none"}

    # Handle file upload
    if triggered_id == "upload-data" and upload_contents:
        try:
            df = parse_uploaded_file(upload_contents)

            # Ensure necessary columns are present
            required_columns = [
                "Midday Temperature (°C)",
                "Midday Dew Point (°C)",
                "Wind (Kn)",
                "Cloud (oktas)",
            ]
            if not all(col in df.columns for col in required_columns):
                return (
                    "Uploaded file is missing required columns.",
                    True,
                    None,
                    empty_graph,
                    empty_style,
                    empty_graph,
                    empty_style,
                    empty_graph,
                    empty_style,
                )

            reference_df = load_data_from_csv(
                "./data/processed/transformed_reference.csv"
            )
            global_forecasts = calculate_overnight_temp(df, reference_df)

            # Generate scatter plots
            midday_vs_overnight_fig = px.scatter(
                df,
                x="Midday Temperature (°C)",
                y="Overnight Min Temperature (°C)",
                title="Midday Temperature vs Overnight Minimum Temperature",
            )

            dew_point_vs_overnight_fig = px.scatter(
                df,
                x="Midday Dew Point (°C)",
                y="Overnight Min Temperature (°C)",
                title="Dew Point Temperature vs Overnight Minimum Temperature",
            )

            # Correlation Heatmap
            corr_matrix = df[
                [
                    "Midday Temperature (°C)",
                    "Midday Dew Point (°C)",
                    "Wind (Kn)",
                    "Cloud (oktas)",
                    "Overnight Min Temperature (°C)",
                ]
            ].corr()
            corr_heatmap_fig = px.imshow(
                corr_matrix, text_auto=True, title="Correlation Heatmap"
            )
            corr_heatmap_fig.update_layout(
                width=1200,  # Larger width to avoid overlap
                height=1000,  # Larger height to avoid overlap
                title={"x": 0.5},
                xaxis_title="",
                yaxis_title="",
                xaxis=dict(
                    tickvals=list(range(len(corr_matrix.columns))),
                    ticktext=[str(col) for col in corr_matrix.columns],
                    tickangle=45,
                    tickmode="array",
                    tickfont=dict(size=12),
                    automargin=True,
                ),
                yaxis=dict(
                    tickvals=list(range(len(corr_matrix.columns))),
                    ticktext=[str(col) for col in corr_matrix.columns],
                    tickangle=0,
                    tickmode="array",
                    tickfont=dict(size=12),
                    automargin=True,
                ),
                coloraxis_colorbar=dict(title="Correlation"),
                margin=dict(l=250, r=20, t=50, b=250),  # Larger margins
            )

            return (
                dbc.Alert(
                    "File processed successfully. You can now download the forecasts.",
                    color="success",
                    className="mt-4",
                ),
                False,  # Enable download button
                dash.no_update,  # No data to update for download yet
                midday_vs_overnight_fig,  # Midday vs Overnight plot
                {"display": "block"},  # Show the midday vs overnight graph
                dew_point_vs_overnight_fig,  # Dew Point vs Overnight plot
                {"display": "block"},
                corr_heatmap_fig,  # Correlation Heatmap plot
                {"display": "block"},
            )
        except Exception as e:
            logging.error(f"Error processing file: {e}")
            return (
                dbc.Alert(
                    "Error processing file. Please try again.",
                    color="danger",
                    className="mt-4",
                ),
                True,
                None,
                empty_graph,
                empty_style,
                empty_graph,
                empty_style,
                empty_graph,
                empty_style,
            )

    # Handle manual input and calculation
    elif triggered_id == "calculate-btn" and calc_clicks:
        try:
            # Validate input using Pydantic model
            input_data = WeatherInput(
                midday_temp=midday_temp,
                dew_point_temp=dew_point_temp,
                wind_speed=wind_speed,
                cloud_cover=cloud_cover,
            )

            # Create dataframe for manual input and process calculation
            trial_data = pd.DataFrame(
                {
                    "Midday Temperature (°C)": [input_data.midday_temp],
                    "Midday Dew Point (°C)": [input_data.dew_point_temp],
                    "Wind (Kn)": [input_data.wind_speed],
                    "Cloud (oktas)": [input_data.cloud_cover],
                }
            )

            reference_df = load_data_from_csv(
                "./data/processed/transformed_reference.csv"
            )
            global_forecasts = calculate_overnight_temp(trial_data, reference_df)

            # Return results without graphs for manual input
            return (
                dbc.Alert(
                    f"Calculated Overnight Min Temperature (°C): {global_forecasts['Overnight Min Temperature (°C)'][0]} °C",
                    color="success",
                    className="mt-4",
                ),
                False,  # Enable download button
                dash.no_update,  # No data to update for download yet
                empty_graph,  # Hide the midday vs overnight graph
                empty_style,  # Hide the midday vs overnight graph
                empty_graph,  # Hide the dew point vs overnight graph
                empty_style,  # Hide the dew point vs overnight graph
                empty_graph,  # Hide the correlation heatmap
                empty_style,  # Hide the correlation heatmap
            )
        except ValidationError as e:
            return (
                dbc.Alert(
                    f"Validation error: Invalid Input", color="danger", className="mt-4"
                ),
                True,
                None,
                empty_graph,
                empty_style,
                empty_graph,
                empty_style,
                empty_graph,
                empty_style,
            )
        except Exception as e:
            logging.error(f"Error in calculation: {e}")
            return (
                dbc.Alert(
                    "An error occurred during calculation. Please try again.",
                    color="danger",
                    className="mt-4",
                ),
                True,
                None,
                empty_graph,
                empty_style,
                empty_graph,
                empty_style,
                empty_graph,
                empty_style,
            )

    # Handle file download of forecasts
    elif triggered_id == "download-btn" and download_clicks:
        if global_forecasts is not None:
            return (
                dash.no_update,
                True,
                dcc.send_data_frame(
                    global_forecasts.to_csv, filename="temperature_forecasts_report.csv"
                ),
                empty_graph,
                empty_style,
                empty_graph,
                empty_style,
                empty_graph,
                empty_style,
            )

    # Default return when no action is triggered
    return (
        "",
        True,
        None,
        empty_graph,
        empty_style,
        empty_graph,
        empty_style,
        empty_graph,
        empty_style,
    )

# Update layout
app.layout = create_layout()

if __name__ == "__main__":
    app.run_server(debug=True)
