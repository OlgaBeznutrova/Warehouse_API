from pydantic import BaseSettings


class Settings(BaseSettings):
    server_host: str = "127.0.0.1"
    server_port: int = 8000

    db_name: str
    db_user: str
    db_password: str

    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expiration: int = 3600


settings = Settings()
