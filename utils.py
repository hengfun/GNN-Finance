#%%
import collections
import numpy as np
import os
import tushare as ts
import pandas as pd
import matplotlib.pyplot as plt
import datetime

#%%
def prepare_prices(stocks):
    data = {}

    stock_files = os.listdir('stocks')
    for i in stocks.code:
        try:
            file_name = [ j for j in stock_files if i in j][0]
            print(i,[ j for j in stock_files if i in j][0])
            data[i]=pd.read_csv(os.path.join('stocks',file_name))
        except:
            print(i)
            pass

    df = pd.concat(data,axis=1)
    prices = df.swaplevel(0,1,axis=1)['close']     
    dates = df.swaplevel(0,1,axis=1)['date'].iloc[:,0]
    time = df.swaplevel(0,1,axis=1)['time'].iloc[:,0]
    date = pd.to_datetime(dates.values)
    time = pd.to_datetime(time.values)
    index = [datetime.datetime.combine(d.date(),t.time()) for d,t in zip(date,time)]
    prices.index = pd.to_datetime(index)
    return prices

#%%
def get_index_data():
    dirs = os.listdir('IH')
    dirs.sort()
    index_files = [d for d in dirs if '2018' in d]
    data= collections.defaultdict(dict)
    for index_file in index_files:
        futures = os.listdir(os.path.join('IH',index_file))
        futures.sort()
        for future in futures:
            future_file = os.path.join("IH",index_file,future)
            future = future.replace('.csv.gz',"")
            data[index_file][future] = pd.read_csv(future_file)
    return data

def get_volumes(data):
    vol = collections.defaultdict(dict)
    for date in data.keys():
        for contract in data[date].keys():
            vol[date][contract] = data[date][contract].volume.sum()
    return pd.DataFrame(vol).T

def get_futures(data):
    vols= get_volumes(data)
    max_vol = []
    for i,j in vols.iterrows():
        max_vol.append(data[i][j.idxmax()])
    contracts = pd.concat(max_vol,axis=0)
    contracts.index = pd.to_datetime(contracts.datetime.values)
    return contracts

def update_index(df):
    new_index =[]
    for i in range(df.shape[0]):
        date = pd.to_datetime(df.date.values[i]).date()
        time = pd.to_datetime(df.time.values[i]).time()
        new = datetime.datetime.combine(date,time)
        new_index.append(new)
    df.index = pd.Index(new_index)
    return df

def get_futures_index(contracts):
    index = pd.read_csv('SH000016.csv')
    index = update_index(index)
    new_df = pd.concat([contracts.close,index.close],axis=1)
    new_df.columns = ['future','index']
    return new_df



if __name__=="__main__":
    sse50 = ts.get_sz50s()
    cs500 = ts.get_zz500s()
    sse50_prices= prepare_prices(sse50)
    cs500_prices = prepare_prices(cs500)

    data = get_index_data()
    contracts = get_futures(data)
    futures = get_futures_index(contracts)
    # futures.to_pickle('future_index.pickle')
    
#%%


#%%
