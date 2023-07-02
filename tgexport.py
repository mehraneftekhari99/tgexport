import os, sys
from dotenv import load_dotenv
from tqdm import tqdm
from telethon.sync import TelegramClient


def export_channel_messages(channel_username, api_id, api_hash):
    # create directory for channel data
    os.makedirs(f"data/{channel_username}", exist_ok=True)

    # get last message id from the latest file in the channel directory
    try:
        last_message_id = int(
            sorted(os.listdir(f"data/{channel_username}"))[-1].split("-")[-1].split(".")[0]
        )
    except IndexError:
        last_message_id = 0

    with TelegramClient("anon", api_id, api_hash) as client:
        # get last message id from channel and compare it to the last message id from the latest file
        total_messages = client.get_messages(channel_username, limit=1)[0].id - last_message_id
        # if there are no new messages, exit
        if total_messages == 0:
            print("No new messages.")
            sys.exit(0)
        else:
            print(f"Exporting {total_messages} new messages.")

        # use total messages to calculate number of iterations for progress bar
        with tqdm(total=total_messages) as pbar:
            # iterate over all messages in channel starting from last_message_id
            for message in client.iter_messages(channel_username, min_id=last_message_id):
                # use message timestamp and id to create filename
                with open(
                    (  # right zero pad message id so it sorts correctly
                        f"data/{channel_username}/"
                        f"{message.date.strftime('%Y-%m-%d')}"
                        f"-{str(message.id).zfill(10)}.txt"
                    ),
                    "w",
                ) as f:
                    # on error write error message to file
                    try:
                        f.write(message.text)
                    except Exception as e:
                        f.write(f"TGExport Error:\n{e}")
                # update progress bar
                pbar.update()


if __name__ == "__main__":
    channel_username = sys.argv[1] if len(sys.argv) > 1 else None
    if not channel_username:
        print("Please provide channel username as first argument.")
        print("Example: python tgexport.py EricNotes")
        sys.exit(1)

    # get api_id and api_hash from https://my.telegram.org
    load_dotenv()
    api_id = os.environ.get("API_ID")
    api_hash = os.environ.get("API_HASH")
    if not api_id or not api_hash:
        print("Please provide API_ID and API_HASH in .env file or as environment variables.")
        sys.exit(2)

    export_channel_messages(channel_username, api_id, api_hash)
