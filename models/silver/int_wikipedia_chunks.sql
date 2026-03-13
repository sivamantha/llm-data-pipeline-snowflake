{{ config( materialized='view', tags=['silver'] ) }}

WITH bronze_data AS (
    SELECT * FROM {{ ref('stg_wikipedia_extracts') }}
)

SELECT
    topic_name,
    raw_text AS chunk_text,
    ARRAY_SIZE (SPLIT (raw_text, ' ')) AS approximate_word_count,
    ingestion_timestamp
FROM bronze_data
WHERE
    raw_text IS NOT NULL
    AND ARRAY_SIZE (SPLIT (raw_text, ' ')) > 7