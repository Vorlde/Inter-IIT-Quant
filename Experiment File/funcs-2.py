import pandas as pd
import numpy as np
import datetime
from datetime import datetime
import plotly.graph_objs as go
import pandas as pd
import pyfolio
import warnings
import matplotlib.pyplot as plt
warnings.filterwarnings("ignore")


def resample_to_constant_volume(df, volume_per_candle, convertTime= False):
    # sort by time
    #df = df.sort_values(by='time')
    # create cumulative volume column
    df['cumulative_volume'] = df['volume'].cumsum()
    
    #print(len(df))
    # initialize the new dataframe to hold resampled data
    resampled_df = pd.DataFrame(columns=['open', 'high', 'low', 'close','volume',"date"])
    
    start_index = 0
    end_index = 0
    cumulative_volume = 0
    for i in range(len(df)):
        cumulative_volume += df.iloc[i]['volume']
        end_index = i
        if cumulative_volume >= volume_per_candle : # make function dynamic in next round
            candle_df = df.iloc[start_index:end_index+1]
            open_price = candle_df.iloc[0]['open']
            high_price = candle_df['high'].max()
            low_price = candle_df['low'].min()
            close_price = candle_df.iloc[-1]['close']
            date_end = df.iloc[start_index]["date"]
            #x =  pd.to_datetime(datetime.strptime(mask, '%Y-%m-%d %H:%M:%S'))
            ## similarly for date_end,, this is to quickly find what 5 minute candle it belong to
            #date_end = x.strftime(f"%Y-%m-%d %H:{5*int(x.minute/5)}:%S")
            if convertTime:
                mask = df.iloc[end_index]["date"].split("+")[0]
                x =  pd.to_datetime(datetime.strptime(mask, '%Y-%m-%d %H:%M:%S'))
                ## similarly for date_end,, this is to quickly find what 5 minute candle it belong to
                temp = ("0"+str(5*int(x.minute/5)))
                date_end = x.strftime(f"%Y-%m-%d %H:{temp[-2:]}:%S")
            """resampled_df = resampled_df.append({'open': open_price, 'high': high_price, 'low': low_price, 
                                                'close': close_price, 'volume': cumulative_volume,
                                                 "date_end": date_end}, 
                                                 ignore_index=True)"""
            for i in range(int(1)):
                resampled_df = resampled_df.append({'open': open_price, 'high': high_price, 'low': low_price, 
                                                    'close': close_price, 'volume': cumulative_volume,
                                                     "date": date_end}, 
                                                     ignore_index=True)
            cumulative_volume = 0
            start_index = end_index + 1
    
    if start_index < len(df):
        candle_df = df.iloc[start_index:len(df)]
        open_price = candle_df.iloc[0]['open']
        high_price = candle_df['high'].max()
        low_price = candle_df['low'].min()
        close_price = candle_df.iloc[-1]['close']
        volume = sum(candle_df["volume"])
        date_end = df.iloc[start_index]["date"]
        #x =  pd.to_datetime(datetime.strptime(mask, '%Y-%m-%d %H:%M:%S'))
        ## similarly for date_end,, this is to quickly find what 5 minute candle it belong to
        #date_end = x.strftime(f"%Y-%m-%d %H:{5*int(x.minute/5)}:%S")
        if convertTime:
            mask = df.iloc[end_index]["date"].split("+")[0]
            x =  pd.to_datetime(datetime.strptime(mask, '%Y-%m-%d %H:%M:%S'))
            ## similarly for date_end,, this is to quickly find what 5 minute candle it belong to
            temp = ("0"+str(5*int(x.minute/5)))
            date_end = x.strftime(f"%Y-%m-%d %H:{temp[-2:]}:%S")
        resampled_df = resampled_df.append({'open': open_price, 'high': high_price, 'low': low_price, 'close': close_price, 'volume': volume,"date": str(date_end)}, ignore_index=True)

    return resampled_df
