#%%

import pandas as pd
from getData import getData
import numpy as np
from datetime import datetime
from syncData import syncData
import simplejson as json
from datetime import datetime
import schedule

#%%

def runScripts():

    print(print(datetime.now()))

    # Un-comment to update for latest data

    getData()

    # Using _preview will ensure new data does not overwrite the live data

    preview = ""
    # preview = "_preview"

    #%%

    # For deaths and reovered data

    def processData(filePath):
        
        includes = ["Australia", "Italy", "Japan", "China", "Korea, South", "United Kingdom", "US", "Singapore", "Iran", "Total"]
        
        df = pd.read_csv(filePath)

        df.loc['Total'] = df.sum(numeric_only=True, axis=0)
        
        df.loc[['Total'],["Country/Region"]] = "Total"
        
        df = df.groupby(["Country/Region"]).sum()
        
        df = df.drop(['Lat','Long'], axis=1)
        
        df = df.T
        
        df.index = pd.to_datetime(df.index, format="%m/%d/%y")
        
        df = df.sort_index(ascending=1)
        
        df.index = df.index.strftime('%Y-%m-%d')
        
        df = df[includes]
        
        return df

    deaths = processData("time_series_19-covid-Deaths.csv")
    recovered = processData("time_series_19-covid-Recovered.csv")

    deaths_daily = deaths.sub(deaths.shift())
    deaths_daily.iloc[0] = deaths.iloc[0]

    recovered_daily = recovered.sub(recovered.shift())
    recovered_daily.iloc[0] = recovered.iloc[0]

    #%%

    with open('latest.json') as json_file:
        latestJson = json.load(json_file)
        latestObj = []
        for row in latestJson['features']:
            latestObj.append(row['attributes'])    
            
        latest = pd.DataFrame(latestObj)
        
        latest_country = latest.groupby(["Country_Region"]).sum()
        latest_country.loc['Total'] = latest_country.sum()
        
        latestData = json.dumps(latest_country.reset_index().to_dict('records'))
        
        syncData(latestData, "2020/03/coronavirus-widget-data", "latest{preview}.json".format(preview=preview))
    #%%

    # For confirmed cases, since we want it for charts

    confirmed = pd.read_csv("time_series_19-covid-Confirmed.csv")

    exclude = ["Diamond Princess cruise ship"]

    includes = ["Australia", "Italy", "Japan", "China", "Korea, South", "United Kingdom", "US", "Singapore", "Iran", "Total"]

    shortlist = ["Australia", "United Kingdom", "US"]

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
    #%%
    confirmed_daily.to_csv("data-output/confirmed_daily.csv")

    #%%

    # To save locally
    deaths.reset_index().to_json('data-output/deaths.json', orient='records')
    deaths_daily.reset_index().to_json('data-output/deaths_daily.json', orient='records')

    over100.reset_index().to_json('data-output/confirmed.json', orient='records')
    confirmed_daily.reset_index().to_json('data-output/confirmed_daily.json', orient='records')

    recovered.reset_index().to_json('data-output/recovered.json', orient='records')
    recovered_daily.reset_index().to_json('data-output/recovered_daily.json', orient='records')

    # To uplodad to S3

    deathsData = json.dumps(deaths.reset_index().to_dict('records'))
    deathsDailyData = json.dumps(deaths_daily.reset_index().to_dict('records'))

    confirmedData = json.dumps(over100.reset_index().to_dict('records'))
    confirmedDailyData = json.dumps(confirmed_daily.reset_index().to_dict('records'))

    recoveredData = json.dumps(recovered.reset_index().to_dict('records'))
    recoveredDailyData = json.dumps(recovered_daily.reset_index().to_dict('records'))

    syncData(deathsData, "2020/03/coronavirus-widget-data", "deaths{preview}.json".format(preview=preview))
    syncData(deathsDailyData, "2020/03/coronavirus-widget-data", "deaths_daily{preview}.json".format(preview=preview))
    syncData(confirmedData, "2020/03/coronavirus-widget-data", "confirmed{preview}.json".format(preview=preview))
    syncData(confirmedDailyData, "2020/03/coronavirus-widget-data", "confirmed_daily{preview}.json".format(preview=preview))
    syncData(recoveredData, "2020/03/coronavirus-widget-data", "recovered{preview}.json".format(preview=preview))
    syncData(recoveredDailyData, "2020/03/coronavirus-widget-data", "recovered_daily{preview}.json".format(preview=preview))

    # Australian stuff

    aus_confirmed = confirmed[confirmed['Country/Region'] == "Australia"]

    aus_confirmed = aus_confirmed.drop(['Lat','Long', 'Country/Region'], axis=1)

    aus_confirmed = aus_confirmed.set_index('Province/State')

    aus_confirmed = aus_confirmed.T

    # aus_confirmed.to_csv('blah.csv')

    aus_confirmed.index = pd.to_datetime(aus_confirmed.index, format="%m/%d/%y")

    aus_confirmed = aus_confirmed.sort_index(ascending=1)

    aus_confirmed.index = aus_confirmed.index.strftime('%Y-%m-%d')

    most_recent = aus_confirmed[-1:]

    most_recent.to_csv("data-output/aus-recent.csv")

    print("done")