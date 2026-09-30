FROM mcr.microsoft.com/playwright:v1.49.0-noble

WORKDIR /app

COPY package*.json ./

# Uses npm ci if package-lock.json exists, otherwise falls back to npm install
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi

COPY . .

CMD ["npx", "playwright", "test"]
