#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State


# In[2]:


#mapbox_access_token = open('mapbox_token.txt').read()
import os
mapbox_access_token = os.environ.get('MAPBOX_TOKEN')


# In[3]:


collected = pd.read_csv('Collected.csv')
collected = collected.drop([col for col in collected.columns if col.startswith('Unnamed:')], axis =1)
print(collected.head())


# In[4]:


### scattermapbox with basic configuration
fig = go.Figure(go.Scattermapbox())

fig.update_layout(
            clickmode = 'event+select',
            hovermode = 'closest',
            autosize=True,
            margin= { 'r': 0, 't': 0, 'b': 0, 'l': 0 },
            mapbox = dict(
                accesstoken=mapbox_access_token,
                style = 'mapbox://styles/jiminlee22/cliszzibc01si01qp1o0le86c', 
                center = dict(lat = 40, lon = 17),
                zoom = 1.1
            ))


# In[5]:


# Create dictionary of author names for dropdown
authors_collected = [{'label' : name, 'value': name} for name in collected['Full_Name_en'].unique()]


# In[6]:


# Write a function that calculates zoom level
import math

def layout_two_points(d_lat, d_lon):
    R = 6371
    lat1_rad = math.radians(d_lat[0])
    lon1_rad = math.radians(d_lon[0])
    lat2_rad = math.radians(d_lat[1])
    lon2_rad = math.radians(d_lon[1])
    
    delta_lat = math.radians(d_lat[0]) - math.radians(d_lat[1])
    delta_lon = math.radians(d_lon[0])  - math.radians(d_lon[1])
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    distance = R * c 
    center = dict(lat = sum(d_lat)/2, lon = sum(d_lon)/2)

    if distance > 0:
        if distance <= 50:
            zoom_level = 8.5
        elif distance <= 100:
            zoom_level = 8
        elif distance <= 200:
            zoom_level = 7
        elif distance <= 600:
            zoom_level = 6
        elif distance <= 1600:
            zoom_level = 5
        elif distance <= 4000:
            zoom_level = 4
        elif distance <= 6500:
            zoom_level = 3
        elif distance <= 13000:
            zoom_level = 1.8
        else:
            zoom_level = 1.1
    else:
        zoom_level = 9
        
    return zoom_level, center


# In[7]:


# global variables

prev_next_click = 0
prev_prev_click = 0
prev_location = None
prev_zoom_in_click = 0
prev_zoom_out_click = 0


# In[8]:
from flask import Flask
server = Flask(__name__)

# Dash App
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# In[9]:


# app layout using scattermapbox 
app.layout = dbc.Container([
    dbc.Row(
        dbc.Col(
            html.H1("20th Century Korean Women Writers", style = {'font-family' : 'Palatino, serif'}),
            width={"size": 8, "offset": 3})
    ),
    dbc.Row([
        dbc.Col(
            dcc.Dropdown(
                id = 'author_dropdown',
                placeholder = 'Select an author',
                multi = False,
                options = authors_collected,
                style={'margin-right': '5px'}),
            width = {'size' : 4}
        ),
        dbc.Col(
            dcc.Dropdown(
                    id = 'location_dropdown',
                    placeholder = 'Select an author first',
                    multi = False,
                    options = [],
                    style={'margin-right': '5px'}),
            width = {'size' : 4}
        ),
        dbc.Col([
            html.Button('Next ▶', id = 'next_button', n_clicks=0, style={'margin-right': '10px'}),
            html.Button('Previous ◀︎', id = 'prev_button', n_clicks=0, style={'margin-right': '15px'}),
            html.Button("+", id="zoom_in", n_clicks=0, style={'margin-right': '10px'}),
            html.Button("-", id="zoom_out", n_clicks=0, style={'margin-right': '10px'})
            ]),
    ]),
    
    html.Div(style={'margin-bottom': '20px'}),
    
    dbc.Row([
        dbc.Col(
            dcc.Graph(id = 'map', 
                      figure = fig, 
                      config={'displayModeBar' : True,
                              'modeBarButtonsToRemove' : ['toImage', 'pan2d', 'select2d', 'lasso2d']}), 
            width = {'size' : 10, 'order' : 1}
        ),
        dbc.Col(  
            dbc.Stack([
                html.Div(id = 'image', style={'padding-bottom': '10px'}), 
                html.Div(id = 'destination', style={'padding-bottom': '10px'}),
                html.Div(id = 'info')
            ]),
            width = {'order' : 2})
    ])
])


