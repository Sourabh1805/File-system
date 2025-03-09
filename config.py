import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

def get_dotenv_file():

    env = os.getenv("ENV", "dev").lower()  # Default to 'dev' if ENV is not set
    print("---------------- ENV -------- ",env )

    if env == "test":
        return ".env.test"
    elif env == "dev":
        return ".env.dev"
    else:
        raise ValueError(f"Unsupported ENV value: {env}. Expected 'dev' or 'test'.")


dotenv_file = get_dotenv_file()
load_dotenv(dotenv_file)
print("----------- dotenv_file----------",dotenv_file)

class Config(BaseSettings):
    ENV: str = "dev"
   
    class Config:
        env_file = dotenv_file  

    

settings = Config()
