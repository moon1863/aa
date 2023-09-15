#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 12 19:11:58 2023

@author: rakibulalam
"""

import dash
import dash_core_components as dcc #for chart
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input,Output
import pandas as pd
import plotly.express as px
import numpy as np
import dash_bootstrap_components as dbc
from dash import dash_table
from plotly.subplots import make_subplots
import base64

external_stylesheets = [dbc.themes.BOOTSTRAP]

df=pd.read_excel("schedule.xlsx",sheet_name="Sheet1")
df['CS_ID']=df['CS_ID'].map(str)
df['Charging_time_hour']=df['Charging_time_hour'].map(lambda x: round(x,2) )
df['Charging_duration_minutes']=df['Charging_duration_minutes'].map(lambda x: round(x,2) )

df2=pd.read_excel("schedule.xlsx",sheet_name="Sheet2")
df2['PlatoonAt']=df2['PlatoonAt'].map(str)
df2['PlatoonTime']=df2['PlatoonTime'].map(lambda x: round(x,2) )
df2=df2.sort_values(by=['vehicleID','PlatoonTime'],ascending=[True,True])
#####################
# to adjust zooming of map based on tightening the boundary of scatterplotted points
def tightZoom(x):
    x1=np.max(x['lat'])
    x2=np.min(x['lat'])
    y1=np.max(x['long'])
    y2=np.min(x['long'])
    max_bound = max(abs(x1-x2), abs(y1-y2)) * 111
    return 11.5 - np.log(max_bound)

coord={}
for i in range(0,len(df2)):
    if coord.get(df2.iloc[i,3]) is None:
        coord[df2.iloc[i,3]]=[df2.iloc[i,4],df2.iloc[i,5]]
    
def find_coord(x):
    return {'lat': coord[x][0],
            'lon': coord[x][1]}


######################
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

vehicleID={999:([],[],[])}
for i in range(0,len(df)):
    tempKey=df["Vehicle_ID"].iloc[i]
    if tempKey not in vehicleID.keys():
        vehicleID[tempKey]=([],[],[])
    vehicleID[tempKey][0].append(df["CS_ID"].iloc[i])
    vehicleID[tempKey][1].append(df["Charging_time_hour"].iloc[i])
    vehicleID[tempKey][2].append(df["Charging_duration_minutes"].iloc[i])

vehicleID.pop(999)

options=[]
for i in range(max(df['Vehicle_ID'])+1):
    options.append( {'label':'Vehicle'+str(i),'value':i})

################

test1_png = 'ucf.png'
test1_base64 = base64.b64encode(open(test1_png, 'rb').read()).decode('ascii')

test2_png = 'plotly.png'
test2_base64 = base64.b64encode(open(test2_png, 'rb').read()).decode('ascii')

app.layout=html.Div(children=[
    dbc.Row([
        dbc.Col(html.Div(html.Img(src='data:image/png;base64,{}'.format(test1_base64), 
                style={'height':'50%', 'width':'50%'}))),#style inside html.Image()
        
        dbc.Col(html.H1("Dashboard for Charging and Platooning Schedule"),
                style={'color': 'red', 'fontSize': 40, 'textAlign': 'center'},
                    width={"size":8, "offset":0}), # width inside dbc.Col
        dbc.Col(html.Div(html.Img(src='data:image/png;base64,{}'.format(test2_base64), 
                style={'height':'100%', 'width':'100%'}))) 
        ]),
    
    dbc.Row(
        dbc.Col(html.Div(children=[
                dcc.Dropdown(
                    id="first-dropdown",
                    options=options,
                    value=0
                )]), width={"size":6, "offset":0}),
        justify="center"
        ),
    dbc.Row(
        dbc.Col(html.H1("Charging Schedule"),
                style={'color': 'Blue', 'fontSize': 20, 'textAlign': 'left'},
                    width={"size":8, "offset":0})), # width inside dbc.Col
    dbc.Row(
        [
            dbc.Col(html.Div(children=[dcc.Graph(id="schedule",style={'width': '70vh', 'height': '50vh'})]), 
                    width={"size":6, "offset":0}, align="center"),
            dbc.Col(html.Div([dcc.Graph(id="map", style={'width': '60vh', 'height': '40vh'})]), 
                    width={"size":6, "offset":0}),
        ],justify="center"
        ),
    dbc.Row(
        dbc.Col(html.H1("Platooning Schedule"),
                style={'color': 'Blue', 'fontSize': 20, 'textAlign': 'left'},
                    width={"size":8, "offset":0})), # width inside dbc.Col
    dbc.Row(
        [
            dbc.Col(dash_table.DataTable(
            id="platooningDecision",
            columns=[
                #{"name":i,"id":i} for i in sorted(df2.columns,reverse=True)
                 {'name': 'PlatoonWith', 'id': 'PlatoonWith'},
                 {'name': 'PlatoonTime', 'id': 'PlatoonTime'},
                 {'name': 'PlatoonAt', 'id': 'PlatoonAt'}
                ],
            #page_current=0,
            #page_size=10,
            #page_action='custom',
            style_cell={
                    'padding-right': '1px',
                    'padding-left': '1px',
                    'text-align': 'center',
                    'marginLeft': 'auto',
                    'marginRight': 'auto'
                },
            fixed_rows={'headers': True},
            style_data={
                'whiteSpace': 'normal',
                'height': 'auto',
                'lineHeight': '1px'
                },
            style_table={
            'height': 300,
            'overflowY': 'auto',
            'width': 480
        },
            
            ), width={"size":3, "offset":0}, 
               align="center",
               style={
                   'textAlign': 'center',
                   "margin-left":"50px",
                   "margin-right":"0px"
        }),
    
        dbc.Col(html.Div([dcc.Graph(id="platooningDecisionMap")], 
                style={'width': '70vh', 'height': '10vh'}),
                width={"size":5, "offset":2}),
        
        ])
])
    
##################
    

@app.callback(
    dash.dependencies.Output("schedule", "figure"),
    dash.dependencies.Output("map", "figure"),
    [dash.dependencies.Input("first-dropdown", "value")]
)
def update_fig(input_value):
    #data = []
    # Create figure with secondary y-axis
    fig = go.Figure(
    data=[
        go.Bar(x=vehicleID[input_value][0], y=vehicleID[input_value][1], name="Charging time", yaxis='y', offsetgroup=1),
        go.Bar(x=vehicleID[input_value][0], y=vehicleID[input_value][2], name="Charging duration", yaxis='y2', offsetgroup=2)
    ],
    layout={
        'xaxis': {'title': 'Charging station ID'},
        'yaxis': {'title': 'Time (hr)'},
        'yaxis2': {'title': 'Duration (min)', 'overlaying': 'y', 'side': 'right'},
        'margin':{'l':100,'r':0,'t':0}
    }
    )

    # Change the bar mode
    fig.update_layout(barmode='group')
   
    
    #bar1 = go.Bar(x=vehicleID[input_value][0], y=vehicleID[input_value][1], name="Start time of charging (24hr-clocktime)")
    #bar2 = go.Bar(x=vehicleID[input_value][0], y=vehicleID[input_value][2], name="Duration of charging (mins)")
    #data.append(fig)
    #data.append(bar2)
    #layout_schedule = {'title': 'Vehicle ID:'+str(input_value)}
    
    MBToken = 'pk.eyJ1IjoicmFsYW0xODYzIiwiYSI6ImNsbWdrZHR4ajI0cHIzcHBjdmsxMWp1YTEifQ.WP57CglH_5qrm68h3UdxBQ'
    #'pk.eyJ1Ijoic2NvaGVuZGUiLCJhIjoiY2szemMxczZoMXJhajNrcGRsM3cxdGdibiJ9.2oazpPgLvgJGF9EBOYa9Wg'
    px.set_mapbox_access_token(MBToken)

    #map_data=[]
    map1 = px.scatter_mapbox(df[df['Vehicle_ID']==input_value], lat="lat", lon="long",\
                        color="CS_ID", size="Charging_time_hour",text="CS_ID",\
                        color_continuous_scale=px.colors.cyclical.IceFire, size_max=15,\
                        zoom=tightZoom(df[df['Vehicle_ID']==input_value]))
                        #title="Location of CS in Map")
    map1.update_traces(textposition='top center')
    map1.update_layout(
        title_x=0.5,
        title_y=0,
        margin={"l": 0, "r": 0, "b": 0, "t": 0}
    )
    
    return [
        #{'data': data,'layout': layout_schedule},
        fig,
        map1
    ]

@app.callback(
    Output('platooningDecision', 'data'),
    #Input('platooningDecision', "page_current"),
    #Input('platooningDecision', "page_size"),
    Input('first-dropdown','value'))

#def update_table(page_current,page_size,input_value):
def update_table(input_value):
    df2_temp=df2[df2['vehicleID']==input_value]
    df2_temp=df2_temp[['PlatoonWith','PlatoonTime','PlatoonAt']]
    #return df2_temp.iloc[
    #    page_current*page_size:(page_current+ 1)*page_size
    #].to_dict('records')
    return df2_temp.to_dict('records')

@app.callback(
    Output('platooningDecisionMap', 'figure'),
    Input('first-dropdown','value'),
    Input('platooningDecision', 'active_cell'))

    
def update_map(input_value,cell_value):
    MBToken = 'pk.eyJ1IjoicmFsYW0xODYzIiwiYSI6ImNsbWdrZHR4ajI0cHIzcHBjdmsxMWp1YTEifQ.WP57CglH_5qrm68h3UdxBQ'
    #'pk.eyJ1Ijoic2NvaGVuZGUiLCJhIjoiY2szemMxczZoMXJhajNrcGRsM3cxdGdibiJ9.2oazpPgLvgJGF9EBOYa9Wg'
    px.set_mapbox_access_token(MBToken)

    df2_temp=df2[df2['vehicleID']==input_value]
    df2_temp=df2_temp.sort_values(by=["PlatoonTime"], ascending=[True])
    if cell_value is None:
        map2 = px.scatter_mapbox(df2_temp[df2_temp['vehicleID']==input_value], lat="lat", lon="long",\
                            color="PlatoonAt",text="PlatoonAt",
                            color_continuous_scale=px.colors.cyclical.IceFire, size_max=15,\
                            zoom=tightZoom(df2_temp[df2_temp['vehicleID']==input_value]))
    else:
        map2 = px.scatter_mapbox(df2_temp[df2_temp['vehicleID']==input_value], lat="lat", lon="long",\
                            color="PlatoonAt",text="PlatoonAt",
                            color_continuous_scale=px.colors.cyclical.IceFire, size_max=15,\
                            center=find_coord(df2_temp.iloc[cell_value['row'],cell_value['column']+1]),
                            zoom=7.5)
            #
    map2.update_traces(textposition='top center')
    map2.update_layout(
        title_x=0.5,
        title_y=0,
        margin={"l": 70, "r": 0, "b": 140, "t": 0})
    
    
    return map2


if __name__=="__main__":
    app.run(host='0.0.0.0', port='8050',debug=True)
