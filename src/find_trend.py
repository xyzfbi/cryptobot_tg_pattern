from src.find_patterns import generate_signal, confirm_patterns
from src.calculate_indicators import find_indicators
from src.receive_bybit import CandlesData


class TradingStrategy:
    def __init__(self, symbol, l_timeframe, h_timeframe):
        self.symbol = symbol.upper()
        self.trend_data = CandlesData(self.symbol).get_trend_data(timeframe=h_timeframe)
        self.pattern_data = CandlesData(self.symbol).get_pattern_indicators_data(timeframe=l_timeframe)
        self.trend_indicators, self.pattern_indicators = find_indicators(self.trend_data, self.pattern_data)
        self.trend_direction = "flat"
        self.trend_strength = "weak"
        self.last = {
            'price': self.trend_data['close'].iloc[0],  # price now
            'sma150': self.trend_indicators['sma150'].iloc[-1],  # простая скользящая средняя на 150 свеч
            'adx': self.trend_indicators['adx'].iloc[-1],  # индекс силы тренда
            'adx_plus': self.trend_indicators['plus_di'].iloc[-1],  # бычья сила
            'adx_minus': self.trend_indicators['minus_di'].iloc[-1],  # медвежья сила
            'tenkan': self.trend_indicators['tenkan_sen'].iloc[-1],  # ишимоку  че скзаать
            'kijun': self.trend_indicators['kijun_sen'].iloc[-1],
            # https://ru.wikipedia.org/wiki/%D0%98%D0%BD%D0%B4%D0%B8%D0%BA%D0%B0%D1%82%D0%BE%D1%80_%D0%98%D1%88%D0%B8%D0%BC%D0%BE%D0%BA%D1%83
            'senkou_a': self.trend_indicators['senkou_span_a'].iloc[-1],
            # https://ru.wikipedia.org/wiki/%D0%98%D0%BD%D0%B4%D0%B8%D0%BA%D0%B0%D1%82%D0%BE%D1%80_%D0%98%D1%88%D0%B8%D0%BC%D0%BE%D0%BA%D1%83
            'senkou_b': self.trend_indicators['senkou_span_b'].iloc[-1],
            # https://ru.wikipedia.org/wiki/%D0%98%D0%BD%D0%B4%D0%B8%D0%BA%D0%B0%D1%82%D0%BE%D1%80_%D0%98%D1%88%D0%B8%D0%BC%D0%BE%D0%BA%D1%83
            # индикаторы на 50 свеч макс по младшему тф
            'ema50': self.pattern_indicators['ema50'].iloc[-1],  # экспоненциальная скользящая средняя
            'rsi12': self.pattern_indicators['rsi12'].iloc[-1],
            # индекс перекупленности и перепроаднности 12 свеч младший таймфрейм
            'rsi25': self.pattern_indicators['rsi25'].iloc[-1],
            # индекс перекупленности и перепроаднности 25 свеч младший фрейм
            'atr7': self.pattern_indicators['atr7'].iloc[-1],  # волатильность рынка поддержки
            'macd': self.pattern_indicators['macd'].iloc[-1],
            # https://ru.wikipedia.org/wiki/%D0%98%D0%BD%D0%B4%D0%B8%D0%BA%D0%B0%D1%82%D0%BE%D1%80_MACD
            'macd_signal': self.pattern_indicators['macd_signal'].iloc[-1]
            # https://ru.wikipedia.org/wiki/%D0%98%D0%BD%D0%B4%D0%B8%D0%BA%D0%B0%D1%82%D0%BE%D1%80_MACD
        }
        self.confirmed_patterns = None
        self.signal = None
        self.sl = None
        self.tp = None

    def find_trend(self):

        # ЗАПРАЩИВАЕМ ПОСЛЕДНИЕ ЗНАЧЕНИЯ ИНДИКАТОРОВ ДЛЯ КАЖДОГО ФРЕЙМА

        # определение тренда - sma150 ichimoku ema
        trend_direction = "flat"
        cloud_bull = self.last['senkou_a'] > self.last['senkou_b']
        cloud_bear = self.last['senkou_a'] < self.last['senkou_b']

        if self.last['price'] > self.last['sma150'] and cloud_bull:
            if self.last['tenkan'] > self.last['kijun'] and self.last['price'] > self.last['ema50']:
                trend_direction = "strong_bullish"

            elif self.last['tenkan'] > self.last['kijun']:
                trend_direction = "bullish"

        elif self.last['price'] < self.last['sma150'] and cloud_bear:
            if self.last['tenkan'] < self.last['kijun'] and self.last['price'] < self.last['ema50']:
                trend_direction = "strong_bearish"

            elif self.last['tenkan'] < self.last['kijun']:
                trend_direction = "bearish"

        # определение силы тренда ADX
        trend_strength = "weak"
        if self.last['adx'] > 25:
            if self.last['adx_plus'] > self.last['adx_minus']:
                trend_strength = "bullish_strong" if self.last['adx'] > 50 else "bullish_weak"
            else:
                trend_strength = "bearish_strong" if self.last['adx'] > 50 else "bearish_weak"

        return trend_direction, trend_strength, self.last

    # sl tp через atr ema и ichimoku
    def sl_tp(self, signal):
        sl = None
        tp = []

        atr_multiplier = 2.0
        tp_multipliers = [1.0, 2.0, 3.0]

        if signal == "buy":
            # продвинктая система sl и tp
            # inspired trading view
            sl_candidates = [
                self.last['kijun'],
                self.last['tenkan'],
                self.last['ema50'] - atr_multiplier * self.last['atr7'],
                self.last['senkou_b'] if self.last['senkou_b'] < self.last['price'] else None
            ]
            sl = max([x for x in sl_candidates if x is not None])

            tp = [self.last['price'] + m * self.last['atr7'] for m in tp_multipliers]
            if self.last['senkou_a'] > self.last['price']:
                tp.append(self.last['senkou_a'])

        elif signal == "sell":
            # inspired trading view
            sl_candidates = [
                self.last['kijun'],
                self.last['tenkan'],
                self.last['ema50'] + atr_multiplier * self.last['atr7'],
                self.last['senkou_b'] if self.last['senkou_b'] > self.last['price'] else None
            ]
            sl = min([x for x in sl_candidates if x is not None])

            tp = [self.last['price'] - m * self.last['atr7'] for m in tp_multipliers]
            if self.last['senkou_a'] < self.last['price']:
                tp.append(self.last['senkou_a'])

        return sl, [x for x in tp if x is not None]

    # sl tp надо немного под паттерны переделать

    def return_signal(self):
        self.trend_direction, self.trend_strength, self.last = self.find_trend()
        self.confirmed_patterns = confirm_patterns(self.trend_data, self.pattern_data)
        self.signal = generate_signal(self.trend_direction, self.last, self.confirmed_patterns)
        self.sl, self.tp = self.sl_tp(self.last)

        self.print_res()

        return self.signal

    def print_res(self):
        print("price:", self.last['price'])
        print("trend:", self.trend_direction)
        print("strength:", self.trend_strength)
        print("signal:", self.signal)
        print("SL:", self.sl)
        print("TP LEVELS:", self.tp)

    def get_res_text(self):
        result = (
            f"price: {self.last['price']}\n"
            f"trend: {self.trend_direction}\n"
            f"strength: {self.trend_strength}\n"
            f"signal: {self.signal}\n"
            f"SL: {self.sl}\n"
            f"TP LEVELS: {self.tp}"
        )
        return result


if __name__ == "__main__":
    symbol = input("Enter symbol: ")
    strategy = TradingStrategy(symbol, 240, 'D')
    print(strategy.trend_data)
    strategy.return_signal()
