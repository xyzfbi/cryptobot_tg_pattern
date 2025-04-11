from receive_bybit import CandlesData
import matplotlib.pyplot as plt
import pandas as pd
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.dates as mdates
import matplotlib.ticker as mticker

def depict_candle_graph(data, symbol="BTCUSDT"):
    #преобразование в формат матплотлиба
    data['datetime'] = data['datetime'].map(mdates.date2num)

    #выбор только нужных столбцов
    data_ohlc = data[['datetime','open', 'high', 'low', 'close']]
    data_ohlc = data_ohlc.astype(float)
    print(data_ohlc)

    #создание фигуры
    fig, ax = plt.subplots(figsize=(15, 7))
    
    #рисование свечей
    candlestick_ohlc(ax, data_ohlc.values, width = 0.6, colorup = 'lime', colordown = 'crimson')

    #настройки осей
    ax.xaxis_date()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    plt.xticks(rotation = 0)

    #количество отметок по оси y
    ax.yaxis.set_major_locator(mticker.MaxNLocator(nbins=12))

    #настрока пределов по оси x
    max_date = data_ohlc['datetime'].max()
    min_date = data_ohlc['datetime'].min()
    delta = max_date - min_date
    ax.set_xlim(min_date, max_date + delta)

    #заголовки и сетка
    plt.title(symbol, fontsize = 18, fontweight='bold')
    plt.xlabel('Дата и время', fontsize = 16, fontweight='bold')
    plt.ylabel('Цена', fontsize = 16, fontweight='bold')
    plt.grid(True, linestyle = '--', alpha = 0.5)

    #цвет фона
    fig.patch.set_facecolor('#f0f8ff')

    
    plt.tight_layout()
    plt.show()




if __name__ == "__main__":
    symbol = input("Input symbol: ").upper()
    data = CandlesData(symbol).get_trend_data().head(50)
    depict_candle_graph(data, symbol)





