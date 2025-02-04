FROM node:20.18.3-alpine3.20 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:stable-alpine3.20
COPY --from=builder /app/dist /usr/share/nginx/html