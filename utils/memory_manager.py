#? sqlite3, json and numpy are for the db so we can create json entries and store them in the db
import sqlite3
import json
# numpy for handling arrays for fast retrieval
import numpy as np
# datetime for handling timestamps
# since i will make memories fade over time i need to keep an eye on whe it was created and updated
from datetime import datetime
import ast
# external func
from funcs import faiss_search
from funcs.embedder import Embedder
from funcs.memory_utils import filter_with_fallback, second_level_filtering


#? Hyper Params
threshold = 1.75





class MemoryManager:    
    #* That will initialize the memory manager with a database path
    def __init__(self,db_path="db/memories.db"):        
        # manage db
        self.conn = sqlite3.connect(db_path)
        #* create the database connection and table if it doesn't exist (only should work once)
        self.cursor = self.conn.cursor()
        self._create_table()
        # self.cursor.execute("PRAGMA table_info(memories);")
        
        self.embedder = Embedder()
        ids, vectors = self.load_all_memories()
        self.faiss_engine = faiss_search.FAISS_SEARCH(ids, vectors)
    
    
        
    #* load all memories from the database but only id and embedding for faiss search
    def load_all_memories(self):
        self.cursor.execute('SELECT id, embedding FROM memories')
        results = self.cursor.fetchall()
        ids = []
        vectors = []

        for row in results:
            memory_id, emb_string = row
            embedding = np.array(ast.literal_eval(emb_string), dtype='float32')
            ids.append(memory_id)
            vectors.append(embedding)

        #? convert to numpy arrays for FAISS
        if len(vectors) == 0:
            return np.array([], dtype='int64'), np.empty((0, 384), dtype='float32')
        
        # ? ensure ids are in int64 format and vectors are in float32 format
        return np.array(ids, dtype='int64'), np.vstack(vectors).astype('float32')
        
        
        
        
    #* create the memories table if it doesn't exist
    def _create_table(self):
        #? some SQL code, CREATE will create something TABLE specified what to create, 
        #? IF NOT EXIST so the code only work if no table is there 
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            text TEXT,
            embedding TEXT,
            tokens TEXT,
            weight REAL,
            attachment REAL,
            lifespan INTEGER,
            last_used TEXT
        )
        ''')
        self.conn.commit()
        
        
        
        
        
        
    #* now come the real functions that handle memory
    def add_new_memory(self, text, embedding, tokens, wight=1.0, attachment=1.0, lifespan=3600):
        
        #? more SQL code, INSERT INTO will insert data into the table specified
        self.cursor.execute('''
        INSERT INTO memories (text, embedding, tokens, weight, attachment, lifespan, last_used)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', 
        (text, 
        json.dumps(embedding.tolist()), 
        json.dumps(tokens), wight, 
        attachment, lifespan, 
        datetime.now().isoformat()))
        
        #? commit the changes to the database (i had to debug for a while to figure out that this is needed (0o0))
        self.conn.commit()
        
        
        #? update the loaded on ram data
        last_id = self.cursor.lastrowid
        # Add embedding to FAISS with the ID
        embedding_np = np.array(embedding, dtype='float32')

        # IDs must be numpy array of int64
        ids_np = np.array([last_id], dtype='int64')

        self.faiss_engine.index.add_with_ids(embedding_np, ids_np)
        
        
    def get_all_for_view(self):
        self.cursor.execute("SELECT id, text FROM memories")
        result = self.cursor.fetchall()
        print(result)
        
    #load specific memory by filtering
    def get_memories(self, query ,limit=90):
        # get memories ids
        ids, distances = self.faiss_engine.search(query, limit)
        #? just to not end up debugging the wrong thing if something went wrong in the FAISS
        if ids is None or ids.size == 0:
            raise Exception("IDs array is empty or None")

        filtered_list = filter_with_fallback(ids, distances, threshold)
        if(len(filtered_list) == 0):
            raise Exception("no entries in the filtered list")
        
        
        print(f"filtered ids list is {filtered_list}")
        if len(filtered_list) > 0:
            print(f"Found {len(filtered_list)} IDs for the query: {query}")
        
        
        #? SQL code to select the memories by id
        placeholders = ','.join('?' for _ in filtered_list)
        query = f"SELECT id, text, weight, attachment, lifespan, last_used FROM memories WHERE id IN ({placeholders}) LIMIT {limit}"
        self.cursor.execute(query, tuple(int(i) for i in filtered_list))
        results = self.cursor.fetchall()
        
        second_level_filtered_list = second_level_filtering(results)
        #TODO: filter by relevant and emotional wight before that
        return second_level_filtered_list