from receive_bybit import CandlesData
import matplotlib.pyplot as plt
import pandas as pd
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from matplotlib import  font_manager as fm, rcParams

def depict_candle_graph(data, symbol="BTCUSDT"):
    #преобразование в формат матплотлиба
    data['datetime'] = data['datetime'].map(mdates.date2num)

    #выбор только нужных столбцов
    data_ohlc = data[['datetime','open', 'high', 'low', 'close']]
    data_ohlc = data_ohlc.astype(float)
    print(data_ohlc)

    #шрифт

    '''
    github_url = 'https://github.com/google/fonts/blob/main/apache/robotoslab/RobotoSlab%5Bwght%5D.ttf'
    font_url = github_url + '?raw=true'
    response = requests.get(font_url)
    with open('temp.ttf', 'wb') as f:
        f.write(response.content)
    f.close()
    '''
    prop = fm.FontProperties(fname='../fonts/Arimo-VariableFont_wght.ttf')
    #создание фигуры
    fig, ax = plt.subplots(figsize=(15, 7))
    ax.set_facecolor('#101014')

    #рисование свечей
    candlestick_ohlc(ax, data_ohlc.values, width = 0.6, colorup = '#20b26c', colordown = '#ef454a')


    #настройки осей
    ax.xaxis_date()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    plt.xticks(rotation = 0, color = '#737376')
    plt.yticks(rotation = 0, color = '#737376')
    for tick in ax.get_xticklabels():
        tick.set_fontproperties(prop)
    for tick in ax.get_yticklabels():
        tick.set_fontproperties(prop)

    #количество отметок по оси y
    ax.yaxis.set_major_locator(mticker.MaxNLocator(nbins=12))

    #настрока пределов по оси x
    max_date = data_ohlc['datetime'].max()
    min_date = data_ohlc['datetime'].min()
    delta = max_date - min_date
    ax.set_xlim(min_date, max_date + delta)

    #заголовки и сетка
    plt.title(symbol, fontsize = 24, fontweight='bold', color = '#737376', fontproperties = prop)
    plt.xlabel('Date and time', fontsize = 14, fontweight='bold', color = '#737376', fontproperties = prop)
    plt.ylabel('Price', fontsize = 14, fontweight='bold', color = '#737376', fontproperties = prop)
    plt.grid(True, alpha=0.2, color='#202124', linewidth=2)
    for spine in ax.spines.values():
        spine.set_color('#71757a')
        spine.set_linewidth(1)


    #цвет фона
    fig.patch.set_facecolor('#101014')


    plt.tight_layout()
    plt.show()




if __name__ == "__main__":
    symbol = input("Input symbol: ").upper()
    data = CandlesData(symbol).get_trend_data().head(50)
    depict_candle_graph(data, symbol)





