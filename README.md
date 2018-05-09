# naccs-api


### build

```
docker build -t naccs-api .
```

### run

interactive
```
docker run -it -p 8888:3000 --name naccs-api --rm naccs-api
```

daemon
```
docker run -d -p 8888:3000 --name naccs-api --rm naccs-api
```
