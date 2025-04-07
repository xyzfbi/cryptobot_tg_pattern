from Find_pattern.find_patterns import generate_signal, confirm_patterns
from calculate_indicators import find_indicators
from Data_from_bybit.receive_bybit import CandlesData


def find_trend(trend_indicators, pattern_indicators, htf_df):
    last = {
        'price': htf_df['close'].iloc[0], # price now
        'sma150': trend_indicators['sma150'].iloc[-1], # простая скользящая средняя на 150 свеч
        'adx': trend_indicators['adx'].iloc[-1], # индекс силы тренда
        'adx_plus': trend_indicators['plus_di'].iloc[-1], # бычья сила
        'adx_minus': trend_indicators['minus_di'].iloc[-1], # медвежья сила
        'tenkan': trend_indicators['tenkan_sen'].iloc[-1], # ишимоку  че скзаать
        'kijun': trend_indicators['kijun_sen'].iloc[-1],  # https://ru.wikipedia.org/wiki/%D0%98%D0%BD%D0%B4%D0%B8%D0%BA%D0%B0%D1%82%D0%BE%D1%80_%D0%98%D1%88%D0%B8%D0%BC%D0%BE%D0%BA%D1%83
        'senkou_a': trend_indicators['senkou_span_a'].iloc[-1], # https://ru.wikipedia.org/wiki/%D0%98%D0%BD%D0%B4%D0%B8%D0%BA%D0%B0%D1%82%D0%BE%D1%80_%D0%98%D1%88%D0%B8%D0%BC%D0%BE%D0%BA%D1%83
        'senkou_b': trend_indicators['senkou_span_b'].iloc[-1], # https://ru.wikipedia.org/wiki/%D0%98%D0%BD%D0%B4%D0%B8%D0%BA%D0%B0%D1%82%D0%BE%D1%80_%D0%98%D1%88%D0%B8%D0%BC%D0%BE%D0%BA%D1%83
        # индикаторы на 50 свеч макс по младшему тф
        'ema50': pattern_indicators['ema50'].iloc[-1], # экспоненциальная скользящая средняя
        'rsi12': pattern_indicators['rsi12'].iloc[-1], # индекс перекупленности и перепроаднности 12 свеч младший таймфрейм
        'rsi25': pattern_indicators['rsi25'].iloc[-1], # индекс перекупленности и перепроаднности 25 свеч младший фрейм
        'atr7': pattern_indicators['atr7'].iloc[-1],  # волатильность рынка поддержки
        'macd': pattern_indicators['macd'].iloc[-1], # https://ru.wikipedia.org/wiki/%D0%98%D0%BD%D0%B4%D0%B8%D0%BA%D0%B0%D1%82%D0%BE%D1%80_MACD
        'macd_signal': pattern_indicators['macd_signal'].iloc[-1] # https://ru.wikipedia.org/wiki/%D0%98%D0%BD%D0%B4%D0%B8%D0%BA%D0%B0%D1%82%D0%BE%D1%80_MACD
    }

    # определение тренда - sma150 ichimoku ema
    trend_direction = "flat"
    cloud_bull = last['senkou_a'] > last['senkou_b']
    cloud_bear = last['senkou_a'] < last['senkou_b']

    if last['price'] > last['sma150'] and cloud_bull:
        if last['tenkan'] > last['kijun'] and last['price'] > last['ema50']:
            trend_direction = "strong_bullish"

        elif last['tenkan'] > last['kijun']:
            trend_direction = "bullish"

    elif last['price'] < last['sma150'] and cloud_bear:
        if last['tenkan'] < last['kijun'] and last['price'] < last['ema50']:
            trend_direction = "strong_bearish"

        elif last['tenkan'] < last['kijun']:
            trend_direction = "bearish"

    # определение силы тренда ADX
    trend_strength = "weak"
    if last['adx'] > 25:
        if last['adx_plus'] > last['adx_minus']:
            trend_strength = "bullish_strong" if last['adx'] > 50 else "bullish_weak"
        else:
            trend_strength = "bearish_strong" if last['adx'] > 50 else "bearish_weak"

    return trend_direction, trend_strength, last



# sl tp через atr ema и ichimoku
def sl_tp(last, signal):
    sl = None
    tp = []

    atr_multiplier = 2.0
    tp_multipliers = [1.0, 2.0, 3.0]

    if signal == "buy":
        # продвинктая система sl и tp
        # inspired trading view
        sl_candidates = [
            last['kijun'],
            last['tenkan'],
            last['ema50'] - atr_multiplier * last['atr7'],
            last['senkou_b'] if last['senkou_b'] < last['price'] else None
        ]
        sl = max([x for x in sl_candidates if x is not None])


        tp = [last['price'] + m * last['atr7'] for m in tp_multipliers]
        if last['senkou_a'] > last['price']:
            tp.append(last['senkou_a'])

    elif signal == "sell":
        # inspired trading view
        sl_candidates = [
            last['kijun'],
            last['tenkan'],
            last['ema50'] + atr_multiplier * last['atr7'],
            last['senkou_b'] if last['senkou_b'] > last['price'] else None
        ]
        sl = min([x for x in sl_candidates if x is not None])

        tp = [last['price'] - m * last['atr7'] for m in tp_multipliers]
        if last['senkou_a'] < last['price']:
            tp.append(last['senkou_a'])

    return sl, [x for x in tp if x is not None]
# sl tp надо немного под паттерны переделать

if __name__ == "__main__":
        symbol = input("Enter symbol: ")
        symbol = symbol.upper()

        trend = CandlesData(symbol).get_trend_data()
        pattern = CandlesData(symbol).get_pattern_indicators_data()
        trend_indicators, pattern_indicators = find_indicators(trend, pattern)

        trend_direction, trend_strength, last = find_trend(trend_indicators, pattern_indicators, trend)
        confirmed_patterns = confirm_patterns(trend, pattern)
        sign = generate_signal(trend_direction, last, confirmed_patterns)
        stop, take = sl_tp(last, sign)

        print("price:", last['price'])
        print("trend:", trend_direction)
        print("strength:", trend_strength)
        print("signal:", sign)
        print("SL:", stop)
        print("TP LEVELS:", take)

