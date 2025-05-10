import os
import json
import logging
from fastapi import FastAPI, Request
from google_auth_oauthlib.flow import Flow  # Corrected import
from googleapiclient.discovery import build
import uvicorn
from google.oauth2.credentials import Credentials
from starlette.responses import RedirectResponse

# Set up logging
logger = logging.getLogger("web_server")
logging.basicConfig(level=logging.INFO)

app = FastAPI()

# Get base URL from environment or default to localhost
# Use PORT from environment or default to 8000
PORT = int(os.getenv("PORT", 8000))

# Get the base URL from environment
# On Railway, we can construct it from RAILWAY_STATIC_URL or RAILWAY_PUBLIC_DOMAIN if available
BASE_URL = os.getenv("BASE_URL")
if not BASE_URL:
    railway_static_url = os.getenv("RAILWAY_STATIC_URL")
    railway_domain = os.getenv("RAILWAY_PUBLIC_DOMAIN")
    if railway_static_url:
        BASE_URL = f"https://{railway_static_url}"
    elif railway_domain:
        BASE_URL = f"https://{railway_domain}"
    else:
        BASE_URL = f"http://localhost:{PORT}"

# Log the redirect URI on startup
logger.info(f"🔗 OAuth Redirect URI: {BASE_URL}/oauth2callback")
logger.info(f"🌐 Running web server on port: {PORT}")
logger.info(f"🌐 Environment variables: PORT={os.getenv('PORT')}, RAILWAY_STATIC_URL={os.getenv('RAILWAY_STATIC_URL')}, RAILWAY_PUBLIC_DOMAIN={os.getenv('RAILWAY_PUBLIC_DOMAIN')}")

# Google OAuth configuration
CLIENT_SECRETS_JSON = os.getenv("GOOGLE_CLIENT_SECRETS_JSON")
if CLIENT_SECRETS_JSON:
    CLIENT_SECRETS = json.loads(CLIENT_SECRETS_JSON)
    logger.info("✅ Google OAuth client secrets loaded successfully")
else:
    logger.error("❌ GOOGLE_CLIENT_SECRETS_JSON environment variable not set")
    CLIENT_SECRETS = None

SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/tasks.readonly'
]

# Dictionary to store OAuth flows for different users
active_flows = {}

@app.get("/")
async def root():
    """Root endpoint to confirm the web server is running."""
    return {"status": "Discord-Basil OAuth server is running"}

@app.get("/authorize")
async def authorize(request: Request, user_id: str):
    """
    Start the OAuth flow for a specific Discord user.
    """
    if not CLIENT_SECRETS:
        return {"error": "OAuth configuration not available"}

    try:
        # Create a flow instance to manage the OAuth 2.0 Authorization Grant Flow
        redirect_uri = f"{BASE_URL}/oauth2callback"
        logger.info(f"Using redirect URI: {redirect_uri}")
        
        flow = Flow.from_client_config(
            client_config=CLIENT_SECRETS,
            scopes=SCOPES,
            redirect_uri=redirect_uri
        )

        # Generate authorization URL
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )

        # Store the flow object for later use in the callback
        active_flows[user_id] = flow

        logger.info(f"Generated authorization URL for user {user_id}")
        return RedirectResponse(url=authorization_url)
    except Exception as e:
        logger.error(f"Error generating authorization URL: {e}")
        return {"error": f"Failed to start authorization: {str(e)}"}

@app.get("/oauth2callback")
async def oauth2callback(request: Request, state: str = None, code: str = None, error: str = None, user_id: str = None):
    """
    Handle the OAuth 2.0 callback from Google.
    """
    if error:
        logger.error(f"OAuth error: {error}")
        return {"error": error}

    if not user_id or user_id not in active_flows:
        logger.error("Invalid or missing user_id in callback")
        return {"error": "Invalid or missing user_id"}

    try:
        flow = active_flows[user_id]
        
        # Use the authorization code to fetch tokens
        flow.fetch_token(code=code)
        
        # Get credentials from flow
        credentials = flow.credentials
        
        # Store credentials for this user (you'll need to implement a storage mechanism)
        # For now, we'll just log that we received them
        logger.info(f"Received OAuth credentials for user {user_id}")
        
        # Clean up flow
        del active_flows[user_id]
        
        # Save credentials to file or database (implement this based on your needs)
        # save_credentials(user_id, credentials)
        
        return {"message": "Authorization successful! You can close this window and return to Discord."}
    except Exception as e:
        logger.error(f"Error processing OAuth callback: {e}")
        return {"error": f"Failed to complete authorization: {str(e)}"}

# Helper functions
def save_credentials(user_id, credentials):
    """
    Save user credentials securely.
    TODO: Implement proper secure storage for user credentials.
    """
    # This is a placeholder. You should store these securely in a database.
    pass

def get_user_google_services(user_id):
    """
    Get Google Calendar and Tasks services for a specific user.
    TODO: Implement user-specific credential retrieval.
    """
    # Placeholder for retrieving user-specific credentials
    # credentials = retrieve_credentials(user_id)
    # 
    # if not credentials:
    #     return None, None
    # 
    # calendar_service = build("calendar", "v3", credentials=credentials, cache_discovery=False)
    # tasks_service = build("tasks", "v1", credentials=credentials, cache_discovery=False)
    # 
    # return calendar_service, tasks_service
    pass