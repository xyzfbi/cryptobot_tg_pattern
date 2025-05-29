from typing import List, Optional, Union

import pandas as pd
from pybit.unified_trading import HTTP

session = HTTP()


def get_available_coins() -> List[str]:
    response = session.get_instruments_info(category="spot")

    symbols = response["result"]["list"]
    coins = {symbol["baseCoin"] for symbol in symbols}

    return list(coins)


class CandlesData:
    def __init__(self, symbol: str = "BTCUSDT"):  # по дфеолту такой символ
        self.session = HTTP()
        self.symbol = symbol
        self.timeframes = {
            '15 minutes': 15,
            '1 hour': 60,
            '4 hours': 240,
            '1 day': 'D'
        }

    @staticmethod
    def normalize_df(df: pd.DataFrame) -> pd.DataFrame:
        df = df.apply(pd.to_numeric, errors="coerce")  # все в числа
        df["datetime"] = pd.to_datetime(df["datetime"],
                                        unit="ms")  # крч меняем юникс время в нормальное и свечи запрашиваются в обратном порядке те от ближайшего к нам до самого позднего

        return df

    def fetch_candles(self, interval: int, limit: int) -> pd.DataFrame:
        response = session.get_kline(
            category="spot",
            symbol=self.symbol,
            interval=str(interval),
            limit=limit
        )

        df = pd.DataFrame(
            response["result"]["list"],
            columns=[
                "datetime",
                "open",
                "high",
                "low",
                "close",
                "volume",  # это в биткоинах тут
                "quote_volume",  # это в usdt
            ]
        )
        return self.normalize_df(df)

    def get_pattern_indicators_data(self, candles_count: int = 50, timeframe: Union[int, str] = 15) -> pd.DataFrame:
        return self.fetch_candles(timeframe, candles_count)

    def get_trend_data(self, candles_count: int = 150, timeframe: Union[int, str] = 60) -> pd.DataFrame:
        return self.fetch_candles(timeframe, candles_count)

    def candles_csv(self, df: pd.DataFrame, timeframe: Union[str, int], df_name: str) -> str:
        filename = f"data/{self.symbol}_{df_name}_{timeframe}.csv"
        df.to_csv(filename, index=False)
        return filename


if __name__ == "__main__":  # точка входа
    smbl = input("Enter symbol: ")
    smbl = smbl.upper()

    data = CandlesData(smbl)
    for_pattern = data.get_pattern_indicators_data()

    for_trend = data.get_trend_data()
    print(for_trend)
    print(for_pattern)
    print(for_trend.head(10))
    data.candles_csv(for_pattern, df_name="for_pattern", timeframe="4h")

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
