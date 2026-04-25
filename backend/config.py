from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
    DB_HOST: str = "192.168.15.26"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "wdmzjzzm1"
    DB_NAME: str = "plc_process_db"
    
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    PLC_PORT: int = 102
    PLC_DB_NUMBER: int = 1

settings = Settings()

DB_CONFIG = {
    'host': settings.DB_HOST,
    'user': settings.DB_USER,
    'password': settings.DB_PASSWORD,
    'database': settings.DB_NAME,
    'port': settings.DB_PORT,
    'charset': 'utf8mb4'
}

PLC_CONFIG = {
    'port': settings.PLC_PORT,
    'db_number': settings.PLC_DB_NUMBER
}
