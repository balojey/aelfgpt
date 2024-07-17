cd chromadb
if [ ! -d "chroma" ]; then
  git clone https://github.com/chroma-core/chroma.git
fi
cd -
docker compose -f chromadb/docker-compose.yml up -d --build
