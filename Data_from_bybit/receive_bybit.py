import pandas as pd
from pybit.unified_trading import HTTP

session = HTTP()

# запрос данных за ласт 24 часа с интервалом в час крч
symbol = "BTCUSDT"
timeframe = "60"  # 60 минут = 1 час
limit = 24       # 24 свечи

response = session.get_kline(
    category="spot",  # или "linear" - usdt -фьючи, "inverse" - обратные фьючи
    symbol=symbol, # пара торговли
    interval=timeframe, # нутут все понятнл
    limit=limit # количество свеч
    # start = ... # эт короче временной интервал запроса данных
    # end = ... # ну эт конец понятно вроже
)
crypto_df = pd.DataFrame(
    response["result"]["list"],
    columns=[
        "datetime",
        "open",
        "high",
        "low",
        "close",
        "volume", # это в биткоинах тут
        "quote_volume", # это в usdt

    ]
)

crypto_df = crypto_df.apply(pd.to_numeric, errors="coerce") # все в числа
crypto_df["datetime"] = pd.to_datetime(crypto_df["datetime"], unit="ms") # крч меняем юникс время в нормальное и свечи запрашиваются в обратном порядке те от ближайшего к нам до самого позднего
crypto_df["quote_volume"] = crypto_df["quote_volume"].apply(lambda x: f"{x/1e6:.2f}M") # ВЫВОД В МИЛЛИОНАХ А НЕ В ТУПОЙ EXP ** форме
# резы от апи в этих крч массивах
'''
print(f"Данные для {symbol} (таймфрейм: {timeframe} минут):")
for candle in response["result"]["list"]:
    print(candle)
    '''

# вывод датафрейма с криптой хз как настроить
print(crypto_df)
'''
Содержание свечи

[
    "1743544800000",      # 0: Время открытия (UNIX timestamp)
    "85217.7",         # 1: Цена открытия
    "85241.2",         # 2: Максимальная цена
    "85217.7",         # 3: Минимальная цена
    "85227.8",         # 4: Цена закрытия
    "0.835161",    # 5: Объём в btc
    "71177.7285573",      # 7: Объём в котировочной валюте

]'''