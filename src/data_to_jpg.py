from typing import Union

import pandas as pd
import os
from src.receive_bybit import CandlesData
import matplotlib.pyplot as plt
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from matplotlib import font_manager as fm
from src.find_trend import TradingStrategy


def depict_candle_graph(
    data: pd.DataFrame,
    symbol: str = "BTCUSDT",
    l_tf: Union[str, int] = 15,
    h_tf: Union[str, int] = 60,
) -> None:
    data = data.head(20).copy()

    # преобразование в формат матплотлиба
    data["datetime"] = data["datetime"].map(mdates.date2num)

    # Выбор нужных столбцов и приведение к типу float
    data_ohlc = data[["datetime", "open", "high", "low", "close"]].astype(float)

    # расчитываем ширину свечи основанной на таймфрейме
    time_diffs = data_ohlc["datetime"].diff().dropna()
    if not time_diffs.empty:
        candle_width = time_diffs.min() * 0.8
    else:
        candle_width = 0.6  # запасной вариант, если дифф не вычисляется

    # шрифт
    prop = fm.FontProperties(family="DejaVu Sans", weight="bold")

    # создание фигуры
    fig, ax = plt.subplots(figsize=(15, 7))
    ax.set_facecolor("#101014")

    # рисование свечей
    candlestick_ohlc(ax, data_ohlc.values, width=candle_width, colorup="#20b26c", colordown="#ef454a")

    # настройки осей
    ax.xaxis_date()
    if h_tf in [60, 240]:
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    else:
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M"))
    plt.xticks(rotation=0, color="#737376")
    plt.yticks(rotation=0, color="#737376")
    for tick in ax.get_xticklabels():
        tick.set_fontproperties(prop)
    for tick in ax.get_yticklabels():
        tick.set_fontproperties(prop)

    # количество отметок по оси y
    ax.yaxis.set_major_locator(mticker.MaxNLocator(nbins=12))

    # настрока пределов по оси x
    max_date = data_ohlc["datetime"].max()
    min_date = data_ohlc["datetime"].min()
    delta = max_date - min_date
    ax.set_xlim(min_date, max_date + delta / 2)

    # заголовки и сетка
    plt.title(symbol, fontsize=24, fontweight="bold", color="#737376", fontproperties=prop)
    plt.xlabel(
        "Date and time",
        fontsize=14,
        fontweight="bold",
        color="#737376",
        fontproperties=prop,
    )
    plt.ylabel("Price", fontsize=14, fontweight="bold", color="#737376", fontproperties=prop)
    plt.grid(True, alpha=0.2, color="#202124", linewidth=2)
    for spine in ax.spines.values():
        spine.set_color("#71757a")
        spine.set_linewidth(1)

    # цвет фона
    fig.patch.set_facecolor("#101014")

    strategy = TradingStrategy(symbol, l_tf, h_tf)

    signal = strategy.return_signal()
    sl_level = strategy.sl
    tp_levels = strategy.tp

    # Получаем диапазон Y
    y_min, y_max = ax.get_ylim()
    y_range = (y_max - y_min) * 0.20

    # начальные координаты стрелки
    arrow_x = 2 * data_ohlc["datetime"].iloc[0] - data_ohlc["datetime"].iloc[1]
    arrow_y = max(data_ohlc["close"].iloc[0], data_ohlc["open"].iloc[0])

    # отрисовка стрелки и sl _ tp
    if signal == "buy" or signal == "sell":
        color = "green"
        if signal == "sell":
            y_range = -y_range
            color = "red"

        # Задаем цвета ЛОКАЛЬНО, а не глобально!
        sl_line_color = "red"
        tp_line_color = "green"

        ax.annotate(
            "",
            xy=(arrow_x, arrow_y + y_range),
            xytext=(arrow_x, arrow_y),
            arrowprops=dict(facecolor=color, shrink=0, width=10, headwidth=28),
            fontsize=12,
            color=color,
        )

        ax.text(
            arrow_x,
            arrow_y - y_range * 0.25,
            f"{signal.upper()} Signal",
            fontsize=15,
            color=color,
            ha="left",
            fontweight="bold",
            fontproperties=prop,
        )

        if sl_level:
            ax.axhline(y=sl_level, color=sl_line_color, linestyle="-", linewidth=1, alpha=0.5)
            ax.text(
                data_ohlc["datetime"].iloc[0],
                sl_level,
                f"SL: {sl_level:.2f}",
                color=sl_line_color,
                fontweight="bold",
                fontproperties=prop,
                va="bottom" if signal == "buy" else "top",
                ha="right",
            )

        for tp in tp_levels:
            ax.axhline(y=tp, color=tp_line_color, linestyle="-", linewidth=1, alpha=0.5)
            ax.text(
                data_ohlc["datetime"].iloc[0],
                tp,
                f"TP: {tp:.2f}",
                color=tp_line_color,
                fontweight="bold",
                fontproperties=prop,
                va="bottom" if signal == "buy" else "top",
                ha="right",
            )
    else:
        color = "grey"
        ax.annotate(
            "",
            xy=(arrow_x + y_range, arrow_y),
            xytext=(arrow_x, arrow_y),
            arrowprops=dict(facecolor=color, shrink=0, width=10, headwidth=28),
            fontsize=12,
            color=color,
        )
        ax.text(
            arrow_x,
            arrow_y - y_range * 0.25,
            f"{' '.join(signal.upper().split('_'))} Signal",
            fontsize=15,
            color=color,
            ha="left",
            fontweight="bold",
            fontproperties=prop,
        )

    plt.tight_layout()
    path = os.path.join("tgbot", "buf.png")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    plt.savefig(path)


class DepictCandleGraph:
    def __init__(self, candle_data):
        self.candle_data = candle_data

    @staticmethod
    def depict_candle_white(self):
        pass

    def depict_candle_black(self, symbol="BTCUSDT"):
        pass


if __name__ == "__main__":
    smbl = input("Input symbol: ").upper()
    data_df = CandlesData(smbl).get_trend_data(timeframe="D")
    depict_candle_graph(data_df, smbl, 15, 60)
