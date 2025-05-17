import os
from dotenv import load_dotenv
import pytz

# Load environment variables
load_dotenv()

# Bot Configuration
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Timezone Configuration
TIMEZONE = pytz.timezone(os.getenv('TIMEZONE', 'America/New_York'))

# Google Configuration
GOOGLE_CREDENTIALS_JSON = os.getenv('GOOGLE_CREDENTIALS_JSON')

# Command Configuration
COMMAND_PREFIX = '!'
COOLDOWN_DURATION = 10  # seconds
