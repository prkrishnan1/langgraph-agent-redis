from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file= ".env", env_file_encoding='utf-8'
    )
    
    azure_endpoint: str = ""
    api_version: str = ""
    openai_api_key: str = ""
    azure_deployment: str = ""

    weather_api_key: str = ""
    tavily_api_key: str = ""
    roche_certs: str = ""

    redis_url: str = ""

settings = Settings()