# In[10]:


# Callback: change the options of the location dropdown depending on value of the author_dropdown 
@app.callback(
    [Output(component_id = 'location_dropdown', component_property = 'options'),
     Output(component_id = 'location_dropdown', component_property = 'placeholder')],
    Input(component_id = 'author_dropdown', component_property = 'value')
)
def location_dropdown(author):
    global prev_next_click, prev_prev_click
    if author is not None: 
        df = collected[collected['Full_Name_en'] == author].reset_index(drop = True)
        options = [{'label' : loc, 'value': loc} for loc in df['Location'].unique()]
        placeholder = 'Select a location'
        
        return options, placeholder        
    
    else:
        options = []
        placeholder = 'Location: Select an author first'
        return options, placeholder


# In[11]:


# Callback: change map based on author_dropdown and location_dropdown
@app.callback(
    [Output(component_id = 'map', component_property = 'figure'),
     Output(component_id = 'next_button', component_property = 'n_clicks'),
     Output(component_id = 'zoom_in', component_property = 'n_clicks'),
     Output(component_id = 'zoom_out', component_property = 'n_clicks')],
    [Input(component_id = 'author_dropdown', component_property = 'value'),
    Input(component_id = 'location_dropdown', component_property = 'value'),
    Input(component_id = 'next_button', component_property = 'n_clicks'),
    Input(component_id = 'zoom_in', component_property = 'n_clicks'),
    Input(component_id = 'zoom_out', component_property = 'n_clicks'),
    Input(component_id = 'prev_button', component_property = 'n_clicks')],
    State(component_id = 'map', component_property = 'figure'),
    prevent_initial_call=True
)
def scattermap(author, location, next_clicks, zoom_in_clicks, zoom_out_clicks, prev_clicks, figure):
    global prev_next_click, prev_location, prev_zoom_in_click, prev_zoom_out_click, prev_prev_click
        
    if author is not None: 
        df = collected[collected['Full_Name_en'] == author].reset_index(drop = True)
        data = go.Scattermapbox(
                    lat=df['Latitude'],
                    lon=df['Longitude'],
                    mode='markers',
                    marker={
                        'size': 10,
                        'opacity' : 1,
                        'color': 'rgb(252, 2, 138)'
                    },
                    unselected={'marker' : {'color': 'rgb(252, 2, 138)'}},
                    selected={'marker' : {'color':'rgb(0,0,0)'}},
                    hoverinfo='text',
                    hovertext=df['Location'],
                    customdata=list(zip(df['Location'], df['Date']))
        )
        data.showlegend = False
        
        if next_clicks == 0:
            figure['data'] = [data]
            
        elif (next_clicks > 1):
             for trace in figure['data'][1:next_clicks]:
                trace['marker']['color'] = 'rgb(252, 2, 138)'
                trace['line']['color'] = 'rgb(105,105,105)'
                
        #NEXT BUTTON 
        if (next_clicks > prev_next_click) and (next_clicks < len(df)):
            df_click = df.loc[[next_clicks-1, next_clicks]]
            d_lat = df_click['Latitude'].tolist()
            d_lon = df_click['Longitude'].tolist()
            trace = go.Scattermapbox(
                        lat=d_lat,
                        lon=d_lon,
                        mode='markers+lines',
                        line={
                            'color': 'rgb(107,142,35)'
                        },
                        marker = {
                            'color' : ['rgb(127,255,0)', 'rgb(0,100,0)'],
                            'size' : 10
                        },
                        hoverinfo='text',
                        hovertext=df_click['Location'],
                        selected={'marker' : {'color':'rgb(0,0,0)'}},
                        customdata=list(zip(df['Location'], df['Date']))
                )
            trace.showlegend = False
            figure['data'].append(trace)
            prev_next_click = next_clicks
        
        if next_clicks >= len(df):
            next_clicks = len(df)
        
        #PREV BUTTON
        if (prev_clicks > prev_prev_click) and (next_clicks - 1 > 0):
            prev_prev_click = prev_clicks
            
            figure['data'] = figure['data'][:next_clicks]
            figure['data'][next_clicks-1]['marker']['color'] = ['rgb(127,255,0)', 'rgb(0,100,0)']
            figure['data'][next_clicks-1]['line']['color'] = 'rgb(107,142,35)'
            next_clicks -= 1
            prev_next_click = next_clicks
        
        #LOCATION DROPDOWN
        if location is None:
            figure['layout']['mapbox']['zoom'] = 1.1
            figure['layout']['mapbox']['center'] = dict(lat = 40, lon = 17)
            
        if (location is not None) and (location != prev_location): 
            df_loc = df[df['Location'] == location].reset_index(drop = True)
            d_lat = df_loc['Latitude'].unique()[0]
            d_lon = df_loc['Longitude'].unique()[0]

            figure['layout']['mapbox']['zoom'] = 8.5
            figure['layout']['mapbox']['center'] = dict(lat = d_lat, lon = d_lon)
           
            prev_location = location

        #ZOOM-IN BUTTON
        if (next_clicks > 0) and (zoom_in_clicks > 0) and (zoom_in_clicks > prev_zoom_in_click):
            df_click = df.loc[[next_clicks-1, next_clicks]]
            d_lat = df_click['Latitude'].tolist()
            d_lon = df_click['Longitude'].tolist()
            zoom_level, center = layout_two_points(d_lat, d_lon)
            
            if (figure['layout']['mapbox']['zoom']) < zoom_level:
                figure['layout']['mapbox']['zoom'] = zoom_level
                figure['layout']['mapbox']['center'] = center
                    
            prev_zoom_in_click = zoom_in_clicks
            
        #ZOOM-OUT BUTTON
        if (zoom_out_clicks > 0) and (zoom_out_clicks > prev_zoom_out_click):
            if ((figure['layout']['mapbox']['zoom'] - 1.8)>= 2):
                zoom_level = figure['layout']['mapbox']['zoom'] - 1.8
                figure['layout']['mapbox']['zoom'] = zoom_level
                
                #if figure['layout']['mapbox']['zoom'] <= 2.5:
                    #if figure['layout']['mapbox']['center']['lon'] > 100:
                        #figure['layout']['mapbox']['center'] = dict(lat = 40, lon = 74)
                  
            else:
                figure['layout']['mapbox']['zoom'] = 1.1
                figure['layout']['mapbox']['center'] = dict(lat = 40, lon = 17)
            
            prev_zoom_out_click = zoom_out_clicks
            
        return figure, next_clicks, zoom_in_clicks, zoom_out_clicks
    
    else:
        next_clicks=0
        prev_clicks = 0
        zoom_in_clicks = 0
        zoom_out_clicks = 0
        prev_next_click =0
        prev_prev_click = 0
        prev_zoom_in_click = 0
        prev_zoom_out_click = 0
        prev_location = None
        
        return {
            'data' : [go.Scattermapbox()],
            'layout': go.Layout(
                        clickmode = 'event+select',
                        hovermode = 'closest',
                        autosize=True,
                        margin= { 'r': 0, 't': 0, 'b': 0, 'l': 0 },
                        mapbox = dict(
                            accesstoken=mapbox_access_token,
                            style = 'mapbox://styles/jiminlee22/cliszzibc01si01qp1o0le86c', 
                            center = dict(lat = 40, lon = 17),
                            zoom = 1.1
            )
        )
    }, next_clicks, zoom_in_clicks, zoom_out_clicks


