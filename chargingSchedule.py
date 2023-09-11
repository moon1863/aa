#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 09:28:31 2023

@author: rakibulalam
"""

import dash
import dash_core_components as dcc #for chart
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input,Output
import pandas as pd

  
df=pd.read_excel("charging_schedule.xlsx",sheet_name="Sheet1")

app = dash.Dash(__name__)
application = app.server
app.title='Dash on AWS EB!'

vehicleID={999:([],[],[])}
for i in range(0,len(df)):
    tempKey=df["Vehicle_ID"].iloc[i]
    if tempKey not in vehicleID.keys():
        vehicleID[tempKey]=([],[],[])
    vehicleID[tempKey][0].append(df["CS_ID"].iloc[i])
    vehicleID[tempKey][1].append(df["Charging_time_hour"].iloc[i])
    vehicleID[tempKey][2].append(df["Charging_duration_minutes"].iloc[i])

vehicleID.pop(999)

app.layout = html.Div([
    html.H1("Optimized charging schedule"),
    html.Div("Choose vehicle ID"),
    
    dcc.Dropdown(
        id="first-dropdown",
        options=[
            {'label':'Vehicle0','value':0},
            {'label':'Vehicle1','value':1},
            {'label':'Vehicle2','value':2},
            {'label':'Vehicle3','value':3},
            {'label':'Vehicle4','value':4},
            {'label':'Vehicle5','value':5},
            {'label':'Vehicle6','value':6},
            {'label':'Vehicle7','value':7},
            {'label':'Vehicle8','value':8},
            {'label':'Vehicle9','value':9},
            {'label':'Vehicle10','value':10},
            {'label':'Vehicle11','value':11},
            {'label':'Vehicle12','value':12},
            {'label':'Vehicle13','value':13},
            {'label':'Vehicle14','value':14},
            {'label':'Vehicle15','value':15},
            {'label':'Vehicle16','value':16}
        ],
        value=0
    ),
    
    dcc.Graph(
        id="schedule",
    )
    
])

@app.callback(
    dash.dependencies.Output("schedule", "figure"),
    [dash.dependencies.Input("first-dropdown", "value")]
)
def update_fig(input_value):
    data = []
    bar1 = go.Bar(x=vehicleID[input_value][0], y=vehicleID[input_value][1], name="Start time of charging (24hr-clocktime)")
    bar2 = go.Bar(x=vehicleID[input_value][0], y=vehicleID[input_value][2], name="Duration of charging (mins)")
    data.append(bar1)
    data.append(bar2)
    layout = {'title': 'Vehicle ID:'+str(input_value)}
    return {
        'data': data,
        'layout': layout
    }
if __name__=="__main__":
    application.run(port='8080',debug=True)


