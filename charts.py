import plotly.graph_objs as go
import plotly.io as pio
from plotly.offline import plot
from getData import getData
from yachtCharter import yachtCharter
from syncDoc import syncDoc
import pandas as pd
import numpy as np
import requests

state_order = ['NSW','VIC',	'QLD','SA', 'WA','TAS',	'ACT','NT']

#%%

getData()

#%%

states = requests.get('https://interactive.guim.co.uk/docsdata/1q5gdePANXci8enuiS4oHUJxcxC13d6bjMRSicakychE.json').json()['sheets']


#%%
   
states_df = pd.DataFrame(states['updates'])
states_df.Date = pd.to_datetime(states_df.Date, format="%d/%m/%Y")
states_df['Cumulative case count'] = pd.to_numeric(states_df['Cumulative case count'])
states_df = states_df.dropna(axis=0,subset=['Cumulative case count'])
states_df = states_df.sort_values(['Date','State', 'Cumulative case count']).drop_duplicates(['State', 'Date'], keep='last')

states_df_og = states_df

states_df = states_df.pivot(index='Date', columns='State', values='Cumulative case count')

#%%

totals_df = pd.DataFrame(states['latest totals'])

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

total_cum = pd.DataFrame()
total_cum['Total'] = states_df.sum(axis=1)
total_cum['pct_change'] = total_cum['Total'].pct_change()
total_cum = total_cum["2020-02-20":]
total_cum = total_cum[:-1]

states_df.to_csv('data-output/states.csv')

states_df_daily = states_df_daily[state_order]

daily_total = pd.DataFrame()
daily_total['Total'] = states_df_daily.sum(axis=1)


# daily_total['pct_change'] = daily_total['Total'].pct_change()
# daily_total = daily_total["2020-03-10":]


states_df_daily.to_csv('data-output/states-daily.csv')

restack_states_daily = states_df_daily.stack().reset_index()

restack_states_daily = restack_states_daily.rename(columns={"level_0":"Date","level_1":"State",0:"Cases"})

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

# deaths = processData("time_series_19-covid-Deaths.csv")
# recovered = processData("time_series_covid19_confirmed_global.csv")
confirmed = processData("time_series_covid19_confirmed_global.csv")

mask = confirmed.iloc[-1] > 100
only100 = confirmed.loc[:, mask]

deaths = processData("time_series_covid19_deaths_global.csv")
mask = confirmed.iloc[-1] > 10
only10deaths = deaths.loc[:, mask]

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

	includes = ["Australia", "Italy", "Spain", "Japan", "China", "Korea, South", "United Kingdom", "US", "Iran", "Singapore", "Sweden"]
	
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
				"maxY": "",
				"periodDateFormat":"",
				"margin-left": "50",
				"margin-top": "30",
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
# Days since >=10 deaths

def makeSince10DeathsChart(df):

	includes = ["Australia", "Italy", "Spain", "Japan", "China", "Korea, South", "United Kingdom", "US", "Iran", "Sweden"]
	
	since10deaths = pd.DataFrame()
	
	lastUpdatedInt = df.index[-1]

	for col in includes:
		print(col)
		start = (df[col] >= 10).idxmax()
		tempSeries = df[col][start:]
		tempSeries = tempSeries.replace({0:np.nan})
		tempSeries = tempSeries.reset_index()
		tempSeries = tempSeries.drop(['index'], axis=1)
		since10deaths = pd.concat([since10deaths, tempSeries], axis=1)


	template = [
			{
				"title": "Deaths due to Covid-19 for selected countries",
				"subtitle": "Showing the number of deaths since the day of the 10th death for the given country, using a log scale. Last updated {date}".format(date=lastUpdatedInt),
				"footnote": "",
				"source": "<a href='https://www.arcgis.com/apps/opsdashboard/index.html#/bda7594740fd40299423467b48e9ecf6' target='_blank'>Johns Hopkins University</a>, based on a <a href='https://blog.grattan.edu.au/2020/03/australian-governments-can-choose-to-slow-the-spread-of-coronavirus-but-they-must-act-immediately/'>chart by the Grattan Institute</a>. Case count is affected by differing rates of testing for each country",
				"dateFormat": "",
				"yScaleType":"scaleLog",
				"xAxisLabel": "Days since 10th death",
				"yAxisLabel": "",
				"minY": "10",
				"maxY": "",
				"periodDateFormat":"",
				"margin-left": "50",
				"margin-top": "30",
				"margin-bottom": "20",
				"margin-right": "20"
			}
		]
	key = []
	periods = []
	labels = []
	chartId = [{"type":"linechart"}]
	since10deaths.fillna('', inplace=True)
	since10deaths = since10deaths.reset_index()
	chartData = since10deaths.to_dict('records')

	yachtCharter(template=template, data=chartData, chartId=[{"type":"linechart"}], chartName="deaths-since-10-live")

