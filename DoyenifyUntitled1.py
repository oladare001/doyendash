#!/usr/bin/env python
# coding: utf-8

# In[1]:


#!pip install firebase-admin
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import matplotlib.pyplot as plt
import dash
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import panel as pn


# In[2]:


#!pip install --upgrade keyring
#!pip install --upgrade pip setuptools


# In[3]:



cred= credentials.Certificate("servicekeys.json")
#firebase_admin.initialize_app(cred, {"databaseURL": "https://doyenifypanelapi.firebaseio.com"})
# Initialize the app with a service account
firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()


# In[4]:


# Reference to the 'CourseRegistration' collection
course_registration_ref = db.collection('CourseRegistration')

# Fetch all documents in the collection
docs = course_registration_ref.stream()

# Convert documents to list of dictionaries
data = [doc.to_dict() for doc in docs]

# Print data to verify
#print(data)


# In[5]:


# Convert to DataFrame
df = pd.DataFrame(data)

# Print DataFrame to verify
#print(df)


# In[6]:


df['createdAt'] = pd.to_datetime(df['createdAt'])


# Extract date and time into separate columns
df['Date'] = df['createdAt'].dt.date
df['Time'] = df['createdAt'].dt.time


# In[7]:


#list(df.columns)


# In[8]:


def convert_price_to_euro(df, currency_symbol):
    # Check if the necessary columns exist in the DataFrame
    if 'paidPrice' not in df.columns or 'paymentCurrency' not in df.columns:
        raise ValueError("DataFrame must contain 'paidPrice' and 'paymentCurrency' columns.")

    # Create the 'TotalpaidinEURO' column based on the conditions
    df['TotalpaidinEURO'] = df.apply(
        lambda row: row['paidPrice'] if row['paymentCurrency'] == currency_symbol else 0,
        axis=1
    )
    
    # Create the 'TotalpaidinNAIRA' column based on the conditions
    df['TotalpaidinNAIRA'] = df.apply(
        lambda row: row['paidPrice'] if row['paymentCurrency'] != currency_symbol else 0,
        axis=1
    )

    return df



# Convert prices
df = convert_price_to_euro(df, currency_symbol='€')

# Print the updated DataFrame


# In[9]:


df.shape


# In[10]:


#df.query("cohort== 0")
count_per_course_status = df.groupby(['course', 'status']).size().reset_index(name='count')
#count_per_course_status


# In[11]:


TotalAmount_In_Categoryofcourses= df.groupby("course")["TotalpaidinEURO"].sum()


# In[12]:


Count_SourceofDis= df['sourceOfDiscovery'].value_counts()


# In[13]:


# Group by 'course' and 'sourceOfDiscovery', then count the occurrences
#count_source_of_discovery = df.groupby(['course', 'sourceOfDiscovery']).size().unstack(fill_value=0)

# Plot a stacked bar chart
#count_source_of_discovery.plot(kind='bar', stacked=True, figsize=(12, 10))

# Add labels and title
#plt.title('Source of Discovery by Course')
#plt.xlabel('Course')
#plt.ylabel('Count')
#plt.legend(title='Source of Discovery')
#plt.xticks(rotation=75)
#plt.tight_layout()

# Show the plot
#plt.show()


# In[14]:


# Aggregate the data by userIp and count occurrences
#ip_counts = df['userIp'].value_counts().reset_index(name='count')
#ip_counts.columns = ['userIp', 'count']

# Plot a single pie chart
#plt.figure(figsize=(10, 8))
#plt.pie(ip_counts['count'], labels=ip_counts['userIp'], autopct='%1.1f%%', startangle=90)
#plt.title('Distribution of User IPs Across All Courses')
#plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
#plt.show()


# In[15]:


