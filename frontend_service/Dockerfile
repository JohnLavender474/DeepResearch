FROM node:20-alpine AS dev

WORKDIR /app

COPY package.json ./

RUN npm install

COPY . .

EXPOSE 5173

CMD ["sh", "-c", "npm install --no-audit --no-fund && npm run dev -- --host"]