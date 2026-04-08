# ElevatorSimulator
Elevator SCAN Algorithm Simulator. A Python/Tkinter application that visualizes the SCAN (elevator) disk scheduling algorithm adapted for passenger elevator control. Features real-time cabin animation, external/internal request handling, and finite state machine (FSM) logic for doors and movement.

# Симулятор лифта с алгоритмом SCAN

Программный продукт разработан в рамках проектного практикума (Стадия 6). Реализует алгоритм обслуживания запросов лифта SCAN ("Лифт") с графической визуализацией на базе библиотеки Tkinter.

## 1. Системные требования

| Компонент | Требование |
| :--- | :--- |
| **ОС** | Windows 7/10/11, Linux (Ubuntu 20.04+), macOS |
| **Python** | Версия 3.8 или выше |
| **Дисплей** | Минимальное разрешение 800x600 |
| **Память** | Не менее 50 МБ свободной оперативной памяти |

## 2. Инструкция по установке и запуску

### Шаг 1. Установка Python
Убедитесь, что на компьютере установлен Python. Откройте терминал (командную строку) и выполните:
```bash
python --version
```

Если Python не установлен, скачайте его с официального сайта и при установке обязательно поставьте галочку "Add Python to PATH".

### Шаг 2. Копирование исходного кода
Склонируйте репозиторий или скачайте архив с кодом.

Распакуйте архив в папку C:\ElevatorSimulator (или любую другую удобную директорию).

### Шаг 3. Запуск приложения
Библиотека Tkinter входит в стандартную поставку Python для Windows и macOS. Установка дополнительных зависимостей не требуется.

Откройте терминал в папке src.

Выполните команду:

```bash
python main.py
```

### Шаг 4. Устранение неполадок (Linux)
Если вы используете Linux (Ubuntu/Debian) и видите ошибку ModuleNotFoundError: No module named 'tkinter', установите пакет tkinter вручную командой:

```bash
sudo apt-get install python3-tk
```

## 3. Состав дистрибутива
src/main.py — Исходный код программы.

docs/ — Эксплуатационная документация по ГОСТ Р 59795-2021.

screenshots/ — Иллюстрации работы интерфейса.
