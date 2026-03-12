import os
import tempfile
import requests
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()

TOPICS = [
    "Large language model",
    "Data engineering",
    "Vector database",
    "Retrieval-augmented generation",
]

# wikipedia blocks the default python user-agent, need to set a real one
session = requests.Session()
session.headers["User-Agent"] = "LLMPipelineBot/1.0 (https://github.com/yourusername; your.email@example.com)"

WIKI_URL = "https://en.wikipedia.org/w/api.php"


def get_wiki_intro(topic):
    """Hit the wikipedia API and pull back the intro section as plain text."""
    resp = session.get(WIKI_URL, params={
        "action": "query",
        "prop": "extracts",
        "exintro": "",
        "explaintext": "",
        "titles": topic,
        "format": "json",
    }, timeout=15)
    resp.raise_for_status()

    pages = resp.json()["query"]["pages"]
    page = next(iter(pages.values()))

    if page.get("missing") is not None:
        return None
    return page.get("extract", "")


def stage_files(temp_dir):
    """PUT the txt files from temp_dir into snowflake internal stage."""
    conn = snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        private_key_file=os.getenv("SNOWFLAKE_KEY_PATH"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        role=os.getenv("SNOWFLAKE_ROLE"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
    )
    cursor = None
    try:
        cursor = conn.cursor()
        # snowflake wants forward slashes even on windows
        path = temp_dir.replace("\\", "/")
        cursor.execute(f"""
            PUT file://{path}/*.txt
            @raw_text_stage
            AUTO_COMPRESS=FALSE
            OVERWRITE=TRUE
        """)
        print("Staged files in raw_text_stage.")
    finally:
        if cursor:
            cursor.close()
        conn.close()


def main():
    print("Fetching Wikipedia extracts...\n")

    with tempfile.TemporaryDirectory() as tmp:
        saved = []

        for topic in TOPICS:
            try:
                text = get_wiki_intro(topic)
            except requests.RequestException as e:
                print(f"  Skipped '{topic}' -- {e}")
                continue

            if not text:
                print(f"  Skipped '{topic}' -- not found")
                continue

            fname = topic.replace(" ", "_") + ".txt"
            with open(os.path.join(tmp, fname), "w", encoding="utf-8") as f:
                f.write(text)

            saved.append(fname)
            print(f"  Saved {fname}")

        if not saved:
            print("\nNothing downloaded, skipping upload.")
            return

        print(f"\nUploading {len(saved)} file(s) to Snowflake...")
        stage_files(tmp)

    print("Done. Temp files cleaned up.")


if __name__ == "__main__":
    main()