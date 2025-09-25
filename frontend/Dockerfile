FROM node:20-alpine

WORKDIR /app

# Копіюємо package файли і ставимо залежності
COPY package*.json ./
RUN npm ci

# Копіюємо весь код і запускаємо dev сервер
COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host"]