FROM mcr.microsoft.com/playwright:v1.48.0-noble

WORKDIR /app

COPY package*.json ./
RUN npm ci || npm install

COPY . .

CMD ["npx", "playwright", "test"]
