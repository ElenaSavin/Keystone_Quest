# bin/bash
id=$1
docker container stop $id
docker container rm $id
docker build . -t keystone
docker run -d --name keystone keystone:latest
docker exec -ti keystone /bin/bash

#python src/main.py -f files --filename 7dfcbe11-6933-4363-b1fd-8c8e1258b85