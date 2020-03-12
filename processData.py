#%%

import pandas as pd
from getData import getData
import numpy as np

# Un-comment to update for latest data

# getData()

confirmed = pd.read_csv("time_series_19-covid-Confirmed.csv")

exclude = ["Diamond Princess cruise ship"]

includes = ["Australia", "Italy", "Japan", "Mainland China", "Republic of Korea", "UK", "US", "Hong Kong SAR", "Singapore", "Iran (Islamic Republic of)"]

confirmed = confirmed.groupby(["Country/Region"]).sum()

over100 = confirmed[confirmed.iloc[ : , -2 ] > 50]

over100 = over100.drop(['Lat','Long'], axis=1)

over100 = over100.T

over100.index = pd.to_datetime(over100.index, format="%m/%d/%y")

over100 = over100.sort_index(ascending=1)

over100.index = over100.index.strftime('%Y-%m-%d') 

replace = {"Republic of Korea":"South Korea","Hong Kong SAR":"Hong Kong", "Iran (Islamic Republic of)":"Iran"}

pctChange = over100.pct_change()*100

pctChange = pctChange[includes]

#%%

# Days since 100 cases

since100 = pd.DataFrame()

for col in includes:
    print(col)
    start = (over100[col] >= 50).idxmax()
    tempSeries = over100[col][start:]
    tempSeries = tempSeries.replace({0:np.nan})
    tempSeries = tempSeries.reset_index()
    tempSeries = tempSeries.drop(['index'], axis=1)
    since100 = pd.concat([since100, tempSeries], axis=1)

since100 = since100.rename(columns=replace)

#%%

import plotly.graph_objs as go
import plotly.io as pio
from plotly.offline import plot
from yachtCharter import yachtCharter

#%%

# Log plot

data = [go.Scatter(
                x = since100.index,
                y = since100[col],
                mode='lines',
                name = col
            ) for col in since100.columns]

layout = go.Layout(
        title="Coronavirus confirmed cases",
        width=800,
        height=600,
        yaxis={"type":"log"}
        )   
    
fig = go.Figure(data=data, layout=layout)
    
# plot(fig, filename="plots/confirmed-cases")


template = [
        {
            "title": "Confirmed cases of Covid-19 for selected countries",
            "subtitle": "Showing the number of cases since the day of the 50th case, using a log scale",
            "footnote": "",
            "source": "<a href='https://www.arcgis.com/apps/opsdashboard/index.html#/bda7594740fd40299423467b48e9ecf6' target='_blank'>Johns Hopkins University</a>, based on a <a href='https://blog.grattan.edu.au/2020/03/australian-governments-can-choose-to-slow-the-spread-of-coronavirus-but-they-must-act-immediately/'>chart by the Grattan Institute</a>",
            "dateFormat": "",
            "yScaleType":"scaleLog",
            "xAxisLabel": "Days since 50th case",
            "yAxisLabel": "",
            "minY": "",
            "maxY":"100000",
            "periodDateFormat":"",
            "margin-left": "50",
            "margin-top": "20",
            "margin-bottom": "20",
            "margin-right": "20"
        }
    ]
key = []
periods = []
labels = []
chartId = [{"type":"linechart"}]
since100.fillna('', inplace=True)
since100 = since100.reset_index()
chartData = since100.to_dict('records')

yachtCharter(template=template, data=chartData, chartId=[{"type":"linechart"}], chartName="cases-of-covid-19-since-100-live")

#%%

# % change plot

data = [go.Scatter(
                x = pctChange.index,
                y = pctChange[col],
                mode='lines',
                name = col
            ) for col in pctChange.columns]

layout = go.Layout(
        title="Coronavirus confirmed cases",
        width=800,
        height=600
        )   
    
fig = go.Figure(data=data, layout=layout)
    
# plot(fig, filename="plots/confirmed-cases-pct")