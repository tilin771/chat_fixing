set -Eeuo pipefail

log() { echo "[$(date +'%F %T%z')] $*"; }

export PATH="/usr/local/bin:/usr/bin:/bin:${PATH}"

cd "$(dirname "$0")/.."

if [[ -f "DockerVars.env" ]]; then
  log "Sourcing DockerVars.env"
  set -a
  . "./DockerVars.env"
  set +a
fi


command -v docker-compose >/dev/null 2>&1 || { log "ERROR: docker-compose not found in PATH"; exit 127; }

docker network create proxy >/dev/null 2>&1 || true

log "Pulling images via docker-compose…"
docker-compose pull

log "Starting services (detached)…"
docker-compose up -d

docker image prune -f >/dev/null 2>&1 || true

log "Containers running:"
docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}'
