docker stop paperlist-be-container
docker rm paperlist-be-container
docker run --name=paperlist-be-container -d -p 3333:3000 paperlist-be
