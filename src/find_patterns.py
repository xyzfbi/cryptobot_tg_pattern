import pandas as pd
import talib

from src.patterns_config import candle_rankings, candlestick_patterns
from src.receive_bybit import CandlesData

"""
пары таймфреймов и свечи
    1. m1 = 75 150/2
    1. M5 = 40 80/2

    2. M15 = 25 150 /2
    2. H1 = 18

    3. H4 = 13 25/2 round
    3. D1 = 8
"""


def find_patterns(data_df: pd.DataFrame, lookback_period: int = 15) -> pd.DataFrame:
    if data_df.empty or len(data_df) < lookback_period:
        print("insufficient data")
        return pd.DataFrame()

    result = []

    for pattern in candlestick_patterns:
        pattern_func = getattr(talib, pattern)
        patterns_results = pattern_func(data_df["open"], data_df["high"], data_df["low"], data_df["close"])

        for i in data_df.head(lookback_period).index:  # перебираем крч по исхожному индексу
            if patterns_results.iloc[i] != 0:
                candle_num = i
                datetime_candle = data_df.loc[i, "datetime"]
                direction = "bullish" if patterns_results.iloc[i] > 0 else "bearish"  # это функция возвращает
                weight = candle_rankings.get(
                    f"{pattern}_Bull" if direction == "bullish" else f"{pattern}_Bear",
                    0,
                )  # это конфиг смотрит ранги
                value = patterns_results.iloc[i]  # это просто возвраащет значение талибовской функции
                # print(candle_num, pattern, direction, weight, value)

                result.append(
                    {
                        "candle_num": candle_num,
                        "datetime": datetime_candle,
                        "direction": direction,
                        "pattern": pattern,  # имя паттерна
                        "value": value,  # bullish / bearish возвращает функция талиб
                        "weight": weight,  # вес по #https://thepatternsite.com/
                    }
                )

    result_df = pd.DataFrame(result)
    return result_df


# функция подтверэжения паттернов младшего таймфрейма с паттернами старшего optimized
def confirm_patterns(data_htf: pd.DataFrame, data_ltf: pd.DataFrame) -> pd.DataFrame:
    confirmed_patterns = []
    patterns_ltf = find_patterns(data_ltf, lookback_period=20)
    patterns_htf = find_patterns(data_htf, lookback_period=20)

    for _, row_ltf in patterns_ltf.iterrows():
        confirmed = False
        for _, pattern in patterns_htf.iterrows():
            if (
                row_ltf["pattern"] == pattern["pattern"]
                and pattern["datetime"] <= row_ltf["datetime"]
                and abs(row_ltf["datetime"] - pattern["datetime"])
                <= pd.Timedelta(days=3)  # если был 3 дня назад максимум
                and pattern["value"] == row_ltf["value"]
            ):
                # print(f"Confirmed: {row_ltf['pattern']} at {row_ltf['datetime']}")
                confirmed = True
                break
        if confirmed:
            confirmed_patterns.append(row_ltf)
    result_df = pd.DataFrame(confirmed_patterns)
    return result_df


if __name__ == "__main__":
    symbol = input("Enter symbol: ")
    symbol = symbol.upper()
    df_htf = CandlesData(symbol).get_trend_data()
    df_ltf = CandlesData(symbol).get_pattern_indicators_data()
    print(df_htf.head())
    print(df_ltf.head())
    rslt = confirm_patterns(df_htf, df_ltf)
    print(rslt)
