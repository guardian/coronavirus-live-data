#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from getData import getData
from yachtCharter import yachtCharter
from syncDoc import syncDoc
import pandas as pd
import numpy as np
import requests
import simplejson as json
from syncData import syncData


#%%


url = "https://covid.ourworldindata.org/data/ecdc/new_cases.csv"
print("Getting", url)
r = requests.get(url)
with open("ecdc-new-cases.csv", 'w') as f:
	f.write(r.text)
	
url = "https://covid.ourworldindata.org/data/ecdc/total_cases.csv"
print("Getting", url)
r = requests.get(url)
with open("ecdc-total-cases.csv", 'w') as f:
	f.write(r.text)


		

#%%



ecdc_new = pd.read_csv("ecdc-new-cases.csv")
ecdc_new = ecdc_new.set_index('date')

ecdc_cum = pd.read_csv("ecdc-total-cases.csv")

ecdc_cum = ecdc_cum.set_index('date')
# ecdc_cum = pd.to_numeric(ecdc_cum)
ecdc_high = ecdc_cum [ecdc_cum.columns[ecdc_cum.iloc[-1]>5000]]
ecdc_high = ecdc_high.drop(['World'], axis=1)

# ecdc_high.index.rename("index", inplace=True) 

# ecdc_high = ecdc_high.rename(columns={"date":"index"})



#%%


countries = list(ecdc_high.columns)
# countries.remove("World")


ecdc_new = ecdc_new[countries]
ecdc_new.fillna(0, inplace=True)
ecdc_high.fillna(0, inplace=True)

confirmedDailyData = json.dumps(ecdc_new.reset_index().to_dict('records'))
syncData(confirmedDailyData, "2020/03/coronavirus-widget-data", "confirmed_daily_ecdc.json")

confirmedDailyData = json.dumps(ecdc_high.reset_index().to_dict('records'))
syncData(confirmedDailyData, "2020/03/coronavirus-widget-data", "confirmed_total_ecdc.json")



ecdc_new_restack = ecdc_new.stack().reset_index()
ecdc_new_restack = ecdc_new_restack.rename(columns={"level_0":"Date","level_1":"Country",0:"Cases"})


#%%

def makeDailyCountryChart(df):
	
	lastUpdatedInt = df.date.iloc[-1]

	template = [
			{
				"title": "Daily count of confirmed Covid-19 cases by country",
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

	yachtCharter(template=template, data=chartData, chartId=chartId, chartName="country-daily-covid-cases-2020")

makeDailyCountryChart(ecdc_new_restack)