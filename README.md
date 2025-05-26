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
├── environment.yml
├── fonts/
│   └── Arimo-VariableFont_wght.ttf
├── README.md
├── src/
│   ├── calculate_indicators.py
│   ├── data_to_jpg.py
│   ├── find_patterns.py
│   ├── find_trend.py
│   ├── patterns_config.py
│   └── receive_bybit.py
└── tgbot/
    ├── buf.png
    ├── handler.py
    ├── keyboard.py
    ├── main.py
    └── rm_commands.py
```

---