# Initialize the Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    # Title
    html.H1("DOYEN DASH", style={'textAlign': 'center', 'padding': '10px 0'}),

    # Sidebar with dropdown for cohort selection
    html.Div([
        html.H2("Select Cohort"),
        dcc.Dropdown(
            id='cohort-dropdown',
            options=[{'label': f'Cohort {cohort}', 'value': cohort} for cohort in df['cohort'].unique()],
            value=df['cohort'].unique()[0],
            clearable=False
        )
    ], style={
        'width': '15%',  # Sidebar width
        'padding': '10px',
        'box-shadow': '2px 0px 5px rgba(0, 0, 0, 0.1)',  # Add some shadow for visual separation
        'background-color': '#f8f9fa'  # Light gray background for sidebar
    }),

    # Main content area
    html.Div([
        # Graph for filtered data
        html.Div([
            dcc.Graph(id='stacked-bar-chart', style={'height': '600px'})
        ], style={'width': '80%', 'display': 'inline-block', 'padding': '10px', 'vertical-align': 'top'}),

        # Table for filtered data
        html.Div([
            html.H4("Total Paid in EURO & NAIRA by Course and Cohort"),
            dash_table.DataTable(
                id='course-total-table',
                columns=[
                    {'name': 'Course', 'id': 'course'},
                    {'name': 'Total Paid in EURO', 'id': 'TotalpaidinEURO'},
                    {'name': 'Total Paid in NAIRA', 'id': 'TotalpaidinNAIRA'}
                ],
                style_table={'width': '20%'},
                style_cell={'textAlign': 'left'},
                style_header={'fontWeight': 'bold'},
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(248, 248, 248)'
                    }
                ]
            )
        ], style={'width': '20%', 'display': 'inline-block', 'padding': '10px', 'vertical-align': 'top'})
    ], style={'display': 'flex'}),

    # Table for course application count by cohort
    html.Div([
        html.H3("Count of Course Applications by Cohort"),
        dash_table.DataTable(
            id='per-cohort-course',
            columns=[
                {'name': 'Course', 'id': 'course'},
                {'name': 'Cohort', 'id': 'cohort'},
                {'name': 'Count', 'id': 'count'}
            ],
            style_table={'width': '100%'},
            style_cell={'textAlign': 'left'},
            style_header={'fontWeight': 'bold'},
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }
            ]
        )
    ], style={'padding': '10px', 'width': '60%'}),

    html.Div([
        html.H3("General Cohort distribution", style={'textAlign': 'center'}),  # Center align the heading
        dcc.Graph(id='pie-table-chart', style={'height': '500px'}),
    ], style={
        'width': '100%', 
        'display': 'flex', 
        'flexDirection': 'column',
        'alignItems': 'center',  # Center align content within the div
        'padding': '10px'
    })
])

@app.callback(
    Output('stacked-bar-chart', 'figure'),
    Output('course-total-table', 'data'),
    Output('per-cohort-course', 'data'),
    Input('cohort-dropdown', 'value')
)
def update_filtered_views(selected_cohort):
    # Filter the DataFrame based on the selected cohort
    filtered_df = df[df['cohort'] == selected_cohort]

    # Group by 'course' and 'sourceOfDiscovery', then count the occurrences
    count_source_of_discovery = filtered_df.groupby(['course', 'sourceOfDiscovery']).size().reset_index(name='count')

    # Create a stacked bar chart
    fig = px.bar(
        count_source_of_discovery,
        x='course',
        y='count',
        color='sourceOfDiscovery',
        title=f'Source of Discovery for Cohort {selected_cohort}',
        labels={'count': 'Count', 'course': 'Course'},
        barmode='stack'
    )

    # Group by 'course' and calculate the total amount paid in euros and naira for each course
    total_amount_in_courses = filtered_df.groupby('course')[['TotalpaidinEURO', 'TotalpaidinNAIRA']].sum().reset_index()

    # Group by 'course' and cohort
    no_of_courses = filtered_df.groupby(['cohort', 'course']).size().reset_index(name='count')

    return fig, total_amount_in_courses.to_dict('records'), no_of_courses.to_dict('records')

