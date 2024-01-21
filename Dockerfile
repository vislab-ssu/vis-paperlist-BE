FROM node:20.9.0

WORKDIR /app

COPY package.json /app/
COPY yarn.lock /app/
RUN yarn install

COPY . /app

ENV PORT=3000
ENV DB_HOST=paperlist-db
ENV DB_USER=root
ENV DB_PASSWORD=VIS4every1
ENV DB_DB=vis
ENV DB_PORT=3306

EXPOSE 3000

CMD ["yarn", "start"]
