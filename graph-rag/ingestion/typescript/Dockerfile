FROM node:22-alpine AS build

WORKDIR /app
COPY package.json tsconfig.json tsconfig.build.json ./
RUN npm install
COPY src ./src
RUN npm run build

FROM node:22-alpine
WORKDIR /app
COPY --from=build /app/package.json ./
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/dist ./dist
ENTRYPOINT ["node", "dist/src/cli.js"]
