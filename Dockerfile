FROM node:20.9.0

WORKDIR /app

# Node Packages
COPY package.json /app/
COPY yarn.lock /app/
RUN yarn install

# Python and Python Packages
RUN apt-get update && apt-get install --yes python3 python3-pip
COPY Word2VecRequirements.txt /app/
RUN pip3 install -r Word2VecRequirements.txt --break-system-packages
RUN python3 -m nltk.downloader punkt stopwords

# Copy codes and build
COPY . /app
RUN yarn build

EXPOSE 3000

CMD ["yarn", "start:prod"]
