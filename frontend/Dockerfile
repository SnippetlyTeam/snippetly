## Multistage Dockerfile for both development (Vite dev server) and production (Nginx)

# --- base deps stage ---
FROM node:20-alpine AS base
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .

# --- development stage ---
FROM base AS dev
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# --- build stage ---
FROM base AS build
RUN npm run build

# --- production runtime (Nginx) ---
FROM nginx:1.27-alpine AS prod
WORKDIR /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist .
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]