FROM mcr.microsoft.com/playwright:v1.49.0-noble

WORKDIR /app

ENV PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

COPY package*.json ./

RUN npm config set fetch-retry-mintimeout 20000 \
    && npm config set fetch-retry-maxtimeout 120000 \
    && npm install --omit=optional --no-audit --ignore-scripts

COPY playwright.config.js ./
COPY tests ./tests

CMD ["npx", "playwright", "test", "tests/test.spec.js"]