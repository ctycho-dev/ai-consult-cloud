FROM node:22-alpine3.19 as node

WORKDIR /app

COPY package*.json ./

COPY . /app

RUN yarn && yarn build

FROM scratch
COPY --from=node /app/dist /
