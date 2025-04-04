from calculate_indicators import find_indicators
from Data_from_bybit.receive_bybit import CandlesData

def analyze_trend(trend_indicators, pattern_indicators, htf_df):

    last = {
        'price': htf_df['close'].iloc[-1], # простая скользящая средняя
        'sma150': trend_indicators['sma150'].iloc[-1],# простая скользящая средняя
        'adx': trend_indicators['adx'].iloc[-1],  # показатель силы тренла
        'tenkan': trend_indicators['tenkan_sen'].iloc[-1], # линия переворота ишимоку
        'kijun': trend_indicators['kijun_sen'].iloc[-1], # base lime ichinoku
        'senkou_a': trend_indicators['senkou_span_a'].iloc[-1], #  верхняя граница облака ишимоку
        'senkou_b': trend_indicators['senkou_span_b'].iloc[-1], #  нижеяя граница облака ишимоку
        'ema50': pattern_indicators['ema50'].iloc[-1], # эксопненциальная скользящая средняя для определения поддержки
        'rsi25': pattern_indicators['rsi25'].iloc[-1], # индикатор перекупленности и перепроданности
        'mfi': pattern_indicators['mfi'].iloc[-1],   #money flow index
        'atr14': pattern_indicators['atr14'].iloc[-1], # показатель волатильности для sl tp average treu range
        'shift5_obv': pattern_indicators['obv'].iloc[-6],
        'obv': pattern_indicators['obv'].iloc[-1], #on balance volume
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

    # сила тренда aadx + volumes
    trend_strength = "weak"
    if last['adx'] > 75 and last['obv'] > last['shift5_obv']: # https://learn.bybit.com/ru/indicators/what-is-adx-indicator/
        trend_strength = "strongest" # оценка силы тренда по adx
    elif last['adx'] > 50:
        trend_strength = "stronger"
    elif last['adx'] > 25 and last['mfi'] > 50:
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
        if (last['price'] > last['ema50'] and
                40 < last['rsi25'] < 70 and
                last['obv'] > last['shift5_obv'] and
                last['mfi'] > 50 and
                last['senkou_a'] > last['senkou_b']):

            signal = "buy"
    elif trend_direction in bear_trend:
        if (last['price'] < last['ema50'] and
                30 < last['rsi25'] < 60 and
                last['obv'] < last['shift5_obv'] and
                last['mfi'] < 50 and
                last['senkou_a'] < last['senkou_b']):

            signal = "sell"

    return signal
# выстановке стоп лоззов и тейкпроффитов через тех анализ
def sl_tp(last, signal):
    sl = None
    tp = None

    if signal == "buy":
        sl = min(last['tenkan'], last['kijun'], last['ema50'] - 1.5 * last['atr14'])
        tp = [
            last['price'] + last['atr14'], #tp1
            last['price'] + 2 * last['atr14'], #tp2
            last['senkou_b'] if last['senkou_b'] > last['price'] else None # tp3 с сопротивлением высчитывает
        ]
    elif signal == "sell":
        sl = max(last['tenkan'], last['kijun'], last['ema50'] + 1.5 * last['atr14'])
        tp = [
            last['price'] - last['atr14'],  # tp1
            last['price'] - 2 * last['atr14'],  # tp2
            last['senkou_b'] if last['senkou_b'] < last['price'] else None  # tp3 с сопротивлением
        ]

    return sl, tp
# ADD OBV MFI VOLUME URGENTLY
if __name__ == "__main__":
        trend = CandlesData("SOLUSDT").get_trend_data()
        pattern = CandlesData("SOLUSDT").get_pattern_indicators_data()
        trend_indicators, pattern_indicators = find_indicators(trend, pattern)
        trend_direction, trend_strength, last = analyze_trend(trend_indicators, pattern_indicators, trend)
        sign = signal_order(trend_direction, last)
        stop, take = sl_tp(last, sign)
        print(last)
        print(trend_direction, trend_strength, sign, stop, take)



