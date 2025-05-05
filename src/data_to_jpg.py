from src.receive_bybit import CandlesData
import matplotlib.pyplot as plt
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from matplotlib import font_manager as fm
from src.find_trend import TradingStrategy


def depict_candle_graph(data, symbol="BTCUSDT", l_tf=15, h_tf=60):
    data = data.head(20)

    # преобразование в формат матплотлиба
    data['datetime'] = data['datetime'].map(mdates.date2num)

    # выбор только нужных столбцов
    data_ohlc = data[['datetime', 'open', 'high', 'low', 'close']]
    data_ohlc = data_ohlc.astype(float)
    print(data_ohlc)

    # шрифт
    prop = fm.FontProperties(family='DejaVu Sans', weight='bold')

    # создание фигуры
    fig, ax = plt.subplots(figsize=(15, 7))
    ax.set_facecolor('#101014')

    # рисование свечей
    candlestick_ohlc(ax, data_ohlc.values, width=0.6, colorup='#20b26c', colordown='#ef454a')

    # настройки осей
    ax.xaxis_date()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    plt.xticks(rotation=0, color='#737376')
    plt.yticks(rotation=0, color='#737376')
    for tick in ax.get_xticklabels():
        tick.set_fontproperties(prop)
    for tick in ax.get_yticklabels():
        tick.set_fontproperties(prop)

    # количество отметок по оси y
    ax.yaxis.set_major_locator(mticker.MaxNLocator(nbins=12))

    # настрока пределов по оси x
    max_date = data_ohlc['datetime'].max()
    min_date = data_ohlc['datetime'].min()
    delta = max_date - min_date
    ax.set_xlim(min_date, max_date + delta / 2)

    # заголовки и сетка
    plt.title(symbol, fontsize=24, fontweight='bold', color='#737376', fontproperties=prop)
    plt.xlabel('Date and time', fontsize=14, fontweight='bold', color='#737376', fontproperties=prop)
    plt.ylabel('Price', fontsize=14, fontweight='bold', color='#737376', fontproperties=prop)
    plt.grid(True, alpha=0.2, color='#202124', linewidth=2)
    for spine in ax.spines.values():
        spine.set_color('#71757a')
        spine.set_linewidth(1)

    # цвет фона
    fig.patch.set_facecolor('#101014')

    strategy = TradingStrategy(symbol, l_tf, h_tf)

    signal = strategy.return_signal()
    sl_level = strategy.sl
    tp_levels = strategy.tp

    # Получаем диапазон Y
    y_min, y_max = ax.get_ylim()
    y_range = (y_max - y_min) * 0.20

    # начальные координаты стрелки
    arrow_x = 2 * data_ohlc['datetime'].iloc[0] - data_ohlc['datetime'].iloc[1]
    arrow_y = max(data_ohlc['close'].iloc[0], data_ohlc['open'].iloc[0])

    if signal == 'buy' or signal == 'sell':
        color = 'green'

        if signal == 'sell':
            y_range = -y_range
            color = 'red'

        ax.annotate('',
                    xy=(arrow_x, arrow_y + y_range),
                    xytext=(arrow_x, arrow_y),
                    arrowprops=dict(facecolor=color, shrink=0, width=10, headwidth=28),
                    fontsize=12,
                    color=color)

        ax.text(arrow_x, arrow_y - y_range * 0.25, f'{signal.upper()} Signal', fontsize=15, color='green', ha='left',
                fontweight='bold', fontproperties=prop)
        if signal == 'buy':
            sl_line_color = 'red'
            tp_line_color = 'green'
        elif signal == 'sell':
            sl_line_color = 'red'
            tp_line_color = 'green'

        ax.axhline(y=sl_level, color=sl_line_color, linestyle='--', linewidth=2)
        ax.text(
            data_ohlc['datetime'].iloc[0],
            sl_level,
            f"SL: {sl_level:.2f}",
            color=sl_line_color,
            fontweight='bold',
            fontproperties=prop,
            va='bottom' if signal == 'buy' else 'top'
        )
        for i, tp in enumerate(tp_levels):
            ax.axhline(y=tp, color=tp_line_color, linestyle='--', linewidth=2)
            ax.text(
                data_ohlc['datetime'].iloc[0],
                tp,
                f"TP: {tp:.2f}",
                color=tp_line_color,
                fontweight='bold',
                fontproperties=prop,
                va='bottom' if signal == 'buy' else 'top'
            )
    else:
        color = 'grey'
        ax.annotate('',
                    xy=(arrow_x + y_range, arrow_y),
                    xytext=(arrow_x, arrow_y),
                    arrowprops=dict(facecolor=color, shrink=0, width=10, headwidth=28),
                    fontsize=12,
                    color=color)

        ax.text(arrow_x,
                arrow_y - y_range * 0.25,
                f'{' '.join(signal.upper().split('_'))} Signal',
                fontsize=15, color=color,
                ha='left',
                fontweight='bold',
                fontproperties=prop
                )

    plt.tight_layout()
    path = '../tgbot/buf.jpg'
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
    symbol = input("Input symbol: ").upper()
    data_df = CandlesData(symbol).get_trend_data(timeframe='D')
    depict_candle_graph(data_df, symbol, 240, 'D')