from datetime import timedelta
def is_body_size_greater_than_nx_average(dataframe, index,atr_multiple,look_back):
    body_sizes = (dataframe['close'] - dataframe['open']).loc[index - look_back:index].abs()
    #print(body_sizes,"efb")
    average_body_size = body_sizes.mean()
    #print(average_body_size)
    current_body_size = abs(dataframe['close'].loc[index] - dataframe['open'].loc[index])
    return current_body_size > atr_multiple * average_body_size


def imbalance_from_volume(df, dateTime_index_to_check, context = {}):
    
    ind = df[df["date"] == dateTime_index_to_check].index[0]
   
    
#     x =  pd.to_datetime(datetime.strptime(dateTime_index_to_check, '%Y-%m-%d %H:%M:%S')+timedelta(minutes=1))
#     endTime = x.strftime(f"%Y-%m-%d %H:%M:%S")

#     end_index = (df[df["date"] == endTime].index)
#     if len(end_index):
#         end_index=end_index[0] ## corner case 15:30
#     else:
#         return False
    
    volume_per_candle = df["volume"].rolling(window=200).mean().rolling(window=30).quantile(0.7).loc[ind]
    if context:
        vol_resampled_data1 = resample_to_constant_volume(context["resampled_candles"], volume_per_candle ,convertTime = True)
        context["resampled_candles"] = vol_resampled_data1
   
    
#     index_in_vol = vol_resampled_data1.index[-1]#vol_resampled_data1[vol_resampled_data1["date_end"] == dateTime_index_to_check].index[0]
    #print(index_in_vol,"jk")
    #print((vol_resampled_data1['volume'][index_in_vol]),volume_per_candle)
    if(((df['volume'][ind])/volume_per_candle) > 1.3): 
        return True
    else :
        return False
def is_body_size_greater_than_3x_average(dataframe, index,atr_multiple,look_back):   #price-time 
    body_sizes = (dataframe['close'] - dataframe['open']).loc[index - look_back:index].abs()
    #print(body_sizes)
    average_body_size = body_sizes.mean()
    #print(average_body_size,"Wrv__________")
    current_body_size = abs(dataframe['close'].loc[index] - dataframe['open'].loc[index])
    #print(current_body_size,"current")
    return current_body_size > atr_multiple * average_body_size

def imbalance_zone(df,dateTime_index_to_check,look_back=30):   #return imbalance zone ( price levels)
    imbalance_candle = df[df["date"] == dateTime_index_to_check].index[0]
    verify_candle  = imbalance_candle+1
    current_candle = imbalance_candle+2

    
    if is_body_size_greater_than_3x_average(df,imbalance_candle,1.2,look_back):
        upper = min(df["low"].loc[imbalance_candle-look_back:imbalance_candle-1])
        lower = df["high"].loc[verify_candle]
        #print(upper,lower)

        if (upper-lower) > 0 :
            return [ lower , upper ]  ## test in future the difference of lines more than some % of body

        else :
            return [0 , 0]
    else:
        return [0 , 0]
def filter_candles_at_index(df, index, body_threshold = 10, untouched_threshold = 20):
    # Calculate the body of the specified candle
    #index = df[df["date"] == dateTime_index_to_check].index[0]
#     print(index)
    df['body'] = df['close'] - df['open']
    body_threshold = (body_threshold+1)*df["body"].mean()
#     print(df["body"])
    body = df.loc[index]['body']
