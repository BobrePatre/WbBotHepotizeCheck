# Используем официальный образ Python 3.9
FROM python:3.12

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл зависимостей в контейнер
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.python.org/simple/


# Копируем все файлы из текущей директории в рабочую директорию контейнера
COPY . .

# Указываем команду для запуска бота
CMD ["python", "main.py"]