@app.callback(
    Output('pie-table-chart', 'figure'),
    Input('cohort-dropdown', 'value')  # We can keep this here for consistency, even though not needed
)
def update_unfiltered_views(selected_cohort):
    # Pie chart data (unfiltered)
    pie_chart_data = df['userIp'].value_counts().reset_index(name='count')
    pie_chart_data.columns = ['userIp', 'count']

    # Create the pie chart
    pie_chart = go.Pie(
        labels=pie_chart_data['userIp'],
        values=pie_chart_data['count'],
        hole=0.3,  # To make it a donut chart
    )

    # Table data (unfiltered)
    count_per_course_status = df.groupby(['course', 'status']).size().reset_index(name='count')

    # Create the table
    table = go.Table(
        columnwidth=[300, 200, 100],  # Specify the width for each column
        header=dict(
            values=['Course', 'Status', 'Count'],
            fill_color='paleturquoise',
            align='left',
            height=40  # Set header row height
        ),
        cells=dict(
            values=[
                count_per_course_status.course,
                count_per_course_status.status,
                count_per_course_status['count']
            ],
            fill_color='lavender',
            align='left',
            height=25  # Set cell height
        )
    )

    # Create subplots with specified layout
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "domain"}, {"type": "table"}]],
        subplot_titles=("Location Distribution", "Course Registration Status")
    )

    # Add pie chart to the first column
    fig.add_trace(pie_chart, row=1, col=1)

    # Add table to the second column
    fig.add_trace(table, row=1, col=2)

    # Update layout for spacing
    fig.update_layout(
        showlegend=True,
        width=1000,  # Total width of the figure
        height=500   # Total height of the figure
    )

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)









# In[16]:




# Initialize Dash app
app = dash.Dash(__name__)

# Define the layout of the Dash app
app.layout = html.Div([
    # Title
    html.H1("DOYEN DASH", style={'textAlign': 'center', 'padding': '10px 0'}),

    # Sidebar with dropdown for cohort selection
    html.Div([
        html.H2("Select Cohort"),
        dcc.Dropdown(
            id='cohort-dropdown',
            options=[{'label': f'Cohort {cohort}', 'value': cohort} for cohort in df['cohort'].unique()],
            value=df['cohort'].unique()[0],
            clearable=False
        )
    ], style={
        'width': '15%',  # Sidebar width
        'padding': '10px',
        'box-shadow': '2px 0px 5px rgba(0, 0, 0, 0.1)',  # Add some shadow for visual separation
        'background-color': '#f8f9fa'  # Light gray background for sidebar
    }),

    # Main content area
    html.Div([
        # Graph for filtered data
        html.Div([
            dcc.Graph(id='stacked-bar-chart', style={'height': '600px'})
        ], style={'width': '80%', 'display': 'inline-block', 'padding': '10px', 'vertical-align': 'top'}),

        # Table for filtered data
        html.Div([
            html.H4("Total Paid in EURO & NAIRA by Course and Cohort"),
            dash_table.DataTable(
                id='course-total-table',
                columns=[
                    {'name': 'Course', 'id': 'course'},
                    {'name': 'Total Paid in EURO', 'id': 'TotalpaidinEURO'},
                    {'name': 'Total Paid in NAIRA', 'id': 'TotalpaidinNAIRA'}
                ],
                style_table={'width': '20%'},
                style_cell={'textAlign': 'left'},
                style_header={'fontWeight': 'bold'},
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(248, 248, 248)'
                    }
                ]
            )
        ], style={'width': '20%', 'display': 'inline-block', 'padding': '10px', 'vertical-align': 'top'})
    ], style={'display': 'flex'}),

    # Table for course application count by cohort
    html.Div([
        html.H3("Count of Course Applications by Cohort"),
        dash_table.DataTable(
            id='per-cohort-course',
            columns=[
                {'name': 'Course', 'id': 'course'},
                {'name': 'Cohort', 'id': 'cohort'},
                {'name': 'Count', 'id': 'count'}
            ],
            style_table={'width': '100%'},
            style_cell={'textAlign': 'left'},
            style_header={'fontWeight': 'bold'},
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }
            ]
        )
    ], style={'padding': '10px', 'width': '60%'}),

    html.Div([
        html.H3("General Cohort distribution", style={'textAlign': 'center'}),  # Center align the heading
        dcc.Graph(id='pie-table-chart', style={'height': '500px'}),
    ], style={
        'width': '100%', 
        'display': 'flex', 
        'flexDirection': 'column',
        'alignItems': 'center',  # Center align content within the div
        'padding': '10px'
    })
])

