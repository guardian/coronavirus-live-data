import plotly.graph_objs as go
import plotly.io as pio
from plotly.offline import plot
from getData import getData
from yachtCharter import yachtCharter
import pandas as pd
import numpy as np
import requests

#%%

getData()

#%%

states = requests.get('https://interactive.guim.co.uk/docsdata/1q5gdePANXci8enuiS4oHUJxcxC13d6bjMRSicakychE.json').json()['sheets']

#%%

state_order = ['NSW','VIC',	'QLD','SA', 'WA','TAS',	'ACT','NT']
   
states_df = pd.DataFrame(states['updates'])
states_df.Date = pd.to_datetime(states_df.Date, format="%d/%m/%Y")
states_df['Cumulative case count'] = pd.to_numeric(states_df['Cumulative case count'])
states_df = states_df.dropna(axis=0,subset=['Cumulative case count'])
states_df = states_df.sort_values(['Date','State', 'Cumulative case count']).drop_duplicates(['State', 'Date'], keep='last')

states_df = states_df.pivot(index='Date', columns='State', values='Cumulative case count')

#%%

states_df_daily = pd.DataFrame()

for col in state_order:
	print(col)
	tempSeries = states_df[col].dropna()
	tempSeries = tempSeries.sub(tempSeries.shift())
	tempSeries.iloc[0] = states_df[col].dropna().iloc[0]
	states_df_daily = pd.concat([states_df_daily, tempSeries], axis=1)

states_df_daily.iloc[0] = states_df.iloc[0]

#%%
# states_df.at['2020-03-19', 'NT'] = 0
# states_df.iloc[0] = 0

# states_df_daily = states_df.sub(states_df.shift())



date_index = pd.date_range(start='2020-01-23', end=states_df.index[-1])

states_df = states_df.reindex(date_index)

states_df_daily = states_df_daily.reindex(date_index)


states_df.index = states_df.index.strftime('%Y-%m-%d')

states_df_daily = states_df_daily.fillna(0)
states_df_daily.index = states_df_daily.index.strftime('%Y-%m-%d')

states_df = states_df.fillna(method='ffill')
states_df = states_df.fillna(0)
states_df = states_df[state_order]
states_df.to_csv('data-output/states.csv')

states_df_daily = states_df_daily[state_order]

states_df_daily.to_csv('data-output/states-daily.csv')

#%%





#%%

def processData(filePath):
        
    df = pd.read_csv(filePath)

    df.loc['Total'] = df.sum(numeric_only=True, axis=0)
    
    df.loc[['Total'],["Country/Region"]] = "Total"
    
    df = df.groupby(["Country/Region"]).sum()
    
    df = df.drop(['Lat','Long'], axis=1)
    
    df = df.T
    
    df.index = pd.to_datetime(df.index, format="%m/%d/%y")
    
    df = df.sort_index(ascending=1)
    
    df.index = df.index.strftime('%Y-%m-%d')
    
    
    
    return df

deaths = processData("time_series_19-covid-Deaths.csv")
recovered = processData("time_series_19-covid-Recovered.csv")
confirmed = processData("time_series_19-covid-Confirmed.csv")

mask = confirmed.iloc[-1] > 100
only100 = confirmed.loc[:, mask]

aus_confirmed = pd.read_csv("time_series_19-covid-Confirmed.csv")
aus_confirmed = aus_confirmed[aus_confirmed['Country/Region'] == "Australia"]
aus_confirmed = aus_confirmed.drop(['Lat','Long', 'Country/Region'], axis=1)
aus_confirmed = aus_confirmed.set_index('Province/State')
aus_confirmed = aus_confirmed.T
aus_confirmed = aus_confirmed.drop(['From Diamond Princess'], axis=1)
aus_confirmed.index = pd.to_datetime(aus_confirmed.index, format="%m/%d/%y")
aus_confirmed = aus_confirmed.sort_index(ascending=1)
aus_confirmed.index = aus_confirmed.index.strftime('%Y-%m-%d')

aus_confirmed.to_csv("data-output/aus-confirmed.csv")