#     print(df)
    # Select only the specified candle if the body is high
    if abs(body) >= body_threshold:
        # Find the percentage of the price range covered by the body that has not been touched by the previous 10 candles
        df['body_min'] = df[['open', 'close']].min(axis=1)
        df['body_max'] = df[['open', 'close']].max(axis=1)
        df['prev_min'] = df['body_min'].shift(1).rolling(window=10).min()
        df['prev_max'] = df['body_max'].shift(1).rolling(window=10).max()
        df['price_range_untouched_min'] = df['body_min'].where(df['body_min'] > df['prev_max'], 0)
        df['price_range_untouched_max'] = df['body_max'].where(df['body_max'] < df['prev_min'], 0)
        df['price_range_untouched'] = df[['price_range_untouched_min', 'price_range_untouched_max']].max(axis=1) - df[['price_range_untouched_min', 'price_range_untouched_max']].min(axis=1)
        df['untouched_percentage'] = df['price_range_untouched'].abs() / df['body'].abs()
        # Select only the specified candle if the percentage is large
        if df.at[index, 'untouched_percentage'] >= untouched_threshold:
            return True
        else:
            return False
    else:
        return False
    
def volCheck(df,dateTime_index_to_check):
    ind = df[df["date"] == dateTime_index_to_check].index[0]
    x =  pd.to_datetime(datetime.strptime(dateTime_index_to_check, '%Y-%m-%d %H:%M:%S')+timedelta(minutes=5))
    #temp = ("0"+str(5*int((x.minute+5)/5)))
    endTime = x.strftime(f"%Y-%m-%d %H:%M:%S")
    # ind2 = df[df["date"] == endTime].index[0]
    # df = df[:ind+1]
    #print(endTime)
    end_index = (df[df["date"] == endTime].index)
    if len(end_index):
        end_index=end_index[0] ## corner case 15:30
    else:
        return False
    
    #print(data["volume"].rolling(window=80000).mean()[ind])
    #vol_resampled_data = resample_to_constant_volume(df[ind-2000:end_index],df["volume"].rolling(window=80000).mean()[ind]*1.7)
    
    volume_per_candle = df["volume"].rolling(window=8000).quantile(0.95).loc[ind]*2.5
    vol_resampled_data1 = resample_to_constant_volume(df.loc[ind-2000:end_index], volume_per_candle ,convertTime = True)
    index = vol_resampled_data1.index[-1]
    return filter_candles_at_index(vol_resampled_data1,index)

    

from collections import defaultdict

def to_intervals(data,n):   # to convert it n minute candle 
    # Read in the data from the text file
    data
    data = data.reset_index()
    data = np.array(data)
    """data = []
    name = "data_2017.txt" #input()
    with open(name, 'r') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            # Ignore the first column (stock name)
            data.append(row[1:])"""

    # Convert the data to n-minute intervals
    interval_data =  defaultdict(list)
    for row in data:
        date = row[1].split()[0]
        time = row[1].split()[1].split("+")[0][:-3]
        if time == "09:08:00":
            continue

        open_price = float(row[2])
        high_price = float(row[3])
        low_price = float(row[4])
        close_price = float(row[5])
        volume = float(row[6])
        # Extract the interval from the time and use it as the key in the dictionary
        interval = int(time[-2:]) // n
        interval = f"{time[:2]}:{interval * n:02d}"
        interval = str(date) +" " + interval + ":00"
        interval_data[interval].append((date, time, open_price, high_price, low_price, close_price, volume))

    # Calculate the final open, high, low, and close prices for each interval
    final_prices = {}
    for interval, prices in interval_data.items():
        # Unpack the tuples into separate lists for each price type
        dates, times, opens, highs, lows, closes, volume = zip(*prices)
        # The final open price is the same as the first open price in the interval
        final_open = opens[0]

        # The final high price is the highest of all the high prices in the interval
        final_high = max(highs)
        # The final low price is the lowest of all the low prices in the interval
        final_low = min(lows)
        # The final close price is the same as the last close price in the interval
        final_close = closes[-1]
        # The final volume will be the sum of all volumes of the candels
        final_volume = sum(volume)
        # Store the final prices in a tuple in the dictionary
        final_prices[interval] = (dates[0], times[0], final_open, final_high, final_low, final_close, final_volume)
    
    ws = []
    # Write the data rows
    for interval, final in final_prices.items():
        date, time, open_price, high_price, low_price, close_price, volume = final
        ws.append([date, time, interval, open_price, high_price, low_price, close_price, volume])
    return pd.DataFrame(ws,columns = ["Date", "Time", "date", "open", "high", "low", "close","volume"])
    

