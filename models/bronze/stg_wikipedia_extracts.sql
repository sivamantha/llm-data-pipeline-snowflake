{{ config(
    materialized='table',
    tags=['bronze', 'ingestion']
) }}

WITH
    raw_stage AS (
        SELECT
            METADATA$FILENAME AS file_name,
            METADATA$FILE_ROW_NUMBER AS row_number,
            $1 AS raw_text,
            CURRENT_TIMESTAMP() AS ingestion_timestamp
        FROM
            @llm_pipeline_dev.bronze.raw_text_stage
    )

SELECT
REPLACE (
        REPLACE (file_name, '.txt', ''),
            '_',
            ' '
    ) AS topic_name,
    raw_text,
    ingestion_timestamp
FROM raw_stage
WHERE
    raw_text IS NOT NULL
    AND TRIM(raw_text) != ''