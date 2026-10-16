# ---- stage 1: build the static React bundle with Node ----
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# ---- stage 2: serve it with unprivileged Nginx (runs as uid 101, port 8080) ----
FROM nginxinc/nginx-unprivileged:1.29-alpine AS runtime
USER root
RUN apk upgrade --no-cache
USER 101
# Where /api/* is proxied. Docker Compose uses the "backend" service; Helm overrides it.
ENV BACKEND_URL=http://backend:8000
COPY nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 8080
HEALTHCHECK --interval=15s --timeout=3s --retries=3 CMD wget -q -O /dev/null http://127.0.0.1:8080/healthz || exit 1
