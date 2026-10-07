# Dockerfile - Local development and docker-compose
# Same shape as Dockerfile.ci, but takes VITE_* args directly instead of the
# pipeline's REACT_APP_* ones.

# ============================================
# Stage 1: Build
# ============================================
FROM node:22-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci --no-audit --no-fund

COPY . .

# Browser-facing Flask API; the CEVA-MP launch config serves it on the host at :4000.
ARG VITE_API_URL=http://localhost:4000
ARG VITE_ENVIRONMENT=development
ENV VITE_API_URL=${VITE_API_URL}
ENV VITE_ENVIRONMENT=${VITE_ENVIRONMENT}

RUN npm run build

# ============================================
# Stage 2: Production (nginx)
# ============================================
FROM nginx:alpine AS production

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost/healthCheck || exit 1

CMD ["nginx", "-g", "daemon off;"]
