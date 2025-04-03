from calculate_indicators import find_indicators
from Data_from_bybit.receive_bybit import CandlesData

def analyze_trend(trend_indicators, pattern_indicators, htf_df):

    last = {
        'price': htf_df['close'].iloc[-1],
        'sma150': trend_indicators['sma150'].iloc[-1],
        'adx': trend_indicators['adx'].iloc[-1],
        'tenkan': trend_indicators['tenkan_sen'].iloc[-1],
        'kijun': trend_indicators['kijun_sen'].iloc[-1],
        'senkou_a': trend_indicators['senkou_span_a'].iloc[-1],
        'senkou_b': trend_indicators['senkou_span_b'].iloc[-1],
        'ema50': pattern_indicators['ema50'].iloc[-1],
        'rsi12': pattern_indicators['rsi12'].iloc[-1],
        'atr7': pattern_indicators['atr7'].iloc[-1]
    }

    # анализ направления тренда по ишимоку
    trend_direction = "flat"
    if last['price'] > last['senkou_a'] and last['price'] > last['senkou_b']:
        if last['tenkan'] > last['kijun']:
            trend_direction = "strong_bullish" # ultra long
        else:
            trend_direction = "bullish" # long
    elif last['price'] < last['senkou_a'] and last['price'] < last['senkou_b']:
        if last['tenkan'] < last['kijun']:
            trend_direction = "strong_bearish" # ultra short
        else:
            trend_direction = "bearish"  #short

    # сила тренда
    trend_strength = "weak"
    if last['adx'] > 75: # https://learn.bybit.com/ru/indicators/what-is-adx-indicator/
        trend_strength = "strongest" # оценка силы тренда по adx
    elif last['adx'] > 50:
        trend_strength = "stronger"
    elif last['adx'] > 25:
        trend_strength = "strong"
    else:
        trend_strength = "weak" # /flat

    return trend_direction, trend_strength, last

    # сигнал к покупке на тех аналихе
def signal_order(trend_direction, last):
    signal = 'hold'
    bull_trend = ["strong_bullish", "bullish"]
    bear_trend = ["strong_bearish", "bearish"]

    if trend_direction in bull_trend:
        if last['price'] > last['ema50'] and 30 < last['rsi12'] < 70 and last['senkou_a'] > last['senkou_b']:
            signal = "buy"
    elif trend_direction in bear_trend:
        if last['price'] < last['ema50'] and 30 < last['rsi12'] < 70 and last['senkou_a'] < last['senkou_b']:
            signal = "sell"

    return signal
# выстановке стоп лоззов и тейкпроффитов через тех анализ
def sl_tp(last, signal):
    sl = None
    tp = None

    if signal == "buy":
        sl = min(last['tenkan'], last['kijun'], last['ema50'] - 1.5 * last['atr7'])
        tp = [
            last['price'] + last['atr7'], #tp1
            last['price'] + 2 * last['atr7'], #tp2
            last['senkou_b'] if last['senkou_b'] > last['price'] else None # tp3 с сопротивлением
        ]
    elif signal == "sell":
        sl = max(last['tenkan'], last['kijun'], last['ema50'] + 1.5 * last['atr7'])
        tp = [
            last['price'] - last['atr7'],  # tp1
            last['price'] - 2 * last['atr7'],  # tp2
            last['senkou_b'] if last['senkou_b'] < last['price'] else None  # tp3 с сопротивлением
        ]

    return sl, tp

if __name__ == "__main__":
        trend = CandlesData("BTCUSDT").get_trend_data()
        pattern = CandlesData("BTCUSDT").get_pattern_indicators_data()
        trend_indicators, pattern_indicators = find_indicators(trend, pattern)

        trend_direction, trend_strength, last = analyze_trend(trend_indicators, pattern_indicators, trend)

        sign = signal_order(trend_direction, last)
        stop, take = sl_tp(last, sign)
        print(last)
        print(trend_direction, trend_strength, sign, stop, take)



