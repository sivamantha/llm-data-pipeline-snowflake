{{ config( materialized='table', tags=['gold', 'core'] ) }}

WITH silver_chunks AS (
    SELECT * FROM {{ ref('int_wikipedia_chunks') }}
)

SELECT topic_name, chunk_text, approximate_word_count,

-- 🧠 The AI Engine: Calling Snowflake Cortex to turn text into a 768-dimension vector
SNOWFLAKE.CORTEX.EMBED_TEXT_768 (
    'snowflake-arctic-embed-m',
    chunk_text
) AS chunk_embedding,
ingestion_timestamp
FROM silver_chunks