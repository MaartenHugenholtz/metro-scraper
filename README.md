### Build Docker image

`docker build -t metro-api .`

### Run container

`docker run -p 8000:8000 metro-api`

### Test API

Open your browser or use curl:

http://localhost:8000/departures


# TODO 
- Limit memory usage
- Deploy on render and test