# MaxClack

Clack to the max!

## Running on Docker

### Requirements

Install docker.
https://www.docker.com/get-started/

### Creating docker images

To build the frontend and backend images for development, use

```bash
docker build -t maxclack-backend ./MaxClack-backend
docker build -t maxclack-frontend ./MaxClack-frontend
```

These will create docker images on your local machine, named maxclack-backend and maxclack-frontend.

### Running docker images

By default, Flask runs on port 5000 and
Vue.js runs on port 5173, so to create containers using the images
and map the ports to local host, run the commands:

```bash
docker run -p 5000:5000 maxclack-backend
docker run -p 5173:5173 maxclack-frontend
```

Each of these will create a container using an image created in the previous step.