makeSince10DeathsChart(only10deaths)

#%%

def makeTimelineChart(df):
	df = df[:-1]
	lastUpdatedInt = df.index[-1]	
	
	labels = [{"x1":"2020-02-01","x2":"2020-02-11","y1":50,"y2":0,"text":"China arrivals blocked","align":"end","hide":""},
			{"x1":"2020-03-01","x2":"2020-03-11","y1":80,"y2":0,"text":"Iran arrivals blocked","align":"end","hide":""},
			{"x1":"2020-03-05","x2":"2020-03-15","y1":120,"y2":0,"text":"South Korean arrivals blocked","align":"end","hide":""},
			{"x1":"2020-03-11","x2":"2020-03-21","y1":240,"y2":0,"text":"Italy arrivals blocked","align":"end","hide":""},
			{"x1":"2020-03-15","x2":"2020-03-25","y1":430,"y2":0,"text":"Outdoor gatherings limited to 500 persons","align":"end","hide":""},
			{"x1":"2020-03-16","x2":"2020-03-26","y1":430,"y2":30,"text":"Self-isolation for overseas travellers, cruise ships blocked for 30 days","align":"end","hide":""},
			{"x1":"2020-03-18","x2":"2020-03-28","y1":430,"y2":60,"text":"Indoor gatherings limited to 100 persons","align":"end","hide":""},
			{"x1":"2020-03-19","x2":"2020-03-29","y1":430,"y2":90,"text":"Borders closed to non-citizens and residents","align":"end","hide":""},
			{"x1":"2020-03-23","x2":"2020-04-02","y1":430,"y2":120,"text":"Pubs / clubs closed, restaurants take-away only","align":"end","hide":""},
			{"x1":"2020-03-24","x2":"2020-04-03","y1":430,"y2":150,"text":"Ban on Australians travelling overseas","align":"end","hide":""},
			{"x1":"2020-03-26","x2":"2020-04-05","y1":430,"y2":180,"text":"Expanded testing criteria","align":"end","hide":""},
			{"x1":"2020-03-28","x2":"2020-04-07","y1":430,"y2":210,"text":"Mandatory isolation in hotels for travellers","align":"end","hide":""},
			{"x1":"2020-03-30","x2":"2020-04-09","y1":430,"y2":0,"text":"All gatherings 2 persons only","align":"end","hide":""}]
	
	details = [
			{
				"title": "Timeline of coronavirus measures v daily case count",
				"subtitle": "This chart shows the total number of cases reported each day for Australia, with annotations showing national measures introduced to limit the spread of the coronavirus. Measures are shown starting from the date they're introduced through to ten days later, which is a rough estimate of the time we might expect to see any effect on cases, according to <a href='https://pursuit.unimelb.edu.au/articles/flattening-the-curve-to-help-australia-s-hospitals-prepare'>researchers from the University of Melbourne</a>. Last updated {date}".format(date=lastUpdatedInt),
				"footnote": "",
				"source": "Guardian Australia, based on a chart by <a href='https://colab.research.google.com/drive/1X72xXEm1FCYpwo5OiRGhDUelMyicRj2L'>Ian Warrington</a>",
				"dateFormat": "%Y-%m-%d",
				"yScaleType":"",
				"xAxisLabel": "Days since 10th death",
				"yAxisLabel": "",
				"minY": "10",
				"maxY": "",
				"periodDateFormat":"",
				"margin-left": "40",
				"margin-top": "250",
				"margin-bottom": "20",
				"margin-right": "20"
			}
		]
	key = []
	periods = []
	chartId = [{"type":"timeline"}]
	df.fillna('', inplace=True)
	df = df.reset_index()
	chartData = df.to_dict('records')

	syncDoc(template=details, data=chartData, chartId=chartId, chartName="1xEijW_9nGVP55-CtmMSyIdOYWP9YYwbs-xZYoAeHEso", labels=labels)

