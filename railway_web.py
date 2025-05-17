import os
import uvicorn
from web_server import app

if __name__ == "__main__":
    # This file serves as the entry point for Railway's web service
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)