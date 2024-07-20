# ./chromadb_init.sh up
./ollama_init.sh up
cd aelfgpt
cp example.env .env
pip install -r requirements.txt
python resources/utils/rag_populate_db.py
chainlit run src/app.py -hw
