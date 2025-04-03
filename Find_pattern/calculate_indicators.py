from Data_from_bybit.receive_bybit import CandlesData
import pandas as pd
import talib as ta

def calculate_ichimoku(df, tenkan_num = 9,  kijun_period = 26, senkou_period = 52):
    result_df = pd.DataFrame()

    tenkan_high = df['high'].rolling(tenkan_num).max()
    tenkan_low = df['low'].rolling(tenkan_num).min()
    result_df['tenkan_sen'] = (tenkan_high + tenkan_low)/2

    kijun_high = df['high'].rolling(kijun_period).max()
    kijun_low = df['low'].rolling(kijun_period).min()
    result_df['kijun_sen'] = (kijun_high + kijun_low)/2

    result_df['senkou_span_a'] = ((result_df['tenkan_sen'] + result_df['kijun_sen']) / 2).shift(kijun_period)

    senkou_high = df['high'].rolling(senkou_period).max()
    senkou_low = df['low'].rolling(senkou_period).min()
    result_df['senkou_span_b'] = ((senkou_high + senkou_low) / 2).shift(kijun_period)

    result_df['chikou_span'] = df['close'].shift(-kijun_period)

    result_df['cloud_green'] = result_df['senkou_span_a'] > result_df['senkou_span_b']
    result_df['cloud_red'] = result_df['senkou_span_a'] < result_df['senkou_span_b']

    result_df['leading_senkou_span_a'] = result_df['senkou_span_a'].shift(-kijun_period)
    result_df['leading_senkou_span_b'] = result_df['senkou_span_b'].shift(-kijun_period)

    return result_df

def find_indicators(highframe_df, lowframe_df):
    # module high time frame
    high = highframe_df['high']
    close = highframe_df["close"]
    low = highframe_df["low"]

    sma150_htf = ta.SMA(close, 150)
    adx_htf = ta.ADX(high, low, close, 14)
    ichimoku_htf = calculate_ichimoku(highframe_df)
    indicators_htf = pd.DataFrame({
        'sma150': sma150_htf,
        'adx': adx_htf,
    })
    indicators_htf = pd.concat([indicators_htf, ichimoku_htf], axis=1)
    # module low timeframee

    ema50_ltf = ta.EMA(close, 50)
    rsi12_ltf = ta.RSI(close, 12)
    atr7_ltf = ta.ATR(high, low, close, 7)
    indicators_ltf = pd.DataFrame({
        'ema50': ema50_ltf,
        'rsi12': rsi12_ltf,
        'atr7': atr7_ltf,
    })

    return indicators_htf, indicators_ltf


if __name__ == "__main__":
    data = CandlesData("BTCUSDT").get_trend_data()
    trend_df = CandlesData("BTCUSDT").get_trend_data()
    patterns_df = CandlesData("BTCUSDT").get_pattern_indicators_data()

    trend_indicators, pattern_indicators = find_indicators(trend_df, patterns_df)

    print(trend_indicators)
    print(pattern_indicators)