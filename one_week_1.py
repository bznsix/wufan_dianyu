import requests
from datetime import datetime, timedelta

# 定义交易对和K线周期
symbol = "BTCUSDT"
interval = "1h"  # 假设你希望获取每小时的K线数据

# 计算一周前的时间
end_time = datetime.now()
start_time = end_time - timedelta(weeks=1)

# 将时间转换为Unix时间戳（毫秒）
start_time_ms = int(start_time.timestamp() * 1000)
end_time_ms = int(end_time.timestamp() * 1000)

# 获取一周内的K线数据
url = f"https://api.binance.com/api/v1/klines?symbol={symbol}&interval={interval}&startTime={start_time_ms}&endTime={end_time_ms}"
response = requests.get(url)
klines = response.json()

# 计数波动幅度大于1%的次数
count = 0

for kline in klines:
    open_price = float(kline[1])
    close_price = float(kline[4])
    change_percent = (close_price - open_price) / open_price * 100

    if abs(change_percent) > 1:
        count += 1

print(f"一周内波动幅度大于1%的次数: {count}")
