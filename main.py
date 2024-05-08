from broker import BROKER
from cerbo import Cerbo
from martin_long import MyStrategy
import sys
import pandas as pd
import time
import datetime
import sys
from pprint import pprint
symbol = 'BTCUSDT'

broker = BROKER(symbol)
long = MyStrategy(symbol)
# 创建一个Cerbo对象并传入strategy对象
cerbo_long = Cerbo(long)
trend = 1 #多头趋势
while True:
    try:
        if trend is not None:
            cerbo_long.update(trend)
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(3)
            
        
        
