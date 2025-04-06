import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# load data
df = pd.read_csv('Sleep_health_and_lifestyle_dataset.csv')

df['BMI Category'] = df['BMI Category'].replace({
    'Normal': 'Normal Weight',
    'Normal Weight': 'Normal Weight',
    'Overweight': 'Overweight',
    'Obese': 'Overweight'
})

# data cleaning
df[['Systolic', 'Diastolic']] = df['Blood Pressure'].str.split('/', expand=True)
df['Systolic'] = pd.to_numeric(df['Systolic'], errors='coerce')
df['Diastolic'] = pd.to_numeric(df['Diastolic'], errors='coerce')

bins = [25, 30, 35, 40, 45, 50, 55, 60]
labels = ['25-29', '30-34', '35-39', '40-44', '45-49', '50-54', '55-59']
df['Age Group'] = pd.cut(df['Age'], bins=bins, labels=labels, right=False, ordered=True)
df['Age Group'] = pd.Categorical(df['Age Group'], categories=labels, ordered=True)

# check if 'None' is in dataset
if 'None' not in df['Sleep Disorder'].unique():
    df['Sleep Disorder'] = df['Sleep Disorder'].fillna('None')

# color palette
custom_blues = ['#a6cee3', '#6baed6', '#4292c6', '#2171b5', '#08519c', '#08306b', '#041c3a']


############################### strip plot ###############################
fig_large = px.strip(
    df, x="Physical Activity Level", y="Quality of Sleep",
    color="Age Group",
    category_orders={"Age Group": labels},
    color_discrete_map={labels[i]: custom_blues[i] for i in range(len(labels))},
    labels={"Physical Activity Level": "Physical Activity Level (Minutes/Day)",
            "Quality of Sleep": "Quality of Sleep (Scale 1-10)"},
    template="simple_white"
)
fig_large.update_traces(marker={'size': 20}, jitter=0.9)
fig_large.update_layout(
    plot_bgcolor='white', paper_bgcolor='white',
    xaxis=dict(showline=True, linewidth=2, linecolor='black', mirror=True),
    yaxis=dict(showline=True, linewidth=2, linecolor='black', mirror=True),
    margin=dict(l=50, r=50, t=50, b=50),
    legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1)
)

############################### barchart ###############################
fig_small1 = px.bar(
    df.groupby("Stress Level", as_index=False)["Quality of Sleep"].mean(),
    x="Stress Level", y="Quality of Sleep",
    title="Stresslevel vs. average   Quality of Sleep",
    color_discrete_sequence=["#6baed6"]
)
fig_small1.update_layout(
    plot_bgcolor='white', paper_bgcolor='white',
    xaxis=dict(showline=True, linewidth=2, linecolor='black', mirror=True),
    yaxis=dict(showline=True, linewidth=2, linecolor='black', mirror=True),
    margin=dict(l=50, r=50, t=50, b=50)
)

############################### boxplot ###############################
fig_small2 = px.box(
    df, x="Age Group", y="Quality of Sleep",
    title="Quality of Sleep in different Age Groups",
    color_discrete_sequence=["#a6cee3"]
)
fig_small2.update_layout(
    plot_bgcolor='white', paper_bgcolor='white',
    xaxis=dict(showline=True, linewidth=2, linecolor='black', mirror=True),
    yaxis=dict(showline=True, linewidth=2, linecolor='black', mirror=True),
    margin=dict(l=50, r=50, t=50, b=50)
)

############################### heatmap ###############################
sleep_disorders_order = ['None', 'Insomnia', 'Sleep Apnea']
pivot_table = df.pivot_table(index='BMI Category', columns='Sleep Disorder', aggfunc='size', fill_value=0)

# labels for bmi-category
y_labels = pivot_table.index.tolist()
y_labels = ['Over-<br>weight' if label == 'Overweight' else label for label in y_labels]
y_labels = ['Normal<br>Weight' if label == 'Normal Weight' else label for label in y_labels]

# values for heatmap
z_values = pivot_table[sleep_disorders_order].values
text_values = [[str(value) for value in row] for row in z_values]

fig_small3 = go.Figure(data=go.Heatmap(
    z=z_values,
    x=sleep_disorders_order,
    y=pivot_table.index,
    colorscale='Blues',
    colorbar=dict(title='Frequency'),
    text=text_values,
    texttemplate="%{text}",
    textfont=dict(size=20),
    hovertemplate="Sleep Disorder: %{x}<br>BMI-Category: %{y}<br>Frequency: %{z}<extra></extra>"
))

# line between cells
fig_small3.update_traces(
    xgap=2,
    ygap=2,
    hoverongaps=False,
    hoverinfo="text"
)

fig_small3.update_layout(
    title=dict(text="Frequencies between BMI-Category and Sleep Disorder", font=dict(size=18)),
    xaxis_title="Sleep Disorder",
    yaxis_title="BMI-Category",
    plot_bgcolor='white',
    paper_bgcolor='white',
    xaxis=dict(showline=True, linewidth=2, linecolor='black', mirror=True),
    yaxis=dict(showline=True, linewidth=2, linecolor='black', mirror=True, tickvals=pivot_table.index, ticktext=y_labels),
    margin=dict(l=50, r=50, t=50, b=50)
)

