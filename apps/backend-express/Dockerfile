FROM node:18-alpine

WORKDIR /workspace

# Copy root configurations and package dependencies
COPY package*.json ./
COPY tsconfig.base.json ./
COPY nx.json ./
COPY apps/backend-express/package*.json ./apps/backend-express/

# Install workspace dependencies
RUN npm ci

# Copy application files and shared packages
COPY apps/backend-express/ ./apps/backend-express/
COPY libs/ ./libs/

# Run build step via Nx
RUN npm run build --workspace=apps/backend-express

WORKDIR /workspace/apps/backend-express

EXPOSE 8000

CMD ["node", "dist/app.js"]