def handle_data(context,data):
    ### check on index n-1::
    ## Fetch n-1 candles volume candles:::
    #data = data.reset_index()
    
    ## exit prev conditions
    if context["position"] == True:
        if data["close"].iloc[-1]>=sum(context["priceLevels"])/2:
            prof = data["close"].iloc[-1] - context["buy"]
            context["profit"] += prof
            if prof<0:
                context["losses"] += 1   
            context["profitList"].append(context["profit"])
            context["position"]  = 0
            context["trades"] += 1
        elif data["close"].iloc[-1]<=context["stoploss"]:
            context["losses"] += 1
            context["position"] = 0
            context["profit"] += data["close"].iloc[-1] - context["buy"]
            context["profitList"].append(context["profit"])
            context["trades"] += 1
        if context["position"]==0:
            print("squaredOff",data["date"].iloc[-1])
        return
    #data_5min = to_intervals(data[['date',"open",'high',"low","close","volume"]].iloc[-5000:],5)
    
    candleToCheck = data["date"].iloc[-5]

    if not imbalance_from_volume(data,candleToCheck,context):
        return
#     print("imbalance Found in volume!!")
#     print(candleToCheck,"__________")
#     print(data_5min)
    p1,p2 = imbalance_zone(data, candleToCheck , 30) ##zone funciton....
#     print(p1,p2)
    if p1==p2:
        return
    
    if max(data["high"].iloc[-4:])>(p1):#-data["low"].iloc[-4:]
        return
    if data["close"].iloc[-1]>p1:
        return
    if (data["close"].iloc[-1]-data["open"].iloc[-1])<0:#p1*0.99:
        return
    ## apply price conditions 
    ## between previous 30 5 minute candles low, current candle high -- range of body of imbalance greater than threshold
    ## 5 min data
    
    context["priceLevels"] = [p1,p2]
   
    # strategy_trade(context,data_5min,candleToCheck) #TODO send volume data
    context["imbalanceCandles"].append(candleToCheck)
    next_candle_strategy_trade(context , data)

def buy(context,price):
    context["position"] = True
    context["buy"] = price
    context['stoploss'] = price - 0.002*price   # to be change 

def next_candle_strategy_trade( context , data):
    print("buy order",data["date"].iloc[-1])
    buy(context,data["close"].iloc[-1])


def strategy_trade(context,df,candleToCheck):
    data = df.iloc[-50:]
    data["mid"] = (data["high"]+data["low"])/2
    data["ao"] = data["mid"].rolling(window = 5).mean() - data["mid"].rolling(window = 34).mean()
    signals = data[(data["ao"].shift(4)< data["ao"].shift(3)) & (data["ao"].shift(3)< data["ao"].shift(2)) & (data["ao"].shift(2) > data["ao"])]
    if len(signal):
        ind = signal.index[-1]
        datetime_ = signal["datetime"].loc[ind]  #latest or not ==== send data only after signal
        # datetime.datetime.strptime(datetime_,"")>candleToCheck:

        #TODO 

        buy(context,data["open"].iloc[-1])
        
    #data[data["ao"].shift(3)< data["ao"].shift(2) and data["ao"].shift(2)< data["ao"].shift(1) and data["ao"].shift(1) > data["ao"]]

def plot(df3):
    
    # Create the candlestick chart
    candlestick = go.Candlestick(x=df3.index, open=df3['open'], close=df3['close'], high=df3['high'], low=df3['low'])

    # Add a line plot with secondary x-axis
    #line = go.Scatter(x=df3['date'], y=df3['close'], name='date', xaxis='x2')
    #line = go.Bar(x=df3.index, y=df3['volume'], name='Volume')

    # Create the figure with both the candlestick and line plots
    fig = go.Figure(data=[candlestick])

    # Update the layout to add a secondary x-axis
