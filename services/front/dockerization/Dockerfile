# Используем Node.js как базовый образ
FROM node:20.18.1-alpine3.21

# RUN addgroup -g 1000 appgroup && \
#     adduser -u 1000 -G appgroup -s /bin/sh -D appuser

# Устанавливаем рабочую директорию
# WORKDIR /opt/projects/front
# # Копируем package.json и package-lock.json
# COPY package.json package-lock.json ./
# # 
# # USER node

# # Устанавливаем зависимости
# RUN npm install 
# RUN chown -R node:node /opt/projects/front
# USER node

# COPY . .


# CMD ["tail", "-f", "/dev/null"]

# Копируем весь проект
# COPY . .

# Открываем порт для дев-сервера
# EXPOSE 3000

# CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
# Этап 2: Финальный образ
# FROM python:3.11.11-slim

# WORKDIR /app
# COPY --from=builder /app/.venv/ /opt/poetry
# COPY src/ /app

# CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8888"]
# CMD ["tail", "-f", "/dev/null"]