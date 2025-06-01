from src.find_patterns import confirm_patterns
from src.calculate_indicators import find_indicators
from src.receive_bybit import CandlesData
from decimal import Decimal
from typing import Any, Tuple, List, Dict, Optional, Union
import pandas as pd


class TradingStrategy:
    def __init__(self, symbol: str, l_timeframe: int, h_timeframe: Union[int, str]):
        self.symbol: str = symbol.upper()
        self.l_timeframe: int = l_timeframe
        self.h_timeframe: int = h_timeframe

        self.trend_data: pd.DataFrame = CandlesData(self.symbol).get_trend_data(timeframe=h_timeframe)
        self.pattern_data: pd.DataFrame = CandlesData(self.symbol).get_pattern_indicators_data(timeframe=l_timeframe)
        self.trend_indicators, self.pattern_indicators = find_indicators(self.trend_data, self.pattern_data)

        self.trend_direction: Optional[str] = None
        self.trend_strength: Optional[str] = None
        self.last: Optional[Dict[str, Any]] = None
        self.confirmed_patterns: Optional[pd.DataFrame] = None
        self.signal: Optional[str] = None
        self.sl: Optional[float] = None
        self.tp: Optional[List[float]] = None

        self._fill_last()
        self._analyze()

    def _fill_last(self) -> None:
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
            # https://ru.wikipedia.org/wiki/%D0%98%D0%BD%D0%B8%D0%BA%D0%B0%D1%82%D0%BE%D1%80_%D0%98%D1%88%D0%B8%D0%BC%D0%BE%D0%BA%D1%83
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
            # https://ru.wikipedia.org/wiki/%D0%98%D0%BD%D0%B8%D0%BA%D0%B0%D1%82%D0%BE%D1%80_MACD
        }

    def _analyze(self) -> None:
        self.trend_direction, self.trend_strength, self.last = self.find_trend()
        self.confirmed_patterns = confirm_patterns(self.trend_data, self.pattern_data)
        self.signal = self.generate_signal(self.trend_direction, self.last, self.confirmed_patterns)
        self.sl, self.tp = self.sl_tp(self.signal)

    def find_trend(self) -> Tuple[str, str, Dict[str, any]]:

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
        if self.last['adx'] > 20:
            if self.last['adx_plus'] > self.last['adx_minus']:
                trend_strength = "bullish_strong" if self.last['adx'] > 40 else "bullish_weak"
            else:
                trend_strength = "bearish_strong" if self.last['adx'] > 49 else "bearish_weak"

        return trend_direction, trend_strength, self.last

    # sl tp через atr ema и ichimoku
    def sl_tp(self, signal: str) -> Tuple[Optional[float], List[float]]:
        sl = None
        tp = []
        sl_multiplier = 0.92
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
            sl = min([x for x in sl_candidates if x is not None])
            sl *= sl_multiplier
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
            sl = max([x for x in sl_candidates if x is not None])
            sl *= sl_multiplier

            tp = [self.last['price'] - m * self.last['atr7'] for m in tp_multipliers]
            if self.last['senkou_a'] < self.last['price']:
                tp.append(self.last['senkou_a'])

        return sl, [float(round(x, 2)) for x in tp if x is not None]

    # sl tp надо немного под паттерны переделать

    @staticmethod
    def generate_signal(trend_direction: str, last: Dict[str, any], confirmed_patterns: pd.DataFrame) -> str:
        bull_trend = ["strong_bullish", "bullish"]  # pep8
        bear_trend = ["strong_bearish", "bearish"]
        min_weight = 25
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
            if row['value'] == 100 and row['weight'] > min_weight  # влияние паттернов вычисляется по весу
        )
        weight_patterns_bear = sum(
            row['weight'] * weight_in_conditions
            for _, row in confirmed_patterns.iterrows()
            if row['value'] == -100 and row['weight'] > min_weight  # влияние паттернов вычисляется по весу
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
            if sum(bool(x) for x in conditions_count) >= 5:  # Минимум 5 из 6 условий
                return "buy"

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
            if sum(bool(x) for x in conditions_count) >= 4:
                return "sell"
        else:
            return "hold"

        return "hold"

    def return_signal(self) -> Optional[str]:
        # Пересчёт, если нужно вручную обновить состояние
        self._fill_last()
        self._analyze()
        return self.signal

    def get_res_text(self) -> str:
        result = (
            f"Coin: {self.symbol}\n"
            f"price: {self.last['price']}\n"
            f"trend: {self.trend_direction}\n"
            f"strength: {self.trend_strength}\n"
            f"signal: {self.signal}\n"
            f"SL: {self.sl}\n"
            f"TP LEVELS: {self.tp}"
        )
        return result


if __name__ == "__main__":
    smbl = input("Enter symbol: ")
    strategy = TradingStrategy(smbl, 15, 60)
    print(strategy.get_res_text())
