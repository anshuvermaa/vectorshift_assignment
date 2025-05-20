from pydantic import BaseSettings

class Settings(BaseSettings):
    # Redis
    redis_host: str
    redis_port: int
    # Hubspot
    hubspot_client_id: str
    hubspot_client_secret: str
    hubspot_redirect_uri: str
    hubspot_authorization_url: str
    hubspot_token_url: str
    # Airtable
    airtable_client_id: str
    airtable_client_secret: str
    airtable_redirect_uri: str
    airtable_token_url: str
    # Notion
    notion_client_id: str
    notion_client_secret: str
    notion_redirect_uri: str
    notion_token_url: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()