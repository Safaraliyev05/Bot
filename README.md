# Telegram Lesson Bot

A Telegram bot designed to guide users through a series of lessons, sending reminders, videos, and tracking user engagement.

## Features

- Sends a series of lesson videos to users.
- Tracks user engagement with lessons.
- Sends reminders for upcoming lessons and bonuses.
- Collects and stores user contact information.
- Provides a Google form for further feedback or data collection.

## Available Commands
### For Users:
- **/start**: Begin the lesson series and start tracking user engagement.

### For Admins:
- **/report**: Provides information about users who have started and viewed the first, second, third, and subsequent videos.
- **/users**: Sends a list of users (including their phone numbers and usernames) in an xlsx file.

## Technologies Used

- Python 3.8+
- Aiogram
- Pandas
- Dotenv

## Setup Instructions

### Prerequisites

- Python 3.8 or above
- Telegram Bot API token (You can create a bot via [BotFather](https://core.telegram.org/bots#botfather))

### Installation

1. Clone the repository:

   ```bash
      git clone https://github.com/Safaraliyev05/Bot.git
   cd Bot

2. Create a virtual environment and activate it
python -m venv venv
source venv/bin/activate

3. Install the required packages
pip install -r requirements.txt

4. Create a .env file in the project root directory and add your environment variables
TOKEN=your-telegram-bot-token
ADMIN_CHAT_ID=your-chat-id




