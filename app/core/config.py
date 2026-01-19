from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str
    MONGO_URI: str
    DATABASE_NAME: str

    # Configuração para ler o arquivo .env automaticamente
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()