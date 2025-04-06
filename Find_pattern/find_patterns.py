import talib
import pandas as pd
from Data_from_bybit.receive_bybit import CandlesData
from patterns_config import candlestick_patterns, candle_rankings

"""
пары таймфреймов и свечи
    1. m1 = 75
    1. M5 = 40
    
    2. M15 = 25
    2. H1 = 18
    
    3. H4 = 13
    3. D1 = 8
"""

def find_patterns(data_df, lookback_period = 5):

    if data_df.empty or len(data_df) < lookback_period:
        print("insufficient data")
        return


    result = []

    for pattern in candlestick_patterns.keys():
        pattern_func = getattr(talib, pattern)
        patterns_results = pattern_func(data_df['open'],
                                        data_df['high'],
                                        data_df['low'],
                                        data_df['close']
                                        )
        '''print(patterns_results)
        print(patterns_results)
        print(type(patterns_results))
        print(patterns_results.columns)'''

        for i in data_df.head(lookback_period).index: # перебираем крч по исхожному индексу
            if patterns_results.iloc[i] != 0:
                candle_num = i
                datetime_candle = data_df.loc[i, 'datetime']
                direction = "bullish" if patterns_results.iloc[i] > 0 else "bearish" # это функция возвращает
                weight = candle_rankings.get(f"{pattern}_Bull" if direction == "bullish" else f"{pattern}_Bear",0 ) # это конфиг смотрит ранги
                value = patterns_results.iloc[i] # это просто возвраащет значение талибовской функции
                # print(candle_num, pattern, direction, weight, value)

                result.append({
                    'candle_num': candle_num,
                    'datetime': datetime_candle,
                    'direction': direction,
                    'pattern': pattern, # имя паттерна
                    'value': value, # bullish / bearish возвращает функция талиб
                    'weight': weight # вес по #https://thepatternsite.com/
                })

    # result_df = pd.DataFrame(result).sort_values(['weight'], ascending=[False])
    result_df = pd.DataFrame(result)
    return result_df


# сигналы на вход через rsi, macd, price относитльно ema и ichimoku cloud
def generate_signal(trend_direction, last):
    signal = 'hold'
    bull_trend = ["strong_bullish", "bullish"] #pep8
    bear_trend = ["strong_bearish", "bearish"]

    # доп условия для входа
    macd_bull = last['macd'] > last['macd_signal']
    macd_bear = last['macd'] < last['macd_signal']
    price_above_cloud = last['price'] > max(last['senkou_a'], last['senkou_b'])
    price_below_cloud = last['price'] < min(last['senkou_a'], last['senkou_b'])

    # generate signal by using trading view system
    if trend_direction in bull_trend:
        # inspired trading view
        conditions_count = [
            last['price'] > last['ema50'],
            last['rsi12'] > 30 and last['rsi12'] < 65,
            macd_bull,
            price_above_cloud,
            last['tenkan'] > last['kijun']
        ]
        if sum(conditions_count) >= 4:  # Минимум 4 из 5 условий
            signal = "buy"

    elif trend_direction in bear_trend:
        # inspired trading view
        conditions_count = [
            last['price'] < last['ema50'],
            last['rsi25'] < 70 and last['rsi25'] > 35,
            macd_bear,
            price_below_cloud,
            last['tenkan'] < last['kijun']
        ]
        if sum(conditions_count) >= 4:
            signal = "sell"

    return signal

if __name__ == "__main__":
    symbol = input("Enter symbol: ")
    df = CandlesData(symbol).get_trend_data()
    print(find_patterns(df, 7))
    df_ltf = CandlesData(symbol).get_pattern_indicators_data()
    print(find_patterns(df_ltf, 13))