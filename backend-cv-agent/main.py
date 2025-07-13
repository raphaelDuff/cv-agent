import os
import logging
from dotenv import load_dotenv
from server import CVServer

# load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"), override=True)
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if not OPENAI_API_KEY:
    print("Error: OPENAI_API_KEY environment variable not found!")

cv_server = CVServer(OPENAI_API_KEY)
app = cv_server.get_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
