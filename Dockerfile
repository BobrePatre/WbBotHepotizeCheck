# Используем официальный образ Python 3.9
FROM python:3.12

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл зависимостей в контейнер
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install requests~=2.32.3
RUN pip install pymongo~=4.7.3
RUN pip install python-dotenv~=1.0.1
RUN pip install openpyxl~=3.1.4
RUN pip install aiogram~=3.8.0



# Копируем все файлы из текущей директории в рабочую директорию контейнера
COPY . .

# Указываем команду для запуска бота
CMD ["python", "main.py"]
