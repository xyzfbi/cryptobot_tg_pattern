from typing import Tuple

import pandas as pd
import talib as ta
from pandas import DataFrame

from src.receive_bybit import CandlesData


# calculate ichimoku   !!!!
def calculate_ichimoku(
    df: pd.DataFrame,
    tenkan_num: int = 9,
    kijun_period: int = 26,
    senkou_period: int = 52,
):
    result_df = pd.DataFrame()

    tenkan_high = df["high"].rolling(tenkan_num).max()
    tenkan_low = df["low"].rolling(tenkan_num).min()
    result_df["tenkan_sen"] = (tenkan_high + tenkan_low) / 2

    kijun_high = df["high"].rolling(kijun_period).max()
    kijun_low = df["low"].rolling(kijun_period).min()
    result_df["kijun_sen"] = (kijun_high + kijun_low) / 2

    result_df["senkou_span_a"] = ((result_df["tenkan_sen"] + result_df["kijun_sen"]) / 2).shift(kijun_period)

    senkou_high = df["high"].rolling(senkou_period).max()
    senkou_low = df["low"].rolling(senkou_period).min()
    result_df["senkou_span_b"] = ((senkou_high + senkou_low) / 2).shift(kijun_period)

    result_df["chikou_span"] = df["close"].shift(-kijun_period)

    result_df["cloud_green"] = result_df["senkou_span_a"] > result_df["senkou_span_b"]
    result_df["cloud_red"] = result_df["senkou_span_a"] < result_df["senkou_span_b"]

    result_df["leading_senkou_span_a"] = result_df["senkou_span_a"].shift(-kijun_period)
    result_df["leading_senkou_span_b"] = result_df["senkou_span_b"].shift(-kijun_period)

    return result_df


# вычисление всех нужных индикаторов
def find_indicators(highframe_df: pd.DataFrame, lowframe_df: pd.DataFrame) -> tuple[DataFrame, DataFrame]:
    # module high time frame
    high_htf = highframe_df["high"]
    close_htf = highframe_df["close"]
    low_htf = highframe_df["low"]

    high_ltf = lowframe_df["high"]
    close_ltf = lowframe_df["close"]
    low_ltf = lowframe_df["low"]

    # INDICATORS HIGHTIME FRAME
    sma150_htf = ta.SMA(close_htf, 150)
    adx_htf = ta.ADX(high_htf, low_htf, close_htf, 14)
    plusdi_htf = ta.PLUS_DI(high_htf, low_htf, close_htf, 14)
    minusdi_htf = ta.MINUS_DI(high_htf, low_htf, close_htf, 14)
    ichimoku_htf = calculate_ichimoku(highframe_df)

    # form indicators HIGH timeframe

    indicators_htf = pd.DataFrame(
        {
            "sma150": sma150_htf,  # общий тренд
            "adx": adx_htf,  # сила тренда
            "plus_di": plusdi_htf,
            "minus_di": minusdi_htf,
        }
    )
    indicators_htf = pd.concat([indicators_htf, ichimoku_htf], axis=1)

    # module low timeframee

    ema50_ltf = ta.EMA(close_ltf, 50)

    rsi25_ltf = ta.RSI(close_ltf, 25)  # RSI 25 CANDLES
    rsi12_ltf = ta.RSI(close_ltf, 12)  # RSI 12 CANDLES
    macd_line, macd_signal, macd_hist = ta.MACD(close_ltf, 12, 26, 9)  # MACD
    atr7_ltf = ta.ATR(high_ltf, low_ltf, close_ltf, 7)  # ATR 7 CANDLES

    # form indicators LOW timeframe
    indicators_ltf = pd.DataFrame(
        {
            "ema50": ema50_ltf,
            "rsi12": rsi12_ltf,
            "rsi25": rsi25_ltf,
            "atr7": atr7_ltf,
            "macd": macd_line,
            "macd_signal": macd_signal,
        }
    )

    return indicators_htf, indicators_ltf


# testing
if __name__ == "__main__":
    symbol = input("Enter symbol: ")
    symbol = symbol.upper()
    data = CandlesData(symbol).get_trend_data()
    trend_df = CandlesData(symbol).get_trend_data()
    patterns_df = CandlesData(symbol).get_pattern_indicators_data()

    trend_indicators, pattern_indicators = find_indicators(trend_df, patterns_df)
    trend_indicators.to_csv("data/trend_indicators.csv")
    pattern_indicators.to_csv("data/pattern_indicators.csv")
    print(trend_indicators)
    print(pattern_indicators)
