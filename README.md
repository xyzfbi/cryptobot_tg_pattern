
---

# cryptobot_tg_pattern

[![GitHub](https://img.shields.io/github/license/xyzfbi/cryptobot_tg_pattern)](https://github.com/xyzfbi/cryptobot_tg_pattern)
[![GitHub last commit](https://img.shields.io/github/last-commit/xyzfbi/cryptobot_tg_pattern)](https://github.com/xyzfbi/cryptobot_tg_pattern/commits/main)
[![GitHub stars](https://img.shields.io/github/stars/xyzfbi/cryptobot_tg_pattern?style=social)](https://github.com/xyzfbi/cryptobot_tg_pattern)

Телеграм-бот для анализа криптовалютных паттернов и генерации торговых сигналов. Разработан для проекта MIEM HSE.

- **Репозиторий:** [xyzfbi/cryptobot_tg_pattern](https://github.com/xyzfbi/cryptobot_tg_pattern)

## Возможности

- 📈 Получение данных с ByBit
- 📊 Расчет технических индикаторов
- 🔎 Распознавание графических паттернов
- 📉 Анализ тренда и генерация торговых сигналов
- 🖼️ Визуализация паттернов
- 🤖 Интерактивный Telegram-бот с клавиатурами
- 🐍 Ядро на Python, поддержка скриптов для Linux и Windows

## Быстрый старт

### Требования
- Anaconda
- Python 3.8+
- Telegram API ключи

### Установка и запуск

1. Установите Anaconda.
2. Создайте окружение из файла:
   ```bash
   conda env create -f environment.yml
   ```
3. Активируйте окружение:
   ```bash
   conda activate cryptobot_tg
   ```
4. (Опционально) Обновите зависимости:
   ```bash
   conda install <новый_пакет>
   conda remove <старый_пакет>
   ```
5. Запустите бота:
   ```bash
   python main.py
   ```

## Структура проекта

```
cryptobot_tg_pattern/
├── environment.yml        # Conda environment spec
├── .env                  # API ключи
├── .gitignore            # Игнорируемые файлы
├── fonts/                # Шрифты для графиков
│   └── Arimo-VariableFont_wght.ttf
├── scripts to run/       # Скрипты для запуска
│   ├── linux.sh          # Запуск под Linux
│   └── windows.bat       # Запуск под Windows
├── src/                  # Ядро анализа
│   ├── receive_bybit.py        # Получение данных с ByBit
│   ├── calculate_indicators.py # Расчет индикаторов
│   ├── find_patterns.py        # Распознавание паттернов
│   ├── find_trend.py           # Анализ тренда
│   ├── patterns_config.py      # Параметры паттернов
│   └── data_to_jpg.py          # Визуализация
├── tgbot/                # Telegram-бот
│   ├── handler.py         # Обработчик сообщений
│   └── keyboard.py        # Клавиатуры
├── main.py               # Точка входа
```

## Запуск

- Для запуска используйте:
  ```bash
  python main.py
  ```
- Для запуска под Linux/Windows используйте скрипты из папки `scripts to run/`.

## Вклад

Pull requests и предложения приветствуются! Открывайте issues для обсуждения новых идей или багов.

## Лицензия

Проект распространяется под лицензией MIT.

## Авторы

- [xyzfbi](https://github.com/xyzfbi)

## FAQ

**Q: Для чего нужен этот бот?**  
A: Для автоматизации анализа криптовалютных рынков и генерации торговых сигналов на основе паттернов.

**Q: Как добавить новый источник данных?**  
A: Реализуйте модуль в папке `src/` и подключите его в основной логике.

**Q: Как изменить параметры паттернов?**  
A: Измените файл `src/patterns_config.py`.

**Q: Как запустить на Windows?**  
A: Используйте скрипт `scripts to run/windows.bat`.

**Q: Как обновить зависимости?**  
A: Используйте команды conda:
   ```bash
   conda install <пакет>
   conda remove <пакет>
   conda env export --no-builds > environment.yml
   ```

---

_Оригинальный репозиторий: [https://github.com/xyzfbi/cryptobot_tg_pattern](https://github.com/xyzfbi/cryptobot_tg_pattern)_
