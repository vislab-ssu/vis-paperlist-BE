FROM node:20.9.0

WORKDIR /app

COPY package.json /app/
COPY yarn.lock /app/
RUN yarn install

COPY . /app

# INPUT ENV HERE
# DOCKER_ENV IS WRITTEN IN GITHUB CODESPACE SECRETS

EXPOSE 3000

CMD ["yarn", "start"]
