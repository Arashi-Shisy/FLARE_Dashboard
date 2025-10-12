# Build stage
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json /app/package.json
RUN npm install
COPY . /app
RUN npm run build

# Serve stage
FROM nginx:stable-alpine
# ★ Nginx設定を差し替え
COPY nginx.conf /etc/nginx/nginx.conf
# ビルド成果物を配置
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
