# Лабораторная работа №2 - Docker

**Тема:** Контейнеризация приложений\
**Студент:** Шамшетов Арыслан Жаксыбаевич\
**Группа:** М8О-106БВ-25\
**Преподаватель:** Блинов Максим


# Docker инструкции для мини-оболочки

## Быстрый старт

### Способ 1: Запуск из Docker Hub
```
docker pull shamshetov2007/dev1lan-shell:1.0.0
docker run -it shamshetov2007/dev1lan-shell:1.0.0
```

### Способ 2: Сборка из исходного кода
```
# Клонировать репозиторий
git clone https://gitlab.mai.ru/idt-lw/m8o-106bv-25/personal/azshamshetov/shamshetov_a_m8o-106bv-25_lab_2#
cd python-lab-2-docker

# Собрать образ
docker build -t dev1lan-shell:1.0.0 .

# Запустить
docker run -it dev1lan-shell:1.0.0
```

## Подробные инструкции
### Сборка образа
```
# Базовая сборка
docker build -t dev1lan-shell:1.0.0 .

# Сборка с другим именем
docker build -t my-shell:latest .

# Сборка без кэша
docker build --no-cache -t dev1lan-shell:1.0.0 .
```
### Запуск контейнера
```
# Базовый запуск
docker run -it dev1lan-shell:1.0.0

# Запуск с монтированием текущей директории
docker run -it -v $(pwd):/data dev1lan-shell:1.0.0

# Запуск в фоновом режиме
docker run -d --name my-shell dev1lan-shell:1.0.0

# Запуск с пробросом портов (если нужно)
docker run -it -p 8080:80 dev1lan-shell:1.0.0
```
### Работа с контейнерами
```
# Посмотреть запущенные контейнеры
docker ps

# Посмотреть все контейнеры
docker ps -a

# Остановить контейнер
docker stop my-shell

# Запустить остановленный контейнер
docker start my-shell

# Удалить контейнер
docker rm my-shell
```
### Работа с образами
```
# Посмотреть образы
docker images

# Скачать образ из Docker Hub
docker pull shamshetov2007/dev1lan-shell:1.0.0

# Загрузить образ на Docker Hub
docker push shamshetov2007/dev1lan-shell:1.0.0

# Удалить образ
docker rmi dev1lan-shell:1.0.0
```

## Проверка работоспособности
### Тестовые команды
После запуска контейнера выполните:

```
dev-1-lan:/data₽ ls -l
dev-1-lan:/data₽ cd /app/src
dev-1-lan:/app/src₽ ls -l
dev-1-lan:/app/src₽ cat main.py
dev-1-lan:/app/src₽ exit
```
### Проверка с монтированием
```
# Запуск с монтированием
docker run -it -v $(pwd):/data dev1lan-shell:1.0.0

# Внутри контейнера проверяем доступ к файлам
dev-1-lan:/data₽ ls -l
dev-1-lan:/data₽ cat README.md
```
## Информация об образе
### Характеристики

- Базовый образ: python:3.11-slim
- Размер: ~600MB
- Точка входа: python /app/src/main.py



### Структура внутри контейнера

```
PV_LABA_2/
├── src/
│   ├── main.py                 # Главный файл приложения
│   ├── commands/               # Модули команд
│   │   ├── cat.py              # Команда cat
│   │   ├── cd.py               # Команда cd
│   │   ├── cp.py               # Команда cp
│   │   ├── ls.py               # Команда ls
│   │   ├── mv.py               # Команда mv
│   │   ├── rm.py               # Команда rm
│   │   ├── zip_tar.py          # Команды работы с архивами
│   │   └── __init__.py         # Инициализация пакета команд
│   └── core/                   # Основные модули
│       ├── parser.py           # Парсер команд
│       ├── path_utils.py       # Утилиты для работы с путями
│       ├── logger.py           # Система логирования
│       └── __init__.py         # Инициализация пакета core
├── tests/                      # Юнит-тесты
│ ├── __init__.py               # Инициализация пакета тестов
│ └── test.py                   # Тесты (31 шт)
├── Dockerfile                  # Конфигурация Docker образа
├── .dockerignore               # Исключения для сборки
├── shell.log                   # Файл логов (создается автоматически)
├── pyproject.toml              # Конфигурация проекта
├── uv.lock                     # Файл зависимостей
├── requirements.txt            # Cписок всех необходимых библиотек и их версий
└── README.md                   # Документация
```
## Устранение проблем
Контейнер сразу завершается
```
# Посмотреть логи
docker logs [CONTAINER_ID]

# Запустить с интерактивной оболочкой для отладки
docker run -it --entrypoint /bin/bash dev1lan-shell:1.0.0
```
##Проблемы с монтированием
```
# Проверить правильность путей
docker run -it -v $(pwd):/data dev1lan-shell:1.0.0

# Монтирование только для чтения
docker run -it -v $(pwd):/data:ro dev1lan-shell:1.0.0
```
## Очистка Docker
```
# Удалить все остановленные контейнеры
docker container prune

# Удалить неиспользуемые образы
docker image prune

# Полная очистка
docker system prune
```
# Ссылки
- Docker Hub: https://hub.docker.com/r/shamshetov2007/dev1lan-shell
- Исходный код: [https://gitlab.mai.ru/idt-lw/m8o-106bv-25/personal/azshamshetov/shamshetov_a_m8o-106bv-25_lab_2#]
