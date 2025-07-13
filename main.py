import os
import logging
from dotenv import load_dotenv
from server import CVServer

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"), override=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
cv_server = CVServer(OPENAI_API_KEY)
app = cv_server.get_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
