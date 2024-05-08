import ccxt
import talib
import pandas as pd
import talib, time
from scipy import signal
import numpy as np
from utils.find_structure import HHLL
from datetime import datetime, timezone, timedelta
from pprint import pprint
structure = HHLL()
binance = ccxt.binance()
class WICKKY():
    def __init__(self,apikey='',secert=''):
        self.file_path = ''
        self.log = None
        binance.apiKey = apikey
        binance.secret = secert
        binance.timeout = 20000

    def getKlines(self, symbol, timeframe='1h',isPerp=False,start_time = None,end_time = None,limit=1000):
        '''
        -  传参starttime,endtime 毫秒级时间戳
        -  0 ： 秒(s)精度的 Unix 时间戳
        -  1 ： 开盘
        -  2 ： 最高
        -  3 ： 最低
        -  4 ： 收盘
        -  5 ： 交易量
        '''
        if isPerp == False:
            data = binance.fetchOHLCV(symbol=symbol,
                                      timeframe=timeframe,
                                      limit=limit)
            return data
        else:
            new_list = []
            if start_time == None and end_time == None:
                params = {
                    "pair" : symbol,
                    "contractType" : 'PERPETUAL',
                    "interval" : timeframe ,
                    "limit" : limit
                }
                r = binance.fapiPublicGetContinuousKlines(params)
                for data in r:
                    new_data = data[:6]
                    new_data[0] = data[0]
                    new_data[1] = float(data[1])
                    new_data[2] = float(data[2])
                    new_data[3] = float(data[3])
                    new_data[4] = float(data[4])
                    new_data[5] = float(data[5])
                    new_list.append(new_data)
                return new_list
            else:
                # start_time = int(datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S').timestamp() * 1000)
                # end_time = int(datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S').timestamp() * 1000)
                last_get = 0
                while True:
                    params = {
                        "pair" : symbol,
                        "contractType" : 'PERPETUAL',
                        "interval" : timeframe ,
                        "limit" : 500
                    }
                    params['startTime'] = start_time
                    r = binance.fapiPublicGetContinuousKlines(params)
                    if r[-1][0] == last_get: #已经下架的交易对，一直都是同一组数据
                        return new_list
                    for data in r:
                        new_data = data[:6]
                        new_data[0] = data[0]
                        new_data[1] = float(data[1])
                        new_data[2] = float(data[2])
                        new_data[3] = float(data[3])
                        new_data[4] = float(data[4])
                        new_data[5] = float(data[5])
                        new_list.append(new_data)
                    last_get = r[-1][0]
                    if (int(r[-1][0]) > end_time) or int(r[-1][6]) >= (int(time.time() * 1000) - 60 * 1000):
                        return new_list
                    start_time = r[-1][0]

    def getAggTrades(self,symbol,start_time = None,end_time = None,limit=1000):
        '''
        -  传参starttime,endtime 毫秒级时间戳
        -  0 ： 秒(s)精度的 Unix 时间戳
        -  1 ： 开盘
        -  2 ： 最高
        -  3 ： 最低
        -  4 ： 收盘
        -  5 ： 交易量
        '''

        df = None
        # 将字符串转换为 datetime 对象，并设置时区为北京时间
        beijing_timezone = timezone(timedelta(hours=8))
        start_time_dt = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S').replace(tzinfo=beijing_timezone)
        end_time_dt = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S').replace(tzinfo=beijing_timezone)

        # 转换为毫秒级时间戳
        start_time = int(start_time_dt.timestamp() * 1000)
        end_time = int(end_time_dt.timestamp() * 1000)

        last_get = 0
        while True:
            params = {
                "symbol" : symbol,
                "limit" : 1000
            }
            params['startTime'] = start_time
            print(params)
            r = binance.fapiPublicGetAggTrades(params)
            df_new = pd.DataFrame(r)
            if df_new.iloc[-1]['T'] == last_get: #已经下架的交易对，一直都是同一组数据
                return pd.DataFrame(r)
            df = pd.concat([df, df_new], ignore_index=True)
            print(df)
            if (int(df.iloc[-1]['T']) > end_time) or int(df.iloc[-1]['T']) >= (int(time.time() * 1000) - 60 * 1000):
                return df
            start_time = df.iloc[-1]['T']
            print(f'更新start_time{start_time}')


    def getEMA(self, data,with_data=True):
        df = pd.DataFrame(data,
                          columns={
                              'open_time': 0,
                              'open': 1,
                              'high': 2,
                              'low': 3,
                              'close': 4,
                              'volume': 5
                          })
        df['open_time'] = pd.to_datetime(df['open_time'],
                                         unit='ms') + pd.Timedelta(hours=8)
        if with_data == True:
            df['ema'] = talib.EMA(df['close'], timeperiod=7)
            df['ema144'] = talib.EMA(df['close'], timeperiod=144)
            df['ema169'] = talib.EMA(df['close'], timeperiod=169)
            df['ema288'] = talib.EMA(df['close'], timeperiod=288)
            df['ema338'] = talib.EMA(df['close'], timeperiod=338)
            df['atr'] = talib.ATR(df['high'],
                                  df['low'],
                                  df['close'],
                                  timeperiod=14)
            df['kama'] = talib.KAMA(df['close'], timeperiod=21)
            df['rsi'] = talib.RSI(df['close'],timeperiod = 14)
            df['dc_up'] = talib.MAX(df['high'], 10)
            df['dc_down'] = talib.MIN(df['low'], 10)
            # df.to_csv(self.file_path)
        return df

    def get_global_account_ratio(self, symbol, period, limit=2):
        symbol = symbol
        r = binance.fapiDataGetGlobalLongShortAccountRatio({
            "symbol": symbol,
            "period": period,
            'limit': limit
        })
        longShortRatio = []
        timestamp = []
        for frame in r:
            longShortRatio.append(float(frame['longShortRatio']))
            timestamp.append(frame['timestamp'])
        r_dict = {'open_time': timestamp, 'longShortRatio': longShortRatio}
        df = pd.DataFrame(r_dict)
        df['open_time'] = pd.to_datetime(df['open_time'],
                                         unit='ms') + pd.Timedelta(hours=8)
        return df

    def get_u_position(self, symbol, period, limit=10):
        r = binance.fapiDataGetOpenInterestHist({
            "symbol": symbol,
            "period": period,
            'limit': limit
        })
        sumOpenInterest = []
        sumOpenInterestValue = []
        open_time = []
        for frame in r:
            sumOpenInterest.append(float(frame['sumOpenInterest']))
            sumOpenInterestValue.append(float(frame['sumOpenInterestValue']))
            open_time.append(frame['timestamp'])
        r_dict = {
            'open_time': open_time,
            'sumOpenInterest': sumOpenInterest,
            'sumOpenInterestValue': sumOpenInterestValue
        }
        df = pd.DataFrame(r_dict)
        df['open_time'] = pd.to_datetime(df['open_time'],
                                         unit='ms') + pd.Timedelta(hours=8)
        return df

    def get_u_taker(self, symbol, period, limit=500):
        symbol = symbol
        r = binance.fapiDataGetTakerlongshortratio({
            "symbol": symbol,
            "period": period,
            'limit': limit
        })
        buySellRatio = []
        buyVol = []
        sellVol = []
        timestamp = []
        for frame in r:
            buySellRatio.append(float(frame['buySellRatio']))
            buyVol.append(float(frame['buyVol']))
            sellVol.append(float(frame['sellVol']))
            timestamp.append(frame['timestamp'])
        r_dict = {
            'open_time': timestamp,
            'buySellRatio': buySellRatio,
            'buyVol': buyVol,
            'sellVol': sellVol,
        }
        df = pd.DataFrame(r_dict)
        df['open_time'] = pd.to_datetime(df['open_time'],
                                         unit='ms') + pd.Timedelta(hours=8)
        # df.index = df['open_time']
        # df.drop(columns=['open_time'], inplace=True)
        return df

    def get_u_long_short_account(self, symbol, period,start_time=0,end_time=0,limit=2):
        '''返回大户持仓多空比'''
        if start_time == 0:
            r = binance.fapiDataGetToplongshortaccountratio({
                "symbol": symbol,
                "period": period,
                'limit': limit,
            })
            longShortRatio = []
            timestamp = []
            for frame in r:
                longShortRatio.append(float(frame['longShortRatio']))
                timestamp.append(frame['timestamp'])
            r_dict = {'timeStamp': timestamp, 'longShortRatio': longShortRatio}
            df = pd.DataFrame(r_dict)
            df['timeStamp'] = pd.to_datetime(df['timeStamp'],
                                             unit='ms') + pd.Timedelta(hours=8)
            # df.index = df['timeStamp']
            # df.drop(columns=['timeStamp'], inplace=True)
            return df
        else:
            longShortRatio = []
            timestamp = []
            while True:
                break_flag = 0
                params = {
                    "symbol": symbol,
                    "period": period,
                    'limit': 500
                }
                params['startTime'] = start_time
                print(start_time)
                r = binance.fapiDataGetToplongshortaccountratio(params)
                for frame in r:
                    longShortRatio.append(float(frame['longShortRatio']))
                    timestamp.append(frame['timestamp'])
                    # time.sleep(1)
                    if end_time == 0 : end_time = 9999999999999 #没有传endtime的情况，最大值
                    if (int(timestamp[-1]) > end_time) or int(timestamp[-1]) >= (int(time.time() * 1000) - 5 * 60 * 1000): #时间刻度最小是5m
                        break_flag = 1
                if break_flag == 1:
                    break
            r_dict = {'timeStamp': timestamp, 'longShortRatio': longShortRatio}
            df = pd.DataFrame(r_dict)
            df['timeStamp'] = pd.to_datetime(df['timeStamp'],
                                             unit='ms') + pd.Timedelta(hours=8)
            df.index = df['timeStamp']
            df.drop(columns=['timeStamp'], inplace=True)
            return df

    def get_b_position(self, symbol, period, limit=10):
        symbol = symbol + 'USD'
        contractType = 'ALL'
        r = binance.dapiDataGetOpenInterestHist({
            "pair": symbol,
            "period": period,
            'limit': limit,
            'contractType': contractType
        })
        sumOpenInterest = []
        sumOpenInterestValue = []
        timestamp = []
        for frame in r:
            sumOpenInterest.append(float(frame['sumOpenInterest']))
            sumOpenInterestValue.append(float(frame['sumOpenInterestValue']))
            timestamp.append(frame['timestamp'])
        r_dict = {
            'timeStamp': timestamp,
            'sumOpenInterest': sumOpenInterest,
            'sumOpenInterestValue': sumOpenInterestValue
        }
        df = pd.DataFrame(r_dict, index=timestamp)
        df.drop(columns=['timeStamp'], inplace=True)
        return df

    def return_futuremarket_coins(self):
        r = binance.fapiPublicGetExchangeInfo({})
        symbols = r['symbols']
        coin_list = []
        for data in symbols:
            trade_symbol = data['symbol']
            coin_list.append(trade_symbol)
        return coin_list

    def return_future_fundingrates(self):
        r = binance.fapiPublicGetPremiumIndex({})
        whole_list = []
        for pair in r:
            symbol = pair['symbol']
            fundingrate = float(pair['lastFundingRate'])
            whole_list.append((symbol,fundingrate))
            timestamp = pair['time']
        return (timestamp,whole_list)

    def return_history_fundingrates(self,symbol,limit):
        r = binance.fapiPublicGetFundingRate({
            "symbol": symbol,
            'limit': limit,
        })
        fundingrate = []
        timestamp = []
        for frame in r:
            fundingrate.append(float(frame['fundingRate']))
            timestamp.append(frame['fundingTime'])
        r_dict = {
            'timeStamp': timestamp,
            'fundingrate': fundingrate
        }
        df = pd.DataFrame(r_dict)
        df['timeStamp'] = pd.to_datetime(df['timeStamp'],
                                         unit='ms') + pd.Timedelta(hours=8)
        df.index = df['timeStamp']
        df.drop(columns=['timeStamp'], inplace=True)
        return df

    def get_u_global_long_short_position(self, symbol, period, limit=2):
        symbol = symbol
        r = binance.fapiDataGetToplongshortpositionratio({
            "symbol": symbol,
            "period": period,
            'limit': limit
        })
        longShortRatio = []
        timestamp = []
        for frame in r:
            longShortRatio.append(float(frame['longShortRatio']))
            timestamp.append(frame['timestamp'])
        r_dict = {'timeStamp': timestamp, 'longShortRatio': longShortRatio}
        df = pd.DataFrame(r_dict)
        df['timeStamp'] = pd.to_datetime(df['timeStamp'],
                                         unit='ms') + pd.Timedelta(hours=8)
        df.index = df['timeStamp']
        df.drop(columns=['timeStamp'], inplace=True)
        return df

    def print_exchangeinfo(self):
        r = binance.fapiPublicGetExchangeInfo({})
        print(r['rateLimits'])
    def find_top_coins(self,numbers,timeframe='1h'):
        r = binance.fapiPublicGetTicker24hr({})
        symbol_dict = {}
        for data in r:
            symbol = data['symbol']
            try:
                data = self.getKlines(symbol,timeframe,isPerp=True,limit=2)
                orign_data = self.getEMA(data)
                precent = (orign_data.iloc[-1]['close'] - orign_data.iloc[-1]['open']) / orign_data.iloc[-1]['open']
                symbol_dict[symbol] = precent
            except:
                pass
        sorted_items = sorted(symbol_dict.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_items[:numbers])
    def find_wrost_coins(self,numbers,timeframe='1h'):
        r = binance.fapiPublicGetTicker24hr({})
        symbol_dict = {}
        for data in r:
            symbol = data['symbol']
            try:
                data = self.getKlines(symbol,timeframe,isPerp=True,limit=2)
                orign_data = self.getEMA(data)
                precent = (orign_data.iloc[-1]['close'] - orign_data.iloc[-1]['open']) / orign_data.iloc[-1]['open']
                symbol_dict[symbol] = precent
            except:
                pass
        sorted_items = sorted(symbol_dict.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_items[-numbers:])
    def find_coins(self,timeframe='1h'):
        r = binance.fapiPublicGetTicker24hr({})
        symbol_dict = {}
        for data in r:
            symbol = data['symbol']
            try:
                data = self.getKlines(symbol,timeframe,isPerp=True,limit=2)
                orign_data = self.getEMA(data)
                precent = (orign_data.iloc[-1]['close'] - orign_data.iloc[-1]['open']) / orign_data.iloc[-1]['open']
                symbol_dict[symbol] = precent
            except:
                pass
        sorted_items = sorted(symbol_dict.items(), key=lambda x: x[1], reverse=True)
        return (sorted_items)

    def find_coins_up_0(self):
        r = binance.fapiPublicGetTicker24hr({})
        symbol_dict = {}
        for data in r:
            symbol = data['symbol']
            try:
                data = self.getKlines(symbol,timeframe='4h',isPerp=True,limit=6)
                df = self.getEMA(data)
                # 提取时间部分
                df['open_time'] = df['open_time'].dt.time
                # 选择 opentime 为 00:00:00 的行
                o = df[df['open_time'] == pd.to_datetime('00:00:00').time()]
                o = o.iloc[-1]['open']
                c = df.iloc[-1]['close']
                precent = (c - o) / o
                symbol_dict[symbol] = precent
            except Exception as e:
                print(e)

        sorted_items = sorted(symbol_dict.items(), key=lambda x: x[1], reverse=True)
        return (sorted_items)

    def equal_low_liq(self,data,threshold):
        '''
        传入dataframe,允许最低点之间偏离的阈值
        返回 最近五个等低点的id,5个等低点的平均价格,区间内是否存在sfp
        '''
        newdata = data
        low = newdata['low'].values
        open_time = data['open_time']
        equal_l = structure.getEqualLows(low)
        if len(equal_l) == 0:
            return None
        latest = equal_l[-1]
        first = data.iloc[latest[0]]['open_time']
        second = data.iloc[latest[1]]['open_time']
        first_value = data.iloc[latest[0]]['low']
        second_value = data.iloc[latest[1]]['low']
        threshold = (first_value - second_value)/first_value
        equal_low_index = [first,second]
        return(equal_low_index)

    def equal_high_liq(self,data,threshold):
        '''
        传入dataframe,允许最低点之间偏离的阈值
        返回 最近五个等低点的id,5个等低点的平均价格,区间内是否存在sfp
        '''
        # newdata = data[-500:]
        newdata = data
        low = newdata['high'].values
        # print(low)
        open_time = data['open_time']
        equal_l = structure.getEqualHighs(low)
        if len(equal_l) == 0:
            return None
        latest = equal_l[-1]
        first = data.iloc[latest[0]]['open_time']
        second = data.iloc[latest[1]]['open_time']
        first_value = data.iloc[latest[0]]['low']
        second_value = data.iloc[latest[1]]['low']
        threshold = (first_value - second_value)/first_value
        equal_low_index = [first,second]
        return(equal_low_index)



    def ifNeedle(self, open, high, low, close):
        if open >= close:
            #阴线
            if (high - open) > 3 * (open - close) or (
                    close - low) > 3 * (open - close):
                return True
        else:
            #阳线
            if (high - close) > 3 * (close - open) or (
                    open - low) > 3 * (close - open):
                return True

    def cal_trendcy(self,data,row):
        if data.iloc[row]['close'] >= data.iloc[row]['open']:
            return True
        else :
            return False

    def zz_god(self,data_1min,data_5min):
        tre_5_min_1 = self.cal_trendcy(data_5min, -4)
        tre_5_min_2 = self.cal_trendcy(data_5min, -3)
        tre_5_min_3 = self.cal_trendcy(data_5min, -2)

        # tre_1_min_1 = self.cal_trendcy(data_1min, -4)
        # tre_1_min_2 = self.cal_trendcy(data_1min, -3)
        # tre_1_min_3 = self.cal_trendcy(data_1min, -2)
        if tre_5_min_1 == True and tre_5_min_2 == False and tre_5_min_3 == False :
            open_time = data_5min.iloc[-2]['open_time']
            index = data_1min[data_1min.open_time == open_time].index.tolist()[0]
            tre_1_min_1 = self.cal_trendcy(data_1min, index+2)
            tre_1_min_2 = self.cal_trendcy(data_1min, index+3)
            tre_1_min_3 = self.cal_trendcy(data_1min, index+4)
            if tre_1_min_1 == True and tre_1_min_2 == False and tre_1_min_3 == False :
                return True

    def ifcrosstunnel(self,data,care_needle =False,row = -2):
        raw = data.iloc[row]
        ema144 = float(raw['ema144'])
        ema169 = float(raw['ema169'])
        ema288 = float(raw['ema288'])
        ema338 = float(raw['ema338'])
        open = float(raw['open'])
        high = float(raw['high'])
        low = float(raw['low'])
        close = float(raw['close'])
        rsi = float(raw['rsi'])
        atr = float(raw['ATR_21'])
        open_time = raw['open_time']
        #我们允许在隧道之间进行一个ATR的波动
        tunnel1_max = max(ema144,ema169) + atr
        tunnel1_min = min(ema144,ema169) - atr
        tunnel2_max = max(ema288,ema338) + atr
        tunnel2_min = min(ema288,ema338) - atr
        # 判断是不是上穿隧道
        if (low < tunnel1_max and high > tunnel1_min) or (low < tunnel2_max and high > tunnel2_min):
            #判断是不是针形态
            if care_needle == True:
                if(self.ifNeedle(open, high, low, close) == True):
                    return True
            else :
                return True

    def coin_list(self, markets):
        coin = []
        r = markets.keys()
        for i in r:
            if (i.find('USDT') == -1):
                pass
            else:
                coin.append(i)
        return coin

    def return_coinlist(self):
        binance_markets = binance.load_markets()
        binacne_coin = []
        binacne_coin = self.coin_list(binance_markets)
        return binacne_coin

    def market_price_ask(self, symbol):
        #返回买方要的最低价格
        data = binance.fetchTicker(symbol)
        print(f'market_price_ask{data}')
        return data['ask']

    def high_raid_kline(self,o,h,l,c):
        '''
        寻找上影线长的K线，输入OHLC，返回序列flag
        '''
        length = len(o)
        flag_list = []
        for i in range(0,length):
            open  = o[i]
            high  = h[i]
            low   = l[i]
            close = c[i]
            #上影线长度
            up_shaow = high - max(close,open)
            #实体长度
            body  = abs(close - open)
            #下影线长度
            down_shaow = abs(low - min(open,close))
            #上影线大于两倍的实体，并且上影线大于下影线
            if up_shaow >= 2 *  body and up_shaow > down_shaow:
                flag_list.append(1)
            else:
                flag_list.append(0)
        return pd.Series(flag_list)

    def low_raid_kline(self,o,h,l,c):
        '''
        寻找上影线长的K线，输入OHLC，返回序列flag
        '''
        length = len(o)
        flag_list = []
        for i in range(0,length):
            open  = o[i]
            high  = h[i]
            low   = l[i]
            close = c[i]
            #上影线长度
            up_shaow = high - max(close,open)
            #实体长度
            body  = abs(close - open)
            #下影线长度
            down_shaow = abs(low - min(open,close))
            #下影线大于两倍的实体，并且下影线大于上影线
            if down_shaow >= 2 *  body and up_shaow < down_shaow:
                flag_list.append(1)
            else:
                flag_list.append(0)
        return pd.Series(flag_list)