#%%
# Days since >=50 cases

def makeSince100Chart(df):

    includes = ["Australia", "Italy", "Japan", "China", "Korea, South", "United Kingdom", "US", "Singapore", "Iran"]
    
    since100 = pd.DataFrame()
    
    lastUpdatedInt = df.index[-1]

    for col in includes:
        print(col)
        start = (df[col] >= 50).idxmax()
        tempSeries = df[col][start:]
        tempSeries = tempSeries.replace({0:np.nan})
        tempSeries = tempSeries.reset_index()
        tempSeries = tempSeries.drop(['index'], axis=1)
        since100 = pd.concat([since100, tempSeries], axis=1)


    template = [
            {
                "title": "Confirmed cases of Covid-19 for selected countries",
                "subtitle": "Showing the number of cases since the day of the 50th case for the given country, using a log scale. Last updated {date}".format(date=lastUpdatedInt),
                "footnote": "",
                "source": "<a href='https://www.arcgis.com/apps/opsdashboard/index.html#/bda7594740fd40299423467b48e9ecf6' target='_blank'>Johns Hopkins University</a>, based on a <a href='https://blog.grattan.edu.au/2020/03/australian-governments-can-choose-to-slow-the-spread-of-coronavirus-but-they-must-act-immediately/'>chart by the Grattan Institute</a>. Case count is affected by differing rates of testing for each country",
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

makeSince100Chart(only100)

#%%

def makeCumulativeChart(df):
    
    lastUpdatedInt = df.index[-1]

    template = [
            {
                "title": "Cumulative count of confirmed Covid-19 cases by state and territory",
                "subtitle": "Last updated {date}".format(date=lastUpdatedInt),
                "footnote": "",
                "source": " | Source: <a href='' target='_blank'>Guardian Australia analysis of state and territory data</a>",
                "dateFormat": "%Y-%m-%d",
                "xAxisLabel": "",
                "yAxisLabel": "Cumulative cases",
                "timeInterval":"day",
                "tooltip":"TRUE",
                "periodDateFormat":"",
                "margin-left": "50",
                "margin-top": "20",
                "margin-bottom": "20",
                "margin-right": "20",
				"xAxisDateFormat": "%b %d"
            }
        ]
    key = []
    periods = []
    labels = []
    chartId = [{"type":"stackedbarchart"}]
    df.fillna('', inplace=True)
    df = df.reset_index()
    chartData = df.to_dict('records')

    yachtCharter(template=template, data=chartData, chartId=chartId, chartName="australian-covid-cases-2020")

makeCumulativeChart(states_df)

def makeDailyChart(df):
    
    lastUpdatedInt = df.index[-1]

    template = [
            {
                "title": "Daily count of confirmed Covid-19 cases by state and territory",
                "subtitle": "Last updated {date}".format(date=lastUpdatedInt),
                "footnote": "",
                "source": " | Source: <a href='' target='_blank'>Guardian Australia analysis of state and territory data</a>",
                "dateFormat": "%Y-%m-%d",
                "xAxisLabel": "",
                "yAxisLabel": "Cumulative cases",
                "timeInterval":"day",
                "tooltip":"TRUE",
                "periodDateFormat":"",
                "margin-left": "50",
                "margin-top": "20",
                "margin-bottom": "20",
                "margin-right": "20",
				"xAxisDateFormat": "%b %d"
            }
        ]
    key = []
    periods = []
    labels = []
    chartId = [{"type":"stackedbarchart"}]
    df.fillna('', inplace=True)
    df = df.reset_index()
    chartData = df.to_dict('records')

    yachtCharter(template=template, data=chartData, chartId=chartId, chartName="australian-daily-covid-cases-2020")

makeDailyChart(states_df_daily)
    

#%%

# Old Stuff

'''

pctChange = over100.pct_change()*100

pctChange = pctChange[includes]

lastUpdatedInt = datetime.strftime(datetime.strptime(confirmed.columns[-1], "%m/%d/%y"), "%d %B, %Y")

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
    
plot(fig, filename="plots/confirmed-cases")

'''