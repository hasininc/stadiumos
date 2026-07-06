FROM node:18-alpine

WORKDIR /workspace

COPY package*.json ./
COPY tsconfig.json ./
COPY backend/express-service/package*.json ./backend/express-service/

RUN npm ci

COPY backend/express-service/ ./backend/express-service/
COPY shared/ ./shared/

RUN npm run build --prefix=backend/express-service

WORKDIR /workspace/backend/express-service

EXPOSE 8000

CMD ["node", "dist/app.js"]
