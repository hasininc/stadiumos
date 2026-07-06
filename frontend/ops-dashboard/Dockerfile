FROM node:18-alpine AS builder

WORKDIR /workspace

COPY package*.json ./
COPY tsconfig.json ./
COPY eslint.config.js ./
COPY frontend/ops-dashboard/package*.json ./frontend/ops-dashboard/

RUN npm ci

COPY frontend/ops-dashboard/ ./frontend/ops-dashboard/
COPY shared/ ./shared/

RUN npm run build --prefix=frontend/ops-dashboard

FROM nginx:1.23-alpine

COPY --from=builder /workspace/frontend/ops-dashboard/dist /usr/share/nginx/html
COPY frontend/ops-dashboard/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