@app.callback(
    Output('stacked-bar-chart', 'figure'),
    Output('course-total-table', 'data'),
    Output('per-cohort-course', 'data'),
    Input('cohort-dropdown', 'value')
)
def update_filtered_views(selected_cohort):
    # Filter the DataFrame based on the selected cohort
    filtered_df = df[df['cohort'] == selected_cohort]

    # Group by 'course' and 'sourceOfDiscovery', then count the occurrences
    count_source_of_discovery = filtered_df.groupby(['course', 'sourceOfDiscovery']).size().reset_index(name='count')

    # Create a stacked bar chart
    fig = px.bar(
        count_source_of_discovery,
        x='course',
        y='count',
        color='sourceOfDiscovery',
        title=f'Source of Discovery for Cohort {selected_cohort}',
        labels={'count': 'Count', 'course': 'Course'},
        barmode='stack'
    )

    # Group by 'course' and calculate the total amount paid in euros and naira for each course
    total_amount_in_courses = filtered_df.groupby('course')[['TotalpaidinEURO', 'TotalpaidinNAIRA']].sum().reset_index()

    # Group by 'course' and cohort
    no_of_courses = filtered_df.groupby(['cohort', 'course']).size().reset_index(name='count')

    return fig, total_amount_in_courses.to_dict('records'), no_of_courses.to_dict('records')

@app.callback(
    Output('pie-table-chart', 'figure'),
    Input('cohort-dropdown', 'value')  # We can keep this here for consistency, even though not needed
)

def update_unfiltered_views(selected_cohort):
    # Pie chart data (unfiltered)
    pie_chart_data = df['userIp'].value_counts().reset_index(name='count')
    pie_chart_data.columns = ['userIp', 'count']

    # Create the pie chart
    pie_chart = go.Pie(
        labels=pie_chart_data['userIp'],
        values=pie_chart_data['count'],
        hole=0.3,  # To make it a donut chart
    )

    # Table data (unfiltered)
    count_per_course_status = df.groupby(['course', 'status']).size().reset_index(name='count')

    # Create the table
    table = go.Table(
        columnwidth=[300, 200, 100],  # Specify the width for each column
        header=dict(
            values=['Course', 'Status', 'Count'],
            fill_color='paleturquoise',
            align='left',
            height=40  # Set header row height
        ),
        cells=dict(
            values=[
                count_per_course_status.course,
                count_per_course_status.status,
                count_per_course_status['count']
            ],
            fill_color='lavender',
            align='left',
            height=25  # Set cell height
        )
    )

    # Create subplots with specified layout
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "domain"}, {"type": "table"}]],
        subplot_titles=("Location Distribution", "Course Registration Status")
    )

    # Add pie chart to the first column
    fig.add_trace(pie_chart, row=1, col=1)

    # Add table to the second column
    fig.add_trace(table, row=1, col=2)

    # Update layout for spacing
    fig.update_layout(
        showlegend=True,
        width=800,  # Total width of the figure
        height=500   # Total height of the figure
    )

    return fig

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)  # Serve the Dash app


# In[17]:


# panel_app.py

import panel as pn

# Use the URL where the Dash app is running
dash_app_url = "http://localhost:8050"

# Create a Panel template and embed the Dash app using an iframe
template = pn.template.FastListTemplate(
    title="DOYEN DASH",
    main=[
        pn.pane.HTML(f'<iframe src="{dash_app_url}" width="450%" height="800" frameborder="0"></iframe>')
    ]
)

# Serve the Panel template
template.show()

# Note: For standalone script execution
if __name__ == '__main__':
    pn.serve(template, port=8058)

