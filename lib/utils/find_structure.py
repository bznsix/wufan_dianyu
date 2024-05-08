import numpy as np
import pandas as pd
from scipy.signal import argrelextrema
from collections import deque
# colors = ['red','black','red','green','purple']
# data = pd.read_csv('../data/test.csv')
# data = data[:500]
# # max_idx = argrelextrema(data['close'].values, np.greater, order=5)[0]
# # min_idx = argrelextrema(data['close'].values, np.less, order=5)[0]
# # plt.figure(figsize=(15, 8))
# # plt.plot(data['close'], zorder=0)
# # plt.scatter(data.iloc[max_idx].index, data.iloc[max_idx]['close'],
# #   label='Maxima', s=100, color=colors[1], marker='^')
# # plt.scatter(data.iloc[min_idx].index, data.iloc[min_idx]['close'],
# #   label='Minima', s=100, color=colors[2], marker='v')

# # plt.legend()
# # plt.savefig('./1.png')
# # plt.show()

# # from collections import deque
# # # Get K consecutive higher peaks
# # K = 2
# # high_idx = argrelextrema(data['close'].values, np.greater, order=5)[0]
# # highs = data.iloc[high_idx]['close']
# # extrema = []
# # ex_deque = deque(maxlen=K)
# # for i, idx in enumerate(high_idx):
# #     if i == 0:
# #         ex_deque.append(idx)
# #         continue
# #     if highs[high_idx[i]] < highs[high_idx[i-1]]:
# #         ex_deque.clear()

# #     ex_deque.append(idx)
# #     if len(ex_deque) == K:
# #     # K-consecutive higher highs found
# #         extrema.append(ex_deque.copy())

# # close = data['close'].values
# # dates = data.index

# # plt.figure(figsize=(15, 8))
# # plt.plot(data['close'])
# # _ = [plt.plot(dates[i], close[i], c=colors[1]) for i in extrema]
# # plt.xlabel('Date')
# # plt.ylabel('Price ($)')
# # plt.legend(['Close', 'Consecutive Highs'])
# # plt.savefig('./2.png')
class HHLL():
    def __init__(self) -> None:
        pass
    def getHigherLows(self,data: np.array, order=5, K=2):
        '''
        Finds consecutive higher lows in price pattern.
        Must not be exceeded within the number of periods indicated by the width
        parameter for the value to be confirmed.
        K determines how many consecutive lows need to be higher.
        '''
        # Get lows
        low_idx = argrelextrema(data, np.less, order=order)[0]
        lows = data[low_idx]
        # Ensure consecutive lows are higher than previous lows
        extrema = []
        ex_deque = deque(maxlen=K)
        for i, idx in enumerate(low_idx):
            if i == 0:
                ex_deque.append(idx)
                continue
            if lows[[i]] < lows[[i-1]]:
                ex_deque.clear()

            ex_deque.append(idx)
            if len(ex_deque) == K:
                extrema.append(ex_deque.copy())

        return extrema

    def getLowerHighs(self,data: np.array, order=5, K=2):
        '''
        Finds consecutive lower highs in price pattern.
        Must not be exceeded within the number of periods indicated by the width
        parameter for the value to be confirmed.
        K determines how many consecutive highs need to be lower.
        '''
        # Get highs
        high_idx = argrelextrema(data, np.greater, order=order)[0]
        highs = data[high_idx]
        # Ensure consecutive highs are lower than previous highs
        extrema = []
        ex_deque = deque(maxlen=K)
        for i, idx in enumerate(high_idx):
            if i == 0:
                ex_deque.append(idx)
                continue
            if highs[[i]] > highs[[i-1]]:
                ex_deque.clear()

            ex_deque.append(idx)
            if len(ex_deque) == K:
                extrema.append(ex_deque.copy())

        return extrema

    def getHigherHighs(self,data: np.array, order=5, K=2):
        '''
        Finds consecutive higher highs in price pattern.
        Must not be exceeded within the number of periods indicated by the width
        parameter for the value to be confirmed.
        K determines how many consecutive highs need to be higher.
        '''
        # Get highs
        high_idx = argrelextrema(data, np.greater, order=5)[0]
        highs = data[high_idx]
        # Ensure consecutive highs are higher than previous highs
        extrema = []
        ex_deque = deque(maxlen=K)
        for i, idx in enumerate(high_idx):
            if i == 0:
                ex_deque.append(idx)
                continue
            if highs[[i]] < highs[[i-1]]:
                ex_deque.clear()

            ex_deque.append(idx)
            if len(ex_deque) == K:
                extrema.append(ex_deque.copy())

        return extrema

    def getLowerLows(self,data: np.array, order=5, K=2):
        '''
        Finds consecutive lower lows in price pattern.
        Must not be exceeded within the number of periods indicated by the width
        parameter for the value to be confirmed.
        K determines how many consecutive lows need to be lower.
        '''
        # Get lows
        low_idx = argrelextrema(data, np.less, order=order)[0]
        lows = data[low_idx]
        # Ensure consecutive lows are lower than previous lows
        extrema = []
        ex_deque = deque(maxlen=K)
        for i, idx in enumerate(low_idx):
            if i == 0:
                ex_deque.append(idx)
                continue
            if lows[[i]] > lows[[i-1]]:
                ex_deque.clear()

            ex_deque.append(idx)
            if len(ex_deque) == K:
                extrema.append(ex_deque.copy())

        return extrema

    def getEqualLows(self,data: np.array, order=5, K=2):
        '''
        Finds consecutive lower lows in price pattern.
        Must not be exceeded within the number of periods indicated by the width
        parameter for the value to be confirmed.
        K determines how many consecutive lows need to be lower.
        '''
        # Get lows
        low_idx = argrelextrema(data, np.less, order=order)[0]
        lows = data[low_idx]
        # Ensure consecutive lows are lower than previous lows
        extrema = []
        ex_deque = deque(maxlen=K)
        for i, idx in enumerate(low_idx):
            if i == 0:
                ex_deque.append(idx)
                continue

            max_lows = max(lows[i],lows[i-1])
            min_lows = min(lows[i],lows[i-1])
            if (max_lows - min_lows) > 0.005 * max_lows :
                ex_deque.clear()

            ex_deque.append(idx)
            if len(ex_deque) == K:
                extrema.append(ex_deque.copy())

        return extrema

    def getEqualHighs(self,data: np.array, order=5, K=2):
        '''
        Finds consecutive lower lows in price pattern.
        Must not be exceeded within the number of periods indicated by the width
        parameter for the value to be confirmed.
        K determines how many consecutive lows need to be lower.
        '''
        # Get lows
        low_idx = argrelextrema(data, np.greater, order=order)[0]
        lows = data[low_idx]
        # Ensure consecutive lows are lower than previous lows
        extrema = []
        ex_deque = deque(maxlen=K)
        for i, idx in enumerate(low_idx):
            if i == 0:
                ex_deque.append(idx)
                continue

            max_lows = max(lows[i],lows[i-1])
            min_lows = min(lows[i],lows[i-1])
            if (max_lows - min_lows) > 0.005 * max_lows :
                ex_deque.clear()

            ex_deque.append(idx)
            if len(ex_deque) == K:
                extrema.append(ex_deque.copy())

        return extrema



