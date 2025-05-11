import os
import json
import logging
from fastapi import FastAPI, Request
from google_auth_oauthlib.flow import Flow  # Corrected import
from googleapiclient.discovery import build
import uvicorn
from google.oauth2.credentials import Credentials
from starlette.responses import RedirectResponse
from google_services import save_user_credentials

# Set up logging
logger = logging.getLogger("web_server")
logging.basicConfig(level=logging.INFO)

app = FastAPI()

# Get the port from environment or default to 8000
PORT = int(os.getenv("PORT", 8000))

# Get the base URL from environment
# Since RAILWAY_STATIC_URL might be empty, we need a better approach
BASE_URL = os.getenv("BASE_URL")
if not BASE_URL or BASE_URL.strip() == "":
    # Try Railway-specific environment variables
    railway_static_url = os.getenv("RAILWAY_STATIC_URL")
    railway_domain = os.getenv("RAILWAY_PUBLIC_DOMAIN")
    railway_service_id = os.getenv("RAILWAY_SERVICE_ID")
    
    # Check if we have valid Railway variables (not None or empty string)
    if railway_static_url and railway_static_url.strip() != "":
        BASE_URL = f"https://{railway_static_url}"
    elif railway_domain and railway_domain.strip() != "":
        BASE_URL = f"https://{railway_domain}"
    elif railway_service_id and railway_service_id.strip() != "":
        # Try to construct URL from service ID
        BASE_URL = f"https://{railway_service_id}.up.railway.app"
    else:
        # We're not on Railway or can't detect URL, use localhost
        BASE_URL = f"http://localhost:{PORT}"

# Log detailed information about URL detection
logger.info(f"🔗 Detected BASE_URL: {BASE_URL}")
logger.info(f"🔗 OAuth Redirect URI: {BASE_URL}/oauth2callback")
logger.info(f"🌐 Running web server on port: {PORT}")
logger.info(f"🌐 Environment variables:")
logger.info(f"   - PORT={os.getenv('PORT')}")
logger.info(f"   - BASE_URL={os.getenv('BASE_URL')}")
logger.info(f"   - RAILWAY_STATIC_URL={os.getenv('RAILWAY_STATIC_URL')}")
logger.info(f"   - RAILWAY_PUBLIC_DOMAIN={os.getenv('RAILWAY_PUBLIC_DOMAIN')}")
logger.info(f"   - RAILWAY_SERVICE_ID={os.getenv('RAILWAY_SERVICE_ID')}")

# Google OAuth configuration
CLIENT_SECRETS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON")
if CLIENT_SECRETS_JSON:
    CLIENT_SECRETS = json.loads(CLIENT_SECRETS_JSON)
    logger.info("✅ Google OAuth client secrets loaded successfully")
else:
    logger.error("❌ GOOGLE_CREDENTIALS_JSON environment variable not set")
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
        logger.error("OAuth client secrets not available")
        return {"error": "OAuth configuration not available"}

    try:
        # Create a flow instance to manage the OAuth 2.0 Authorization Grant Flow
        redirect_uri = f"{BASE_URL}/oauth2callback"
        
        # Log detailed information about the authorization attempt
        logger.info(f"==== AUTHORIZATION DEBUG INFO ====")
        logger.info(f"User ID: {user_id}")
        logger.info(f"Redirect URI: {redirect_uri}")
        
        # Log client info (without sensitive parts)
        if isinstance(CLIENT_SECRETS, dict):
            if 'web' in CLIENT_SECRETS:
                client_id = CLIENT_SECRETS['web'].get('client_id', 'Not found')
                auth_uri = CLIENT_SECRETS['web'].get('auth_uri', 'Not found')
                redirect_uris = CLIENT_SECRETS['web'].get('redirect_uris', [])
                logger.info(f"Client ID: {client_id}")
                logger.info(f"Auth URI: {auth_uri}")
                logger.info(f"Configured redirect URIs: {redirect_uris}")
                
                # Check if our redirect URI is in the configured list
                if redirect_uri not in redirect_uris:
                    logger.error(f"⚠️ CRITICAL: Redirect URI {redirect_uri} is not in the configured redirect URIs list!")
            else:
                logger.error("OAuth client configuration missing 'web' section")
        
        # Create the OAuth flow
        flow = Flow.from_client_config(
            client_config=CLIENT_SECRETS,
            scopes=SCOPES,
            redirect_uri=redirect_uri
        )

        # Generate authorization URL with additional parameters for testing
        # Include the user_id in the state parameter to retrieve it in the callback
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent',
            state=user_id  # Include user_id in state to retrieve it in callback
        )

        # Store the flow object for later use in the callback
        active_flows[user_id] = flow

        logger.info(f"Generated authorization URL: {authorization_url}")
        logger.info(f"State parameter with user_id: {state}")
        logger.info(f"==== END DEBUG INFO ====")
        
        return RedirectResponse(url=authorization_url)
    except Exception as e:
        logger.error(f"Error generating authorization URL: {e}")
        return {"error": f"Failed to start authorization: {str(e)}"}

@app.get("/oauth2callback")
async def oauth2callback(request: Request, state: str = None, code: str = None, error: str = None):
    """
    Handle the OAuth 2.0 callback from Google.
    """
    # Log all query parameters for debugging
    query_params = dict(request.query_params)
    logger.info(f"OAuth callback received with params: {query_params}")
    
    if error:
        logger.error(f"OAuth error: {error}")
        return {"error": error}

    # Get user_id from state or query parameters
    user_id = query_params.get('user_id')
    
    # Log detailed information about the callback
    logger.info(f"==== OAUTH CALLBACK DEBUG INFO ====")
    logger.info(f"State: {state}")
    logger.info(f"Code: {code is not None}")  # Just log if code exists, not the actual code
    logger.info(f"User ID: {user_id}")
    logger.info(f"Active flows: {list(active_flows.keys())}")
    
    if not user_id or user_id not in active_flows:
        logger.error("Invalid or missing user_id in callback")
        return {"error": "Invalid or missing user_id. Make sure to use the !connect_google command again."}

    try:
        flow = active_flows[user_id]
        
        # Use the authorization code to fetch tokens
        flow.fetch_token(code=code)
        
        # Get credentials from flow
        credentials = flow.credentials
        
        # Save the credentials for this user
        saved = save_user_credentials(user_id, credentials)
        if saved:
            logger.info(f"Successfully saved OAuth credentials for user {user_id}")
        else:
            logger.error(f"Failed to save OAuth credentials for user {user_id}")
        
        # Clean up flow
        del active_flows[user_id]
        logger.info(f"==== END OAUTH CALLBACK DEBUG INFO ====")
        
        return {"message": "Authorization successful! You can close this window and return to Discord."}
    except Exception as e:
        logger.error(f"Error processing OAuth callback: {e}")
        logger.info(f"==== END OAUTH CALLBACK DEBUG INFO ====")
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