makeTimelineChart(daily_total)

#%%


total_cum.index = pd.to_datetime(total_cum.index, format="%Y-%m-%d")
total_cum['pct_change'] = total_cum['pct_change']*100
total_cum['5 day average'] = total_cum['pct_change'].rolling(5).mean()
total_cum.index = total_cum.index.strftime('%Y-%m-%d')
# total_cum.to_csv('data-output/total-cumulative.csv')

def makePercentGrowth(df):
	df = df[['pct_change','5 day average']]
	df.rename(columns={"pct_change": "% growth in cases"}, inplace=True)
	lastUpdatedInt =  df.index[-1]
	
	template = [
			{
				"title": "Percent growth in Australian coronavirus cases",
				"subtitle": "Showing the percent change in the daily cumulative total of confirmed coronavirus cases since 20 February, and a five day rolling average of the percent change. Last updated {date}".format(date=lastUpdatedInt),
				"footnote": "",
				"source": "Guardian Australia, based on a charts produced by Gideon Meyerowitz-Katz",
				"dateFormat": "%Y-%m-%d",
				"yScaleType":"",
				"xAxisLabel": "",
				"yAxisLabel": "",
				"minY": "",
				"maxY": "",
				"periodDateFormat":"",
				"margin-left": "50",
				"margin-top": "30",
				"margin-bottom": "20",
				"margin-right": "10"
			}
		]
	key = []
	periods = []
	labels = []
	chartId = [{"type":"linechart"}]
	df.fillna('', inplace=True)
	df = df.reset_index()
	chartData = df.to_dict('records')

	yachtCharter(template=template, data=chartData, chartId=[{"type":"linechart"}], chartName="percent-change-corona-2020")

makePercentGrowth(total_cum)

#%%