# In[12]:


# Callback: print destination or end statement 
@app.callback(
    Output(component_id = 'destination', component_property = 'children'),
    [Input(component_id = 'next_button', component_property = 'n_clicks'),
     Input(component_id = 'author_dropdown', component_property = 'value')]
)
def end_statement(next_clicks, author):

    if author is not None: 
        df = collected[collected['Full_Name_en'] == author].reset_index(drop = True)
                
        if (next_clicks >= len(df)):
            statement = [html.Span("You have reached the end")]
            return statement
        
        elif (next_clicks > 0):
            start_date = df.loc[next_clicks-1]['Date']
            end_date = df.loc[next_clicks]['Date']
            start = df.loc[next_clicks-1]['Location']
            end = df.loc[next_clicks]['Location']
            statement = [
                html.Span(f"Trip #{next_clicks}:", style={'color': 'black', "font-size": "18px", "font-weight": "bold"}),
                html.Div([
                    html.Span(f"{start_date}", style = {'color' : 'black'}),
                    html.Span(" ~ ", style = {'color' : 'black', "font-weight": "bold"}),
                    html.Span(f"{end_date}", style = {'color' : 'black'})
                ]),
                html.Div([
                    html.Span("From ", style = {'color': 'black'}),
                    html.Span(start, style={'color': 'rgb(50,205,50)'})
                ]),
                html.Div([
                    html.Span("To ", style={'color': 'black'}),
                    html.Span(end, style={'color': 'rgb(21,71,52)'})
                ])
            ]           
            return statement

        else:
            return None
    else:
        return None 


