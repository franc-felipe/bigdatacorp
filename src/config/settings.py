# src/config/settings.py
import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict # Mantenha SettingsConfigDict importado

# NÃO importe ou chame load_dotenv() aqui.
# pydantic-settings com model_config fará isso por você.

class Settings(BaseSettings):
    # PARA PYDANTIC V2: Use 'model_config' para configurar o carregamento do .env
    # Esta é a maneira correta de dizer ao pydantic-settings para procurar o .env
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore' # Ignora variáveis no .env que não estão definidas aqui
    )

    # BIGDATACORP API
    BIGDATACORP_TOKEN_ID: str
    BIGDATACORP_ACCESS_TOKEN: str

    # DATA WAREHOUSE
    DW_HOST: str
    DW_DATABASE: str
    DW_PORT: int
    DW_USER: str
    DW_PASS: str

@lru_cache()
def get_settings() -> Settings: # Adicione o tipo de retorno para clareza
    return Settings()

settings = get_settings()