def makeCumulativeChart(df):
	
	lastUpdatedInt = df.index[-1]

	template = [
			{
				"title": "Cumulative count of confirmed Covid-19 cases by state and territory",
				"subtitle": "The most recent day is usually based on incomplete data. Last updated {date}".format(date=lastUpdatedInt),
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
	key = [
		{"key":"NSW","colour":"#000000"},
		{"key":"VIC","colour":"#0000ff"},
		{"key":"QLD","colour":"#9d02d7"},
		{"key":"SA","colour":"#cd34b5"},
		{"key":"WA","colour":"#ea5f94"},
		{"key":"TAS","colour":"#fa8775"},
		{"key":"ACT","colour":"#ffb14e"},
		{"key":"NT","colour":"#ffd700"}
		]
	periods = []
	labels = []
	chartId = [{"type":"stackedbarchart"}]
	df.fillna('', inplace=True)
	df = df.reset_index()
	chartData = df.to_dict('records')

	yachtCharter(template=template, data=chartData, chartId=chartId, chartName="australian-covid-cases-2020", key=key)

makeCumulativeChart(states_df)

#%%

def makeDailyChart(df):
	
	lastUpdatedInt = df.index[-1]

	template = [
			{
				"title": "Daily count of confirmed Covid-19 cases by state and territory",
				"subtitle": "The most recent day is usually based on incomplete data. Last updated {date}".format(date=lastUpdatedInt),
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
	key = [
		{"key":"NSW","colour":"#000000"},
		{"key":"VIC","colour":"#0000ff"},
		{"key":"QLD","colour":"#9d02d7"},
		{"key":"SA","colour":"#cd34b5"},
		{"key":"WA","colour":"#ea5f94"},
		{"key":"TAS","colour":"#fa8775"},
		{"key":"ACT","colour":"#ffb14e"},
		{"key":"NT","colour":"#ffd700"}
		]
	periods = []
	labels = []
	chartId = [{"type":"stackedbarchart"}]
	df.fillna('', inplace=True)
	df = df.reset_index()
	chartData = df.to_dict('records')

	yachtCharter(template=template, data=chartData, chartId=chartId, chartName="australian-daily-covid-cases-2020", key=key)

makeDailyChart(states_df_daily)
	
#%%

def makeDailyStatesChart(df):
	
	lastUpdatedInt = df['Date'].iloc[-1]

	template = [
			{
				"title": "Daily count of confirmed Covid-19 cases by state and territory",
				"subtitle": "The most recent day is usually based on incomplete data. Last updated {date}".format(date=lastUpdatedInt),
				"footnote": "",
				"source": " | Source: <a href='' target='_blank'>Guardian Australia analysis of state and territory data</a>",
				"dateFormat": "%Y-%m-%d",
				"xAxisLabel": "",
				"yAxisLabel": "Cumulative cases",
				"timeInterval":"day",
				"tooltip":"<strong>Date: </strong>{{#nicedate}}Date{{/nicedate}}<br/><strong>Cases: </strong>{{Cases}}",
				"periodDateFormat":"",
				"margin-left": "50",
				"margin-top": "5",
				"margin-bottom": "20",
				"margin-right": "25",
				"xAxisDateFormat": "%b %d"
			}
		]
	key = []
	periods = []
	labels = []
	chartId = [{"type":"smallmultiples"}]
	df.fillna('', inplace=True)
	chartData = df.to_dict('records')

	yachtCharter(template=template, data=chartData, chartId=chartId, chartName="australian-states-daily-covid-cases-2020")

makeDailyStatesChart(restack_states_daily)

#%%

testing_pm = totals_df[['State or territory', 'Tests per million', 'Last updated']]
testing_pm['Color'] = "rgb(227, 26, 28)"
testing_pm.loc[testing_pm['State or territory'] == 'National', 'Color'] = "rgb(31, 120, 180)"
testing_pm['Tests per million'] = pd.to_numeric(testing_pm['Tests per million'])
testing_pm = testing_pm.sort_values(by=['Tests per million'], ascending=False)

#%%
def makeStatesTestingChart(df):
	
	lastUpdatedInt = df['Last updated'].iloc[-1]

	template = [
			{
				"title": "Covid-19 tests performed per one million people for Australian states and territories",
				"subtitle": "Showing the number of coronavirus tests carried out adjusted for population, using ABS population estimates for September 2019. Last updated {date}".format(date=lastUpdatedInt),
				"footnote": "",
				"source": "<a href='' target='_blank'>Guardian Australia analysis of state and territory data</a>",
				"dateFormat": "%Y-%m-%d",
				"xAxisLabel": "",
				"yAxisLabel": "Cumulative cases",
				"timeInterval":"day",
				"minX":"0",
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
	chartId = [{"type":"horizontalbar"}]
	options = [{"enableShowMore":"0"}]
	df.fillna('', inplace=True)
	chartData = df.to_dict('records', )

	yachtCharter(template=template, data=chartData, chartId=chartId, options=options, chartName="australian-states-testing-2020")

makeStatesTestingChart(testing_pm)

#%%

hospitals = totals_df[['State or territory','Deaths','Current hospitalisation','Current ICU','Current ventilator use', 'Last updated']]

def makeHospitalsTable(df):
	
	lastUpdatedInt = df['Last updated'].iloc[-1]

	df = df.drop(['Last updated'], axis=1)

	template = [
			{
				"title": "Deaths and hospitalisation figures by state and territory",
				"subtitle": "NSW hospitalisation figures include admissions under the Hospital in the Home program. Last updated {date}".format(date=lastUpdatedInt),
				"footnote": "",
				"source": "Guardian Australia / Department of Prime Minister and Cabinet"
			}
		]
	key = []
	periods = []
	labels = []
	chartId = [{"type":"table"}]
	options = [{"enableShowMore":"0"}]
	df.fillna('', inplace=True)
	chartData = df.to_dict('records', )

	yachtCharter(template=template, data=chartData, chartId=chartId, options=options, chartName="deaths-hospital-corona-2020")

makeHospitalsTable(hospitals)

#%%

# Old Stuff



#%%

# Data from covid19data.com.au

'''
sources = requests.get('https://interactive.guim.co.uk/docsdata/1_vY9rYf2M-lYvTRS6PVbS5kesy_31Ih_8R51pFW2GnY.json').json()['sheets']

sources_df = pd.DataFrame()

sources_cols = ['']

source_cols = ["Overseas - New","Local Known - New","Local Unknown - New","Under investigation - New"]

nsw_sources = pd.DataFrame(sources['NSW'])
vic_sources = pd.DataFrame(sources['VIC'])
vic_sources = vic_sources[1:]

nsw_sources[""] = nsw_sources[""] + "/2020"
vic_sources[""] = vic_sources[""] + "/2020"

nsw_sources[""] = pd.to_datetime(nsw_sources[""], format="%d/%m/%Y")
vic_sources[""] = pd.to_datetime(vic_sources[""], format="%d/%m/%Y")

nsw_sources = nsw_sources.set_index([""])
vic_sources = vic_sources.set_index([""])


nsw_sources = nsw_sources[source_cols]
vic_sources = vic_sources[source_cols]

for col in source_cols:
 	nsw_sources[col] = pd.to_numeric(nsw_sources[col])
 	vic_sources[col] = pd.to_numeric(vic_sources[col])


sources_df = nsw_sources + vic_sources

sources_df['Total local'] = sources_df["Local Known - New"] + sources_df["Local Unknown - New"]	
sources_df.index = sources_df.index.strftime('%Y-%m-%d')
'''

# Data from NSW data gov and Vic scrape


#%%

def makeTransmissionChart(df):
	
	df = df[["Overseas - New",'Total local',"Under investigation - New"]]
	df.rename(columns={"Overseas - New": "Overseas", "Under investigation - New": "Under investigation", "Total local": "Local"}, inplace=True)
	lastUpdatedInt =  df.index[-1]
	
	template = [
			{
				"title": "Source of Covid-19 infections for NSW and Victoria",
				"subtitle": "Showing the daily count of new cases by the source of infection. Last updated {date}".format(date=lastUpdatedInt),
				"footnote": "",
				"source": "<a href='https://www.covid19data.com.au/' target='_blank'>covid19data.com.au</a>",
				"dateFormat": "%Y-%m-%d",
				"yScaleType":"",
				"xAxisLabel": "",
				"yAxisLabel": "",
				"minY": "",
				"maxY": "",
				"periodDateFormat":"",
				"margin-left": "50",
				"margin-top": "30",
				"margin-bottom": "20",
				"margin-right": "10"
			}
		]
	key = []
	periods = []
	labels = []
	chartId = [{"type":"linechart"}]
	df.fillna('', inplace=True)
	df = df.reset_index()
	chartData = df.to_dict('records')

	yachtCharter(template=template, data=chartData, chartId=[{"type":"linechart"}], chartName="transmission-sources-line-2020")

# makeTransmissionChart(sources_df)
	

#%%

# data1 = go.Scatter(
# 				x = total_cum.index,
# 				y = total_cum['pct_change'],
# 				mode='lines',
# 				name='% change'
# 			) 

# data2 = go.Scatter(
# 				x = total_cum.index,
# 				y = total_cum['rolling'],
# 				mode='lines',
# 				name='% change'
# 			) 

# layout = go.Layout(
# 		title="% change",
# 		width=800,
# 		height=600
# 		)   

# data = [data1,data2]	

# fig = go.Figure(data=data, layout=layout)
# 	
# plot(fig, filename="plots/cum-aus-pct-change")

#%%

# daily_total.index = pd.to_datetime(daily_total.index, format="%Y-%m-%d")

# blah = go.Scatter(
# 				x = daily_total.index,
# 				y = daily_total['pct_change'],
# 				mode='lines',
# 				name='% change'
# 			) 

# layout = go.Layout(
# 		title="% change",
# 		width=800,
# 		height=600
# 		)   

# data = [blah]	

# fig = go.Figure(data=data, layout=layout)
# 	
# plot(fig, filename="plots/daily-aus-pct-change")



#%%

# Log plot
'''
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