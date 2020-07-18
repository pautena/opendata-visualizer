import pandas as pd
import io
import numpy as np
import requests
from app import settings


def get_confirmed_cases_ccaa_df():
    r = requests.get(settings.TOTAL_CONFIRMED_CASES_CCAA_URL)

    if r.status_code == 200:
        df= pd.read_csv(io.StringIO(r.content.decode('utf-8')),index_col="cod_ine")
        df=df.reset_index()
        df.to_csv('tmp/data.csv')
        return df
    else:
        print(f"error fetching csv. status code: {r.status_code}")
        return pd.DataFrame()

def get_confirmed_cases_df():
    r = requests.get(settings.TOTAL_CONFIRMED_CASES_URL)

    if r.status_code == 200:
        df= pd.read_csv(io.StringIO(r.content.decode('utf-8')),index_col="date")
        df.to_csv('tmp/data.csv')
        return df
    else:
        print(f"error fetching csv. status code: {r.status_code}")
        return pd.DataFrame()
    
def get_deaths_df():
    r = requests.get(settings.TOTAL_DEATHS_URL)

    if r.status_code == 200:
        df= pd.read_csv(io.StringIO(r.content.decode('utf-8')),index_col="date")
        df.replace(0, np.nan, inplace=True)
        df.to_csv('tmp/data.csv')
        return df
    else:
        print(f"error fetching csv. status code: {r.status_code}")
        return pd.DataFrame()

