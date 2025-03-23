from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()


class GameSettings(BaseModel):
    API_BASE_URL: str = os.getenv("API_BASE_URL", "https://default.api.com")
    TIMEOUT: int = int(os.getenv("TIMEOUT", 60))
    CORS_ORIGINS: list[str] = os.getenv("CORS_ORIGINS", "http://localhost").split(",")
    HARDHAT_URL: str = os.getenv("HARDHAT_URL", "n9xnx9873x1n210981nxnx098")
    CONTRACT_ADDRESS: str = os.getenv("CONTRACT_ADDRESS", "80543534378hfddshi")
    PRIVATE_KEY: str = os.getenv("PRIVATE_KEY", "7849127421dshadhisadhisasadhsai")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")

settings = GameSettings()
print(settings)
