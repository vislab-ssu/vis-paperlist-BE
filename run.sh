docker build -t paperlist-be .
docker run --name=paperlist-be-container -d -p 3333:3000 paperlist-be
