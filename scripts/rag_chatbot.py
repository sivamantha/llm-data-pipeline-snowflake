import os
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()


def connect():
    """Quick helper to grab a Snowflake connection."""
    return snowflake.connector.connect(
        user=os.getenv('SNOWFLAKE_USER'),
        private_key_file=os.getenv('SNOWFLAKE_KEY_PATH'),
        account=os.getenv('SNOWFLAKE_ACCOUNT'),
        role=os.getenv('SNOWFLAKE_ROLE'),
        warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
        database=os.getenv('SNOWFLAKE_DATABASE'),
        schema='GOLD'
    )


def ask(question):
    """Runs a RAG query — finds relevant chunks via vector search, then feeds them to the LLM."""
    conn = connect()

    try:
        cur = conn.cursor()

        # find the top 3 most relevant chunks using cosine similarity
        cur.execute("""
            WITH user_embedding AS (
                SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_768('snowflake-arctic-embed-m', %s) AS vec
            ),
            matches AS (
                SELECT
                    chunk_text,
                    VECTOR_COSINE_SIMILARITY(
                        chunk_embedding,
                        (SELECT vec FROM user_embedding)
                    ) AS score
                FROM llm_pipeline_dev.gold.fct_wikipedia_embeddings
                ORDER BY score DESC
                LIMIT 3
            )
            SELECT chunk_text FROM matches;
        """, (question,))

        rows = cur.fetchall()
        if not rows:
            return "Couldn't find anything relevant in the database."

        context = "\n\n".join(row[0] for row in rows)

        # pass the context + question to the LLM and let it do its thing
        prompt = f"""You are a helpful AI data assistant. Answer the user's question
strictly using the Context provided below. If the answer is not in the Context,
say "I don't know based on the provided data."

Context:
{context}

Question: {question}"""

        cur.execute("SELECT SNOWFLAKE.CORTEX.COMPLETE('llama3-8b', %s);", (prompt,))
        return cur.fetchone()[0]

    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("Welcome to the RAG demo — type 'exit' to quit")
    print("=" * 50 + "\n")

    while True:
        q = input("Ask a question: ").strip()
        if q.lower() in ('exit', 'quit'):
            print("Done. See ya.")
            break

        print("\nSearching + generating...\n")
        print(f"AI: {ask(q)}\n")
        print("-" * 50)