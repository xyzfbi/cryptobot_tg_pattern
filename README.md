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
