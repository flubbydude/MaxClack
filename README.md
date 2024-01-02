# MaxClack

Clack to the max!

## Running on Docker

### Requirements

Install docker.
https://www.docker.com/get-started/

### Running using `docker compose`

Spin up frontend, backend, and database using `docker compose up`. This command will print out the logs from all the containers, and when this command is cancelled (using `control + c`) will destroy all the containers.

In order run the containers in the background, use:

```sh
docker compose up -d
```

You can destroy the containers later using

```sh
docker compose down
```

To view the logs of the containers, use

```sh
docker compose logs
```

To view the logs of the containers as a stream, use the `-f` option to "follow" the logs.

### Hot reloading using `docker compose`

In order to hot reload, the command `docker compose watch` must be running while the containers are running.
You can run `docker compose watch`, which basically runs `docker compose up --build` to rebuild the containers and then
starts watching your files and syncing your files with the containers'.

If you want to view logs while hot reloading, do one of the following:

#### Option 1 (detached containers)

Make 2 shells, the first watches (basically runs `docker compose up --build -d` and then watches):

```sh
docker compose watch
```

The second prints logs:

```sh
docker compose logs -f
```

When done, spin down the containers using:

```sh
docker compose down
```

#### Option 2 (non-detached containers)

Or, make 2 shells, the first runs the containers and prints logs:

```sh
docker compose up
```

The second watches:

```sh
docker compose watch
```

When the `docker compose up` program is cancelled, the containers will be deleted.
