from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    database_url: str
    jwt_secret: str = 'development-only-change-me'
    llm_base_url: str = ''
    llm_api_key: str = ''
    llm_model: str = 'llama-3.1-8b-instant'
    embedding_model: str = 'sentence-transformers/all-MiniLM-L6-v2'
    allowed_origins: str = 'http://localhost:3000'
    @property
    def origins(self): return [x.strip() for x in self.allowed_origins.split(',')]
settings = Settings()
