# Docker & Docker Compose Cheatsheet

Quick reference for essential Docker commands.

---

## Containers

```bash
# Lifecycle
docker run -d --name myapp -p 8080:80 nginx:alpine # Run detached with port mapping
docker ps                                          # List running containers
docker ps -a                                       # List all containers
docker stop <container>                            # Stop running container
docker start <container>                           # Start stopped container
docker restart <container>                         # Restart container
docker rm <container>                              # Delete container
docker rm -f $(docker ps -aq)                      # Delete all containers

# Execution & Logs
docker logs -f --tail 100 <container>              # Follow logs (last 100 lines)
docker exec -it <container> /bin/sh                # Interactive shell inside container
docker inspect <container>                         # Inspect low-level details
docker stats                                       # Live stream resource usage
```

---

## Images

```bash
docker build -t myapp:1.0 .                       # Build image from Dockerfile
docker images                                      # List local images
docker rmi <image>                                 # Delete image
docker image prune -a                              # Remove all unused images
docker tag myapp:1.0 registry.example.com/myapp:1.0 # Tag for registry
docker push registry.example.com/myapp:1.0         # Push image to registry
```

---

## Volumes & Networks

```bash
# Volumes
docker volume create my-data                       # Create volume
docker volume ls                                   # List volumes
docker volume rm my-data                           # Delete volume

# Networks
docker network create my-net                       # Create bridge network
docker network ls                                  # List networks
docker network connect my-net <container>          # Connect container to network
```

---

## Docker Compose

```bash
docker compose up -d                               # Start services in background
docker compose ps                                  # Status of services
docker compose logs -f <service>                   # Follow service logs
docker compose exec <service> sh                   # Shell inside service container
docker compose down                                # Stop and remove resources
docker compose down -v                             # Stop and delete volumes
```

---

[← Back to Cheatsheets](README.md)
