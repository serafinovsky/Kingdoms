# Kingdoms Game

Многопользовательская браузерная стратегия, построенная на современных веб-технологиях и микросервисной архитектуре.

## 📽️ Демо

https://github.com/serafinovsky/Kingdoms/blob/master/assets/demo.mp4

### Игровой процесс

![Gameplay Demo](./assets/demo.gif)

## 🎮 Особенности

- Многопользовательская игра в реальном времени
- Аутентификация через OAuth2 (Яндекс, Github)
- Коммуникация на основе WebSocket
- Микросервисная архитектура
- Контейнеризация для разработки и продакшена
- Мониторинг через Prometheus и Grafana

## 🏗️ Архитектура

Проект состоит из нескольких микросервисов:

- **Auth Service**: Аутентификация и управление пользователями
- **Cabinet Service**: Управление картами и история
- **Rooms Service**: Игровые комнаты и матчмейкинг
- **Front Service**: Веб-клиент
- **Media Service**: Статические файлы и медиа

## 🛠️ Технологии

- **Backend**:

  - FastAPI (Python)
  - MongoDB
  - PostgreSQL
  - Redis
  - WebSockets

- **Frontend**:

  - SolidJS
  - TypeScript
  - Vite

- **Инфраструктура**:
  - Docker
  - Traefik
  - Prometheus
  - Grafana

## 🚀 Запуск проекта

1. Клонируйте репозиторий:

```bash
export USER_ID=$(id -u)
export GROUP_ID=$(id -g)
git clone https://github.com/serafinovsky/Kingdoms.git
cd Kingdoms
```

2. Создайте файл `.env` с необходимыми переменными окружения:

```bash
cp template.env .env
```

3. Запустите окружение разработки:

```bash
docker compose -f docker-compose.dev.yml -f up -d --build
```

4. Запустите стек мониторинга (опционально):

```bash
docker compose -f docker-compose.monitoring.yml up -d
```

## 📝 Разработка

- Сервер разработки front-end: http://localhost:7000
- Панель управления Traefik: http://localhost:8080
- Grafana: http://localhost:7000/grafana

## 🌟 Планы развития

1. **Боты**:

   - Реализация интерфейса для ботов
   - Добавление игровых ботов

2. **Оптимизация производительности**:

   - Оптимизация объема сообщений WebSocket, использование бинарного протокола, вроде protobuf
   - Рассмотрение возможности перехода на Centrifugo
   - Возможный перенос игрового цикла на Golang

3. **Инфраструктура**:

   - Доработать docker-compose, сделать копирование и установку через pip а не poetry для prod
   - Добавление автоматического тестирования
   - Реализация CI/CD pipeline