#     fig.update_layout(xaxis2=dict(title='volume', overlaying='x', side='top'),yaxis2 = dict(title='volume', overlaying='y', side='top'))
    fig.update_layout(xaxis_rangeslider_visible=False)

    # Show the chart
    fig.show()
    return
def plot_candlestick_with_volume(df3):
    candlestick = go.Candlestick(x=df3.index, open=df3['open'], close=df3['close'], high=df3['high'], low=df3['low'])

    # Add a line plot with secondary x-axis
    #line = go.Scatter(x=df3['date'], y=df3['close'], name='date', xaxis='x2')
    line = go.Bar(x=df3.index, y=df3['volume'], name='Volume')

    # Create the figure with both the candlestick and line plots
    fig = go.Figure(data=[candlestick,line])

    # Update the layout to add a secondary x-axis
    fig.update_layout(xaxis2=dict(title='volume', overlaying='x', side='top'),yaxis2 = dict(title='volume', overlaying='y', side='top'))
    fig.update_layout(xaxis_rangeslider_visible=False)

    # Show the chart
    fig.show()
    return

def filter_candles_at_index(df, index, body_threshold, untouched_threshold):
    # Calculate the body of the specified candle
    df['body'] = df['close'] - df['open']
    body = df.at[index, 'body']
    # Select only the specified candle if the body is high
    if abs(body) >= body_threshold:
        # Find the percentage of the price range covered by the body that has not been touched by the previous 10 candles
        df['body_min'] = df[['open', 'close']].min(axis=1)
        df['body_max'] = df[['open', 'close']].max(axis=1)
        df['prev_min'] = df['body_min'].shift(1).rolling(window=10).min()
        df['prev_max'] = df['body_max'].shift(1).rolling(window=10).max()
        df['price_range_untouched_min'] = df['body_min'].where(df['body_min'] > df['prev_max'], 0)
        df['price_range_untouched_max'] = df['body_max'].where(df['body_max'] < df['prev_min'], 0)
        df['price_range_untouched'] = df[['price_range_untouched_min', 'price_range_untouched_max']].max(axis=1) - df[['price_range_untouched_min', 'price_range_untouched_max']].min(axis=1)
        df['untouched_percentage'] = df['price_range_untouched'].abs() / df['body'].abs()
        # Select only the specified candle if the percentage is large
        if df.at[index, 'untouched_percentage'] >= untouched_threshold:
            return True
        else:
            return False
    else:
        return False

    
def filter_candles(df, body_threshold=10, untouched_threshold=20):
    
    # Calculate the body of each candle
    df['body'] = df['close'] - df['open']
    body_threshold = (body_threshold+1)*df["body"].mean()
    # Select only those candles where the body is high
    df = df[df['body'].abs() >= body_threshold]
    # Find the percentage of the price range covered by the body that has not been touched by the previous 10 candles
    df['body_min'] = df[['open', 'close']].min(axis=1)
    df['body_max'] = df[['open', 'close']].max(axis=1)
    df['prev_min'] = df['body_min'].shift(1).rolling(window=10).min()
    df['prev_max'] = df['body_max'].shift(1).rolling(window=10).max()
    df['price_range_untouched_min'] = df['body_min'].where(df['body_min'] > df['prev_max'], 0)
    df['price_range_untouched_max'] = df['body_max'].where(df['body_max'] < df['prev_min'], 0)
    df['price_range_untouched'] = df[['price_range_untouched_min', 'price_range_untouched_max']].max(axis=1) - df[['price_range_untouched_min', 'price_range_untouched_max']].min(axis=1)
    df['untouched_percentage'] = df['price_range_untouched'].abs() / df['body'].abs()
    # Select only those candles where the percentage is large
    df = df[df['untouched_percentage'] >= untouched_threshold]
    return df
print("adv")