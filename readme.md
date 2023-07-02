# TGExport

TGExport is a simple Python script to export and save messages from Telegram channels. It uses the Telethon library to interact with the Telegram API.

## Features

- Downloads and saves messages from specified Telegram channel
- Uses Telegram message timestamp and id to name the files
- Saves new messages, skipping any previously downloaded ones

## Getting Started

### Prerequisites

TGExport uses Poetry for dependency management. Make sure you have Poetry installed. If not, follow the instructions on the [Poetry website](https://python-poetry.org/docs/).
You also need to register a 3rd-party app in [Telegram API Developer Tools](https://my.telegram.org/apps) to get the APP_ID and APP_HASH.

### Installation

1. Clone the repo:
   ```
   git clone https://github.com/mehraneftekhari99/tgexport.git
   ```
2. Navigate to the project directory:
   ```
   cd tgexport
   ```
3. Install the dependencies:
   ```
   poetry install
   ```

### Usage

1. Create a `.env` file in the project root directory with the following content, and replace the placeholders with your actual Telegram API ID and Hash:
   ```
   API_ID=<Your Telegram API ID>
   API_HASH=<Your Telegram API Hash>
   ```

2. Run the script:
   ```
   poetry run python tgexport.py <Telegram Channel Username>
   ```

## Running Tests

Run the tests to verify that everything is working correctly:
```
poetry run python tests.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is released into the public domain. For more information, see the [LICENSE](https://unlicense.org) in this repository.