# from matplotlib.lines import Line2D

# close = data['close'].values
# dates = data.index

# order = 5
# K = 2

# hh = getHigherHighs(close, order, K)
# hl = getHigherLows(close, order, K)
# # ll = getEqualLows(close, order, K)
# ll = getLowerLows(close, order, K)
# lh = getLowerHighs(close, order, K)

# plt.figure(figsize=(15, 8))
# plt.plot(data['close'])

# equal_low = []
# for i in ll :
#   equal_low.append(i[0])
#   equal_low.append(i[1])
#   equal_low = list(dict.fromkeys(equal_low))
# for i in hl :
#   equal_low.append(i[0])
#   equal_low.append(i[1])
#   equal_low = list(dict.fromkeys(equal_low))
# for i in hh :
#   equal_low.append(i[0])
#   equal_low.append(i[1])
#   equal_low = list(dict.fromkeys(equal_low))
# for i in lh :
#   equal_low.append(i[0])
#   equal_low.append(i[1])
#   equal_low = list(dict.fromkeys(equal_low))

# data_equal_low = close[equal_low]
# bull_ob = []
# bear_ob = []
# for i, idx in enumerate(equal_low):
#   if i != 0:
#     #上升趋势，寻找I点附近的下跌的值
#     if close[equal_low[i]] > close[equal_low[i-1]]:
#       print('看涨OB')
#       print(data.iloc[equal_low[i]]['open_time'])
#       bull_ob.append(i-1)
#     #下降趋势，寻找I点附近的上涨的值
#     if close[equal_low[i]] < close[equal_low[i-1]]:
#       print('看跌OB')
#       print(data.iloc[equal_low[i]]['open_time'])
#       bear_ob.append(i-1)

# print(f'看涨OB：{bull_ob}')
# print(f'看跌OB：{bear_ob}')

# close_bull_ob = close[bull_ob]
# close_bear_ob = close[bear_ob]
# #s 表示散点的大小，形如 shape (n, )
# #label 表示显示在图例中的标注
# #alpha 是 RGBA 颜色的透明分量
# #edgecolors 指定三点圆周的颜色
# plt.scatter(equal_low,data_equal_low,c=colors[3],label=colors[2],alpha=0.6,edgecolors='white')

# plt.xlabel('Date')
# plt.ylabel('Price ($)')
# # plt.ylim(0, close.max())
# ticker = 'btc'
# plt.title(f'Potential Divergence Points for {ticker} Closing Price')
# plt.show()
# plt.savefig('./3.png')