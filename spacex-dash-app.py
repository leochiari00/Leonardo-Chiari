# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Build dropdown options
site_options = [{'label': 'All Sites', 'value': 'ALL'}] + [
    {'label': site, 'value': site} for site in sorted(spacex_df['Launch Site'].unique())
]

# Create an app layout
app.layout = html.Div(children=[
    html.H1(
        'SpaceX Launch Records Dashboard',
        style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}
    ),

    # TASK 1: Launch Site dropdown
    dcc.Dropdown(
        id='site-dropdown',
        options=site_options,
        value='ALL',
        placeholder="Select a Launch Site",
        clearable=False,
        style={'width': '60%', 'margin': '0 auto'}
    ),
    html.Br(),

    # TASK 2: Pie chart
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):", style={'textAlign': 'center'}),

    # TASK 3: Range slider
    dcc.RangeSlider(
        id='payload-slider',
        min=min_payload,
        max=max_payload,
        step=1000,
        value=[min_payload, max_payload],
        tooltip={"placement": "bottom", "always_visible": False},
        marks={
            int(min_payload): str(int(min_payload)),
            int((min_payload + max_payload) / 2): str(int((min_payload + max_payload) / 2)),
            int(max_payload): str(int(max_payload))
        },
    ),
    html.Br(),

    # TASK 4: Scatter chart
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Helper: pick a color column if present
COLOR_COL = 'Booster Version Category' if 'Booster Version Category' in spacex_df.columns else None

# TASK 2: callback for pie chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def update_pie(selected_site):
    if selected_site == 'ALL':
        # Total successful launches by site
        success_by_site = spacex_df.groupby('Launch Site')['class'].sum().reset_index()
        fig = px.pie(
            success_by_site,
            values='class',
            names='Launch Site',
            title='Total Successful Launches by Site'
        )
    else:
        # Success vs Failure for the selected site
        df_site = spacex_df[spacex_df['Launch Site'] == selected_site]
        outcome_counts = df_site['class'].value_counts().rename({1: 'Success', 0: 'Failure'}).reset_index()
        outcome_counts.columns = ['Outcome', 'Count']
        fig = px.pie(
            outcome_counts,
            values='Count',
            names='Outcome',
            title=f'Success vs Failure for {selected_site}'
        )
    return fig

# TASK 4: callback for scatter chart
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [
        Input(component_id='site-dropdown', component_property='value'),
        Input(component_id='payload-slider', component_property='value')
    ]
)
def update_scatter(selected_site, payload_range):
    low, high = payload_range
    mask = (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)
    df = spacex_df[mask]
    if selected_site != 'ALL':
        df = df[df['Launch Site'] == selected_site]

    scatter_kwargs = dict(
        data_frame=df,
        x='Payload Mass (kg)',
        y='class',
        title='Payload vs. Outcome (1=Success, 0=Failure)'
              + ('' if selected_site == 'ALL' else f' — {selected_site}')
    )
    if COLOR_COL:
        scatter_kwargs['color'] = COLOR_COL

    fig = px.scatter(**scatter_kwargs)
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)

