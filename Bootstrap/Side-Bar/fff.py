# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from flask import Flask
import pandas as pd
from pandas import DataFrame
from pandas import json_normalize
import pymongo
from pymongo import MongoClient
import plotly.graph_objs as go
import plotly.offline as pyo
import plotly.express as px
import numpy as np
import pytz, time
from datetime import datetime, tzinfo, timezone, timedelta, date
import dash_bootstrap_components as dbc
import random
from sqlalchemy import create_engine
from plotly.subplots import make_subplots


# %%
# constants
df = pd.read_csv('Bootstrap\Side-Bar\iranian_students.csv')
localTimezone = pytz.timezone('Asia/Singapore')
datetimeNow = datetime.now(localTimezone)


# %%
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY],
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}],
                suppress_callback_exceptions=True
                )


# %%
def serve_layoutOnReload():
    # styling the sidebar
    SIDEBAR_STYLE = {
        "position": "fixed",
        "top": 0,
        "left": 0,
        "bottom": 0,
        "width": "16rem",
        "padding": "2rem 1rem",
        "background-color": "#f8f9fa",
    }

    # padding for the page content
    CONTENT_STYLE = {
        "margin-left": "18rem",
        "margin-right": "2rem",
        "padding": "2rem 1rem",
    }

    sidebar = html.Div(
        [
            html.H2("Sidebar", className="display-4"),
            html.Hr(),
            html.P(
                "Number of students per education level", className="lead"
            ),
            dbc.Nav(
                [
                    dbc.NavLink("Home", href="/", active="exact"),
                    dbc.NavLink("Page 1", href="/page-1", active="exact"),
                    dbc.NavLink("Page 2", href="/page-2", active="exact"),
                ],
                vertical=True,
                pills=True,
            ),
        ],
        style=SIDEBAR_STYLE,
    )

    content = html.Div(id="page-content", children=[], style=CONTENT_STYLE)

    web_layout = html.Div([
        dcc.Location(id="url"),
        sidebar,
        content
    ])

    return web_layout


app.layout = serve_layoutOnReload
# app.layout = html.Div([
#     dcc.Location(id="url"),
#     sidebar,
#     content
# ])


# %%
@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")]
)
def render_page_content(pathname):
    if pathname == "/":
        return [
                html.H1('Kindergarten',
                        style={'textAlign':'center'}),
                dbc.Container([
                        dbc.Row([
                            dbc.Col([
                                html.P("Date picker:", className='text-right font-weight-bold mb-4'),
                                ],xs=12, sm=12, md=12, lg=5, xl=5),
                            dbc.Col([
                                dcc.DatePickerRange(id='date-range', 
                                                    min_date_allowed=date(2020, 6, 1),
                                                    max_date_allowed=datetimeNow.date(),
                                                    start_date=datetimeNow.date() - timedelta(days=7),
                                                    end_date=datetimeNow.date(), ),
                                ],xs=12, sm=12, md=12, lg=5, xl=5),], no_gutters=True, justify='center'),
                        
                        dbc.Row(
                            dbc.Col(html.H2(" ", className='text-center text-primary mb-4'), width=12)
                            ),
                        
                        dbc.Row([
                            dbc.Col([
                                dcc.Graph(id="students", figure={}),
                            ], xs=12, sm=12, md=12, lg=5, xl=5),], justify='center')
                ], fluid=True)
            ]
    elif pathname == "/page-1":
        return [
                html.H1('Grad School',
                        style={'textAlign':'center'}),
                dcc.Graph(id='bargraph',
                         figure=px.bar(df, barmode='group', x='Date',
                         y=['Girls Grade School', 'Boys Grade School']))
                ]
    elif pathname == "/page-2":
        return [
                html.H1('High School',
                        style={'textAlign':'center'}),
                dcc.Graph(id='bargraph',
                         figure=px.bar(df, barmode='group', x='Date',
                         y=['Girls High School', 'Boys High School']))
                ]
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )


# %%
@app.callback([Output("students", "figure")],
                [Input("date-range", "start_date"),
                 Input("date-range", "end_date")])
def update_charts(start_date, end_date):
    # read data upon refresh browser
    df = pd.read_csv('Bootstrap\Side-Bar\iranian_students.csv')

    # masks
    mask1 = (
        (df.Date >= pd.to_datetime(start_date))
        & (df.Date <= pd.to_datetime(end_date))
    )# daily sgym signups

    # filtered dataframes
    filtered_data1 = df.loc[mask1, :].reset_index(drop=True)

    # plots
    # daily sgym signups
    trace = []
    trace.append(go.Bar(
            x = filtered_data1['Date'],
            y = filtered_data1['Girls Kindergarten'],
            name = 'Count of students'
        ))
    
    # add moving average
    filtered_data1['Moving Avg'] = filtered_data1['Girls Kindergarten'].rolling(window=7, min_periods=1).mean()
    trace.append(go.Scatter(x=filtered_data1['Date'], y=filtered_data1['Moving Avg'], name = 'Rolling Mean=7'))
    
    students_fig = {'data': trace,
                            'layout': go.Layout(
                                {"title": {"text": "Student Count\n"
                                            '('+str(start_date)+' to '+str(end_date)+')', 
                                                "x": 0.05, "xanchor": "left"},
                                    "xaxis": {"fixedrange": False, 'title':'Date',   
                                                'tickmode':'linear', 'automargin':True},
                                    "yaxis": {"fixedrange": False, 'title':'Count of Signups'},
                                    'xaxis_tickformat':'%d %b',
                                    'title_font_size': 14,
                                    'hovermode':'closest',
                                    'legend_title_text':'Gym',
                                    'hovermode':'closest',
                                    },)   }
    
    return students_fig


# %%
if __name__=='__main__':
    app.run_server(debug=True, port=8050)


