import backtrader as bt
import backtrader.indicators as btind
import pandas as pd
import pdb
class MyStrategy(bt.Strategy):
    params = (
        ('margin', 10), #杠杆倍数
        ('gap_time', 10), #分成多少份
        ('kline_interval',60*(60*1000)), #多少分钟
        ('long_win_ratio',0.01) #止盈比例
    )

    def __init__(self):
        self.broker.setcommission(commission=1/10000)
        
        self.start_cash = 0 #起始总资金
        self.now_gap = 0 #现在已经用了多少份
        self.long_order = {} #所有的多单{'gap_time':order}
        self.long_stop_order = {} #最新的止盈单
        self.dead_order = 0 #最新的止损订单
        self.last_can_buy = 0 #最新一次可以购买的时间
        self.last_buy_price = [99999] #最后一次购买的价格列表
        self.waitting_for_open = 0 #等待第一次挂单成交
        self.waitting_to_buy_order = []
        self.waitting_to_sell_order = []
        
    def next(self):
        close = self.data.lines.close[0]
        #获取当前持仓
        position = self.broker.getposition(self.data).size
        cash = self.broker.get_cash()
        
        # 获取当前的日期时间
        current_datetime = self.data.datetime.datetime()
        # 将日期时间转换为毫秒级别的时间戳
        timestamp_ms = int(current_datetime.timestamp() * 1000)
        
        # print(f'{current_datetime},现金{cash},仓位{position}')
        if  position < 0.0001 and self.waitting_for_open == 0: #这里可能没有仓位
            self.one_piece_money = cash / self.params.gap_time
            size = self.one_piece_money / close
            order = self.buy(price=close,size=size)
            self.waitting_for_open = 1
            self.last_can_buy = timestamp_ms + self.params.kline_interval
            print(f'开仓,价格{close},总现金{cash},当前时间{current_datetime}')
            # 更新下总现金
            self.waitting_to_buy_order.append(order)
        
        if  self.now_gap < self.params.gap_time and close < min(self.last_buy_price) * (1-self.params.long_win_ratio) and timestamp_ms > self.last_can_buy:
            size = self.one_piece_money / close
            self.buy(price=close,size=size)
            self.last_can_buy = timestamp_ms + self.params.kline_interval
            print(f'加仓，价格{close},头寸{size},当前时间{current_datetime}')
        
        # need_to_del = []
        # for order in self.waitting_to_buy_order:
        #     if order.status == order.Completed:
        #         if close > order.executed.price*(1+self.params.long_win_ratio):
        #             print(f'检测卖单{close},{order.executed.price}')
        #             print(f'{order.ref}完成')
        #             # 设置卖单
        #             self.sell(size=abs(order.executed.size))
        #             need_to_del.append(order)

        # for order in need_to_del:
        #     self.waitting_to_buy_order.remove(order)
        
                
    def notify_order(self, order):
        order_status = ['Created','Submitted','Accepted','Partial',
                        'Completed','Canceled','Expired','Margin','Rejected']
        # # 未被处理的订单
        # if order.status in [order.Submitted, order.Accepted]:
        #     print('ref:%.0f, name: %s, Order: %s'% (order.ref,
        #                                            order.data._name,
        #                                            order_status[order.status]))
        #     print(order.price)
        #     return
        if order.status in [order.Partial, order.Completed]:
            if order.isbuy():
                self.now_gap += 1
                self.waitting_for_open = 0
                # 设置卖单
                price = order.executed.price*(1+self.params.long_win_ratio)
                self.last_buy_price.append(order.executed.price)
                # print(
                #         'BUY EXECUTED, status: %s, ref:%.0f, name: %s, Size: %.2f, Price: %.2f, Cost: %.2f, Comm %.2f' %
                #         (order_status[order.status], # 订单状态
                #          order.ref, # 订单编号
                #          order.data._name, # 股票名称
                #          order.executed.size, # 成交量
                #          order.executed.price, # 成交价
                #          order.executed.value, # 成交额
                #          order.executed.comm)) # 佣金
                # print(f'买单成交，价格{self.last_buy_price},当前次数{self.now_gap}，设置卖单价{price}')
                self.sell(exectype=bt.Order.Limit,price = price,size=abs(order.executed.size))
            elif order.issell():
                self.now_gap -= 1
                self.last_can_buy -= self.params.kline_interval
                order_executed_time = self.data.num2date(order.executed.dt)
                self.last_buy_price.remove(min(self.last_buy_price))
                print(f'卖出,价格{order.executed.price},时间{order_executed_time}')
                print(f'更新,上次购买价格{self.last_buy_price},')
                # print('SELL EXECUTED, status: %s, ref:%.0f, name: %s, Size: %.2f, Price: %.2f, Cost: %.2f, Comm %.2f' %
                #             (order_status[order.status],
                #              order.ref,
                #              order.data._name,
                #              order.executed.size,
                #              order.executed.price,
                #              order.executed.value,
                #              order.executed.comm))
        # elif order.status in [order.Canceled, order.Margin, order.Rejected, order.Expired]:
        #     # 订单未完成
        #     print('ref:%.0f, name: %s, status: %s'% (
        #         order.ref, order.data._name, order_status[order.status]))
        #     print(order.price)


    def stop(self):
        print('---------stop----------')
        print(bt.num2date(self.data.datetime[-1]).isoformat())
        print('self.stats 当前可用资金', self.stats.broker.cash[0])
        print('self.stats 当前总资产', self.stats.broker.value[0])
        print('self.stats 最大回撤', self.stats.drawdown.drawdown[0])