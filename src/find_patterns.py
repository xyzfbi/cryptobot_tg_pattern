import talib
import pandas as pd
from src.receive_bybit import CandlesData
from src.patterns_config import candlestick_patterns, candle_rankings

"""
пары таймфреймов и свечи
    1. m1 = 75 150/2
    1. M5 = 40 80/2
    
    2. M15 = 25 150 /2
    2. H1 = 18 
    
    3. H4 = 13 25/2 round
    3. D1 = 8
"""

def find_patterns(data_df, lookback_period = 15):

    if data_df.empty or len(data_df) < lookback_period:
        print("insufficient data")
        return pd.DataFrame()


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
# функция подтверэжения паттернов младшего таймфрейма с паттернами старшего optimized
def confirm_patterns(data_htf, data_ltf):
    confirmed_patterns = []
    patterns_ltf = find_patterns(data_ltf, lookback_period = 15)
    patterns_htf = find_patterns(data_htf, lookback_period = 15)

    for _, row_ltf in patterns_ltf.iterrows():
        confirmed = False
        for _, pattern in patterns_htf.iterrows():
            # print(f"Comparing {row_ltf['pattern']} ({row_ltf['datetime']}) with {pattern['pattern']} ({pattern['datetime']})")
            if (row_ltf['pattern'] == pattern['pattern'] and
                    pattern['datetime'] <= row_ltf['datetime'] and
                    abs(row_ltf['datetime'] - pattern['datetime']) <= pd.Timedelta(days=100) and # если был 3 дня назад максимум
                    pattern['value'] == row_ltf['value']):
                # print(f"Confirmed: {row_ltf['pattern']} at {row_ltf['datetime']}")
                confirmed = True
                break
        if confirmed:
            confirmed_patterns.append(row_ltf)
    result_df = pd.DataFrame(confirmed_patterns)
    return result_df




# сигналы на вход через rsi, macd, price относитльно ema и ichimoku cloud
def generate_signal(trend_direction, last, confirmed_patterns):
    signal = 'hold'
    bull_trend = ["strong_bullish", "bullish"] #pep8
    bear_trend = ["strong_bearish", "bearish"]
    min_weight = 30
    if confirmed_patterns.empty:
        return 'hold_no_pattern'

    # доп условия для входа
    macd_bull = last['macd'] > last['macd_signal']
    macd_bear = last['macd'] < last['macd_signal']
    price_above_cloud = last['price'] > max(last['senkou_a'], last['senkou_b'])
    price_below_cloud = last['price'] < min(last['senkou_a'], last['senkou_b'])
    weight_in_conditions = 0.02

    weight_patterns_bull = sum(
        row['weight'] * weight_in_conditions
        for _, row in confirmed_patterns.iterrows()
        if row['value'] == 100 and row['weight'] > min_weight # влияние паттернов вычисляется по весу
    )
    weight_patterns_bear = sum(
        row['weight'] * weight_in_conditions
        for _, row in confirmed_patterns.iterrows()
        if row['value'] == -100 and row['weight'] > min_weight # влияние паттернов вычисляется по весу
    )


    # generate signal by using trading view system
    if trend_direction in bull_trend:
        # inspired trading view
        conditions_count = [
            last['price'] > last['ema50'],
            30 < last['rsi12'] < 65,
            macd_bull,
            price_above_cloud,
            last['tenkan'] > last['kijun'],
            weight_patterns_bull
        ]
        if sum(conditions_count) >= 6:  # Минимум 5 из 6 условий
            signal = "buy"

    elif trend_direction in bear_trend:
        # inspired trading view
        conditions_count = [
            last['price'] < last['ema50'],
            70 > last['rsi25'] > 35,
            macd_bear,
            price_below_cloud,
            last['tenkan'] < last['kijun'],
            weight_patterns_bear
        ]
        if sum(conditions_count) >= 5:
            signal = "sell"

    return signal



if __name__ == "__main__":
    symbol = input("Enter symbol: ")
    symbol = symbol.upper()
    df_htf = CandlesData(symbol).get_trend_data()
    df_ltf = CandlesData(symbol).get_pattern_indicators_data()
    print(df_htf.head())
    print(df_ltf.head())
    result = confirm_patterns(df_htf, df_ltf)
    print(result)
