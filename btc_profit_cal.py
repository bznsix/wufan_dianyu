import requests
import time
from datetime import datetime, timedelta
import hmac
import hashlib
from prettytable import PrettyTable

# 填写你的API密钥和密钥秘钥
api_key = ''
api_secret = ''

# 获取服务器时间
def get_server_time():
    url = "https://fapi.binance.com/fapi/v1/time"
    response = requests.get(url)
    return response.json()['serverTime']

# 创建请求签名
def create_signature(query_string, secret):
    return hmac.new(secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

# 获取交易数据
def get_trades(symbol, start_time, end_time, api_key, api_secret):
    base_url = "https://fapi.binance.com"
    endpoint = "/fapi/v1/userTrades"
    params = {
        'symbol': symbol,
        'startTime': start_time,
        'endTime': end_time,
        'limit': 1000,
        'recvWindow': 60000,
        'timestamp': get_server_time()
    }

    query_string = '&'.join(["{}={}".format(k, params[k]) for k in params])
    signature = create_signature(query_string, api_secret)
    url = f"{base_url}{endpoint}?{query_string}&signature={signature}"
    
    headers = {
        'X-MBX-APIKEY': api_key
    }

    response = requests.get(url, headers=headers)
    # print(response.text)  # 打印响应文本来检查数据
    return response.json()

# 计算昨天的时间范围
yesterday_start = int((datetime.now() - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0).timestamp() * 1000)
yesterday_end = int((datetime.now() - timedelta(days=1)).replace(hour=23, minute=59, second=59, microsecond=999).timestamp() * 1000)

# 获取昨天的合约交易数据
trades = get_trades('BTCUSDT', yesterday_start, yesterday_end, api_key, api_secret)

# 初始化统计数据
buy_volume, sell_volume, profit_loss = 0, 0, 0

# 遍历交易数据
for trade in trades:
    qty = float(trade['qty'])
    price = float(trade['price'])
    realized_pnl = float(trade['realizedPnl'])  # 实现盈亏

    if trade['side'] == 'BUY':
        buy_volume += qty
    else:
        sell_volume += qty

    profit_loss += realized_pnl

# print("昨天的买入量:", buy_volume)
# print("昨天的卖出量:", sell_volume)
# print("昨天的盈亏:", profit_loss)

# 初始化表格
table = PrettyTable()
table.field_names = ["类型", "数量", "总价值"]

# 初始化统计数据
buy_volume, sell_volume, total_buy_value, total_sell_value = 0, 0, 0, 0

# 遍历交易数据并填充表格
for trade in trades:
    qty = float(trade['qty'])
    price = float(trade['price'])
    value = qty * price

    if trade['side'] == 'BUY':
        buy_volume += qty
        total_buy_value += value
        table.add_row(['买入', qty, value])
    else:
        sell_volume += qty
        total_sell_value += value
        table.add_row(['卖出', qty, value])

# 计算利润
profit_loss = total_sell_value - total_buy_value

# 在表格中添加总计行
table.add_row(['总买入', buy_volume, total_buy_value])
table.add_row(['总卖出', sell_volume, total_sell_value])

# 打印表格和利润
print(table)
print("总利润:", profit_loss)