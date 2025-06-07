## Инструкция по установке

1. ### Установите [Anaconda](https://www.anaconda.com/download). 
2. ### Создайте окружение из файла:
   ```bash
   conda env create -f environment.yml
   ```
3. ### Активируйте его: 
    ```
    conda activate cryptobot_tg
    ```

4. ### Обновите зависимости (если нужно):

``
conda install новый_пакет
``

``
conda remove старый_пакет
``

5. ### Пересоздайте environment.yml
```
conda env export --no-builds > environment.yml
```
# cryptobot_tg_pattern

## Структура проекта

```
cryptobot_tg_pattern/
├── environment.yml        # Conda environment spec
├── .env                   # API ключи
├── .gitignore             # Игнорируемые файлы
├── fonts/                 # Шрифты для графиков
│   └── Arimo-VariableFont_wght.ttf
├── scripts to run/                 # промежуточные скрипты для установки
│   ├── linux.sh           # Промежуточный скрипт запуск Linux
│   └── windows.bat   # Промежуточный скрипт запуск Windows
├── src/                   # Ядро анализа
│   ├── receive_bybit.py     # Получение данных с ByBit
│   ├── calculate_indicators.py # Расчет технических индикаторов
│   ├── find_patterns.py      # Распознавание паттернов
│   ├── find_trend.py         # Анализ тренда и генерация сигнала
│   ├── patterns_config.py    # Параметры паттернов
│   └── data_to_jpg.py        # Визуализация паттернов
├── tgbot/                 # Telegram-бот
│   ├── handler.py           # Обработчик сообщений
│   └── keyboard.py          # Интерактивные клавиатуры
├── main.py                # Точка входа
```

---
