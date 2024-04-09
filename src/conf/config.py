from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
    db_url: str
    db_local_url: str
    secret_key: str
    algorithm: str
    mail_username: str
    mail_password: str
    mail_from: str
    mail_port: int
    mail_server: str
    redis_host: str
    redis_local_host: str = 'localhost'
    redis_port: int = '6379'
    db_admin: str
    db_password: str
    db_port: str
    db_name: str
    cloudinary_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str
    cloudinary_url: str


settings = Settings(_env_file='.env', _env_file_encoding='utf-8')
print(settings.db_url)