# In[13]:


# Callback: click marker and info is displayed
@app.callback(
    Output(component_id = 'info', component_property = 'children'),
    [Input(component_id = 'map', component_property = 'clickData'),
     Input(component_id = 'author_dropdown', component_property = 'value')]
)
def display_info(clickData, author):
    if (clickData is not None):
        if author is not None:
            info = "Selected:\nLocation - " + str(clickData['points'][0]['customdata'][0]) + "\nDate - " + str(clickData['points'][0]['customdata'][1])
            statement = [
                    html.Span("Selected Marker:"),
                    html.Div(html.Span("Location - " + str(clickData['points'][0]['customdata'][0]), style={"padding-left": "40px"})),
                    html.Div(html.Span("Date - " + str(clickData['points'][0]['customdata'][1]), style={"padding-left": "40px"}))
                ]   
            return statement


# In[14]:


# Images
#print(list(zip(collected['Name_ko'].unique(), collected['Full_Name_en'].unique())))
# 한국민족문화대백과사전
# https://encykorea.aks.ac.kr/


# In[15]:


# Callback: click marker and picture is displayed
@app.callback(
    Output(component_id = 'image', component_property = 'children'),
    Input(component_id = 'author_dropdown', component_property = 'value')
)
def display_img(author):
    if author is None:
        return None
    else:
        source = r'assets/{}.jpg'.format(author)
        return html.Img(src = source, alt='image', style={'height':'100%','width':'100%'})


# In[16]:


if __name__ == '__main__':
    app.run_server(debug=False)


# In[17]:


# primary task:
 # export this app using RENDER 


# In[18]:


# write a read_me file (file that explains how to use this app for Dr. Lee)
    #(explain why u have male authors in there too)


# In[19]:


# review before sending it to Dr. Lee

# ADJUST ZOOM LEVELS IN LAYOUT_TWO_POINTS FUNCTION 
    #(Na hye Seok IS HELPFUL)
# need to check if the dataframe is in the order


# In[20]:


# Issues
# OPTION: multipage that allows to choose between single or multiple authors
# Destination Statement : padding (long destinations-->)
# WHEN LOCATION IS SELECTED, THE MARKER OF THAT PARTICULAR LOCATION HAVE A DIFFERENT COLOR AND THE LOCATION TEXT ALSO HAS A DIFFERENT COLOR
# add an input box (type in NUMBER of the trip)
# EAST SEA OF JAPAN LABEL (DOUBLE-CHECK)


# In[21]:


# Next Steps 
# hoverinfo (html formatting)