############################### create dash-app ###############################
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.Div([
        html.H1("Sleep, Health and Lifestyle",
                style={'font-size': '44px', 'color': '#1f77b4', 'font-family': 'Arial, sans-serif'}),

        # Info text below the title
        html.P("The dataset was synthetically generated and includes information on sleep patterns as well as factors that may influence "
                "them, such as physical activity, stress levels, and health metrics. With 374 observations and 13 variables, it provides a solid "
                "foundation for analyzing sleep quality and duration, along with the factors that may impact them.",
               style={'font-size': '18px', 'color': 'black', 'margin-bottom': '5px',
                      'font-family': 'Arial, sans-serif', 'width': '63%'}),

        # dropdown
        dcc.Dropdown(
            id='metric-dropdown',
            options=[
                {'label': 'Sleep Quality', 'value': 'Quality of Sleep'},
                {'label': 'Sleep Duration', 'value': 'Sleep Duration'}
            ],
            value='Sleep Duration',  # standard value
            clearable=False,
            style={'width': '40%', 'font-family': 'Arial, sans-serif', 'margin-top': '30px'}
        ),

        # strip plot
        dcc.Graph(id='strip-plot', figure=fig_large,
                  style={"width": "100%", "height": "820px", "margin-top": "25px"}),
    ], style={"width": "70%"}),

    # plots on the right
    html.Div([
        dcc.Graph(id='bar-plot', figure=fig_small1, style={"height": "350px"}),
        dcc.Graph(id='box-plot', figure=fig_small2, style={"height": "350px"}),
        dcc.Graph(id='heatmap-plot', figure=fig_small3, style={"height": "350px"})
    ], style={"display": "flex", "flexDirection": "column", "width": "30%", "margin-top": "30px"}),
], style={"display": "flex"})


############################### callback-funktion to update plots ###############################
@app.callback(
    [Output('strip-plot', 'figure'),
     Output('bar-plot', 'figure'),
     Output('box-plot', 'figure')],
    [Input('metric-dropdown', 'value')]
)
def update_plots(selected_metric):

    # for customized labeling
    y_axis_labels = {"Quality of Sleep": "Sleep Quality (Scale 1-10)",
                     "Sleep Duration": "Sleep Duration (Hours)"}
    selected_metric_name = {"Quality of Sleep": "Sleep Quality",
                     "Sleep Duration": "Sleep Duration"}

    # strip plot
    fig_large_updated = px.strip(
        df, x="Physical Activity Level", y=selected_metric,
        color="Age Group",
        custom_data=["Age Group"],
        category_orders={"Age Group": labels},
        color_discrete_map={labels[i]: custom_blues[i] for i in range(len(labels))},
        labels={"Physical Activity Level": "Physical Activity Level (Minutes/Day)",
                selected_metric: y_axis_labels.get(selected_metric, selected_metric)},
        template="simple_white"
    )
    fig_large_updated.update_traces(
        marker={'size': 20},
        jitter=0.9,
        hovertemplate = "Age Group: %{customdata[0]}<br>Physical Activity Level: %{x}<br>" + selected_metric_name.get(selected_metric, selected_metric) + ": %{y}<extra></extra>"
    )
    fig_large_updated.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        title=dict(text=f"Influence of Physical Activity on {selected_metric_name.get(selected_metric, selected_metric)} per Age Group",
                   font=dict(size=22), x=0.02, xanchor='left'),
        xaxis=dict(showline=True, linewidth=2, linecolor='black', mirror=True),
        yaxis=dict(dtick=1,showline=True, linewidth=2, linecolor='black', mirror=True),
        margin=dict(l=50, r=50, t=80, b=50),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    # barchart
    fig_small1_updated = px.bar(
        df.groupby("Stress Level", as_index=False)[selected_metric].mean(),
        x="Stress Level", y=selected_metric,
        labels={"Stress Level":"Stress Level (Scale 1-10)",
                selected_metric: f"Average {y_axis_labels.get(selected_metric, selected_metric)}"},
        color_discrete_sequence=["#a6cee3"]
    )
    fig_small1_updated.update_traces(
        hovertemplate="Stress Level: %{x}<br>" + selected_metric_name.get(selected_metric, selected_metric) + ": %{y:.1f}<extra></extra>"
    )
    fig_small1_updated.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        title=dict(text=f"Average {selected_metric_name.get(selected_metric, selected_metric)} per Stress Level", font=dict(size=18)),
        xaxis=dict(showline=True, linewidth=2, linecolor='black', mirror=True),
        yaxis=dict(showline=True, linewidth=2, linecolor='black', mirror=True),
        margin=dict(l=50, r=50, t=50, b=50)
    )

    # boxplot
    fig_small2_updated = px.box(
        df, x="Age Group", y=selected_metric,
        labels={"Age Group": "Age Group",
                selected_metric: y_axis_labels.get(selected_metric, selected_metric)},
        color_discrete_sequence=["#1f78b4"]
    )
    fig_small2_updated.update_traces(
        hovertemplate=(
            "Age Group: %{x}<br>Value: %{y:.2f}<br><extra></extra>"
        )
    )
    fig_small2_updated.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        title=dict(text=f"Difference in {selected_metric_name.get(selected_metric, selected_metric)} across different Age Groups", font=dict(size=18)),
        xaxis=dict(showline=True, linewidth=2, linecolor='black', mirror=True),
        yaxis=dict(dtick=1,showline=True, linewidth=2, linecolor='black', mirror=True),
        margin=dict(l=50, r=50, t=50, b=50)
    )

    return fig_large_updated, fig_small1_updated, fig_small2_updated


############################### start app ###############################
if __name__ == "__main__":
    app.run(debug=True)
    # app.run(host='0.0.0.0', port=8050)