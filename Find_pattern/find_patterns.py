import talib
from Data_from_bybit.receive_bybit import CandlesData
from patterns_config import candlestick_patterns, candle_rankings

def check_empty(df):
    return df.empty
def check_candles_patterns(data_df, lookback_period = 100):
    patterns_data = []
    for pattern in candlestick_patterns.keys():
        pattern_func = getattr(talib, pattern)
        results = pattern_func(data_df['open'], data_df['high'], data_df['low'], data_df['close']) # поиск паттернов по всему периоду страшего фрейма
        recent_results = results.tail(lookback_period) # поиск паттернов в последних n свечах
        if check_empty(recent_results):
            return False
        else:
            pass
check_candles_patterns(CandlesData("BTCUSDT").get_trend_data())

'''
import pandas as pd

def check_recent_patterns(df, lookback=3):
    """
    Проверяет последние N свечей на наличие свечных паттернов.
    Возвращает DataFrame с колонками:
    - pattern_name: название паттерна
    - direction: bullish/bearish
    - count: сколько раз появился в lookback-периоде
    - last_signal: значение последнего сигнала (>0 = bullish, <0 = bearish)
    - ranking: сила паттерна (если используется candle_rankings)
    """
    patterns_data = []
    
    for pattern in candlestick_patterns.keys():
        pattern_func = getattr(talib, pattern)
        results = pattern_func(df['open'], df['high'], df['low'], df['close'])
        recent_results = results.tail(lookback)
        pattern_count = sum(recent_results != 0)
        
        if pattern_count > 0:
            direction = "bullish" if recent_results.iloc[-1] > 0 else "bearish"
            pattern_name = candlestick_patterns[pattern]
            
            # Добавляем ранг паттерна (если доступен candle_rankings)
            ranking = candle_rankings.get(f"{pattern}_Bull" if direction == "bullish" else f"{pattern}_Bear", 0)
            
            patterns_data.append({
                "pattern_name": pattern_name,
                "direction": direction,
                "count": pattern_count,
                "last_signal": recent_results.iloc[-1],
                "ranking": ranking  # Для сортировки по силе паттерна
            })
    
    # Создаем DataFrame и сортируем по рангу (чем меньше ranking, тем сильнее паттерн)
    patterns_df = pd.DataFrame(patterns_data)
    if not patterns_df.empty:
        patterns_df.sort_values(by="ranking", ascending=True, inplace=True)
    
    return patterns_df'''



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