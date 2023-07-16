from datetime import datetime
import os
import sys
import sqlite3
import argparse
from tqdm import tqdm
import re
from telethon.sync import TelegramClient
from dotenv import load_dotenv

__version__ = "0.1"


def escape_symbols(chat_name):
    return "".join([c if c.isalnum() else "_" for c in str(chat_name)])


def get_last_message_id(chat_id, client, is_sqlite, cursor=None):
    _original_chat_id = chat_id
    chat_id = escape_symbols(chat_id)
    if is_sqlite:
        last_message_id = cursor.execute(f"SELECT MAX(id) FROM {chat_id}").fetchone()[0]
        if last_message_id is None:
            last_message_id = 0
    else:
        try:
            # 2023-06-13-0000000028.txt
            files = [
                f
                for f in os.listdir(f"data/{_original_chat_id}")
                if re.match(r"\d{4}-\d{2}-\d{2}-\d{10}\.txt", f)
            ]
            last_message_id = int(sorted(files)[-1].split("-")[-1].split(".")[0])
        except IndexError:
            last_message_id = 0

    total_messages = client.get_messages(_original_chat_id, limit=1)[0].id - last_message_id
    return last_message_id, total_messages


def export_metadata(chat_id, api_id, api_hash, is_sqlite=False):
    # export metadata: date of export and chat info
    _original_chat_id = chat_id
    chat_id = escape_symbols(chat_id)
    conn = None
    metadata = {}

    with TelegramClient("anon", api_id, api_hash) as client:
        chat = client.get_entity(_original_chat_id)
        metadata["chat_name"] = chat.title
        metadata["chat_id"] = chat.id
        metadata["chat_type"] = chat.__class__.__name__
        metadata["chat_username"] = chat.username
        metadata["chat_date"] = chat.date.strftime("%Y-%m-%d %H:%M:%S")
        metadata["chat_export_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        metadata["chat_export_version"] = "0.1"
        metadata["chat_export_format"] = "sqlite" if is_sqlite else "txt"

    if is_sqlite:
        conn = sqlite3.connect(f"data/{chat_id}.db")
        c = conn.cursor()
        c.execute(f"""CREATE TABLE IF NOT EXISTS {chat_id}_meta (
            key TEXT PRIMARY KEY,
            value TEXT
        )""")
        for key, value in metadata.items():
            c.execute(f"""INSERT INTO {chat_id}_meta VALUES (
                "{key}",
                "{value}"
            )""")
        conn.commit()
        conn.close()
    else:
        # write to file (Key,Value)
        os.makedirs(f"data/{chat_id}", exist_ok=True)
        with open(f"data/{chat_id}/_metadata.txt", "w") as f:
            for key, value in metadata.items():
                f.write(f"{key},{value}\n")


def export_messages(chat_id, api_id, api_hash, is_sqlite=False):
    _original_chat_id = chat_id
    chat_id = escape_symbols(chat_id)
    conn = None

    if is_sqlite:
        conn = sqlite3.connect(f"data/{chat_id}.db")
        c = conn.cursor()
        c.execute(f"""CREATE TABLE IF NOT EXISTS {chat_id} (
            id INTEGER PRIMARY KEY,
            date TEXT,
            text TEXT
        )""")
    else:
        os.makedirs(f"data/{chat_id}", exist_ok=True)

    with TelegramClient("anon", api_id, api_hash) as client:
        last_message_id, total_messages = get_last_message_id(
            _original_chat_id, client, is_sqlite, c if is_sqlite else None
        )

        if total_messages == 0:
            print("No new messages.")
            sys.exit(0)
        else:
            print(f"Exporting {total_messages} new messages.")

        with tqdm(total=total_messages) as pbar:
            for message in client.iter_messages(_original_chat_id, min_id=last_message_id):
                if is_sqlite:
                    try:
                        c.execute(f"""INSERT INTO {chat_id} VALUES (
                            {message.id},
                            "{message.date.strftime('%Y-%m-%d %H:%M:%S')}",
                            "{message.text.replace('"', '""')}"
                        )""")
                    except sqlite3.OperationalError as e:
                        print(f"Error inserting into SQLite: {e}")
                else:
                    with open(
                        (  # right zero pad message id so it sorts correctly
                            f"data/{chat_id}/"
                            f"{message.date.strftime('%Y-%m-%d')}"
                            f"-{str(message.id).zfill(10)}.txt"
                        ),
                        "w",
                    ) as f:
                        try:
                            f.write(message.text)
                        except Exception as e:
                            f.write(f"TGExport Error:\n{e}")
                pbar.update()

        if is_sqlite:
            conn.commit()
            conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("chat_id", help="username or id of the chat to export")
    parser.add_argument("--id", help="use channel id instead of username", action="store_true")
    parser.add_argument("--sqlite", help="export to sqlite database", action="store_true")
    parser.add_argument("--version", help="print version and exit", action="store_true")
    parser.add_argument("--metadata", help="export metadata", action="store_true")
    args = parser.parse_args()

    if args.version:
        print(f"TGExport v{__version__}")
        sys.exit(0)

    load_dotenv()
    api_id = os.getenv("API_ID")
    api_hash = os.getenv("API_HASH")

    if not api_id or not api_hash:
        print("Please provide API_ID and API_HASH in .env file or as environment variables.")
        sys.exit(2)

    chat_id = str(args.chat_id)

    if args.metadata:
        print("Exporting metadata...")
        export_metadata(chat_id, api_id, api_hash, args.sqlite)

    export_messages(chat_id, api_id, api_hash, args.sqlite)
