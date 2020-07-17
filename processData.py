#%%

import pandas as pd
from getData import getData
import numpy as np
from datetime import datetime
from syncData import syncData
import simplejson as json
from datetime import datetime
import requests
import traceback
from sendEmail import sendEmail

#%%

def runScripts():
	print(1/0)
	state_order = ['NSW','VIC',	'QLD','SA', 'WA','TAS',	'ACT','NT']
	
	states = requests.get('https://interactive.guim.co.uk/docsdata/1q5gdePANXci8enuiS4oHUJxcxC13d6bjMRSicakychE.json').json()['sheets']
	
	states_df = pd.DataFrame(states['updates'])
	states_df.Date = pd.to_datetime(states_df.Date, format="%d/%m/%Y")
	states_df['Cumulative case count'] = pd.to_numeric(states_df['Cumulative case count'])
	states_df = states_df.dropna(axis=0,subset=['Cumulative case count'])
	states_df = states_df.sort_values(['Date','State', 'Cumulative case count']).drop_duplicates(['State', 'Date'], keep='last')
	
	states_df_og = states_df
	
	states_df = states_df.pivot(index='Date', columns='State', values='Cumulative case count')
	
	states_df_daily = pd.DataFrame()
	
	for col in state_order:
		print(col)
		tempSeries = states_df[col].dropna()
		tempSeries = tempSeries.sub(tempSeries.shift())
		tempSeries.iloc[0] = states_df[col].dropna().iloc[0]
		states_df_daily = pd.concat([states_df_daily, tempSeries], axis=1)
	
	states_df_daily.iloc[0] = states_df.iloc[0]
	
	date_index = pd.date_range(start='2020-01-22', end=states_df.index[-1])
	
	
	states_df_daily = states_df_daily.reindex(date_index)
	
	states_df_daily = states_df_daily.fillna(0)
	states_df_daily.index = states_df_daily.index.strftime('%Y-%m-%d')
	states_df_daily = states_df_daily[state_order]
	daily_total = pd.DataFrame()
	daily_total['Australia'] = states_df_daily.sum(axis=1)
	
		
	print(print(datetime.now()))
	
	# Un-comment to update for latest data
	
	getData()
	
	# Using _preview will ensure new data does not overwrite the live data
	
	preview = ""
	# preview = "_preview"
	
	with open('latest.json') as json_file:
		latestJson = json.load(json_file)
		latestObj = []
		shortlist = ["Australia", "United Kingdom", "US"]
		
		for row in latestJson['features']:
			latestObj.append(row['attributes'])    
			
		latest = pd.DataFrame(latestObj)
		
		latest_country = latest.groupby(["Country_Region"]).sum()
		latest_country.loc['Total'] = latest_country.sum()
		
		latestData = json.dumps(latest_country.reset_index().to_dict('records'))
		
		syncData(latestData, "2020/03/coronavirus-widget-data", "latest{preview}.json".format(preview=preview))
	
	# For confirmed cases, since we want it for charts
	
	confirmed = pd.read_csv("time_series_covid19_confirmed_global.csv")
	
	shortlist = ["United Kingdom", "US", "Total"]
	
	confirmed.loc['Total'] = confirmed.sum(numeric_only=True, axis=0)
	
	confirmed.loc[['Total'],["Country/Region"]] = "Total"
	
	confirmed_country = confirmed.groupby(["Country/Region"]).sum()
	
	over100 = confirmed_country[confirmed_country.iloc[ : , -1 ] > 100]
	
	over100 = over100.drop(['Lat','Long'], axis=1)
	
	over100 = over100.T
	
	over100.index = pd.to_datetime(over100.index, format="%m/%d/%y")
	
	over100 = over100.sort_index(ascending=1)
	
	over100.index = over100.index.strftime('%Y-%m-%d')
	
	confirmed_daily = over100.sub(over100.shift())
	confirmed_daily.iloc[0] = over100.iloc[0]
	
	confirmed_daily_short = confirmed_daily[shortlist]
	confirmed_daily_short['Australia'] = daily_total['Australia']
	confirmed_daily_short[confirmed_daily_short < 0] = 0
	
	confirmed_daily.to_csv("data-output/confirmed_daily.csv")
	confirmed_daily.reset_index().to_json('data-output/confirmed_daily.json', orient='records')
	
	# To uplodad to S3
	
	confirmedDailyData = json.dumps(confirmed_daily_short.reset_index().to_dict('records'))
	
	syncData(confirmedDailyData, "2020/03/coronavirus-widget-data", "confirmed_daily{preview}.json".format(preview=preview))

	print("Done, data updated")

# def doThings():
# 	try:
# 		runScripts()
# 	except Exception:
# 		print(traceback.format_exc())
# 		sendEmail(traceback.format_exc(), "corona data alers", ["nick.evershed@theguardian.com"])

runScripts()			