# stdio proxy to the hosted JOY Automart MCP server (https://www.joyautomart.com/mcp)
FROM node:22-alpine
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev
COPY bin ./bin
ENTRYPOINT ["node", "bin/joyautomart-mcp.js"]
