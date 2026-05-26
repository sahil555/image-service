from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "image-service"
    AWS_REGION: str = "ap-south-1"
    S3_BUCKET_NAME: str
    DYNAMODB_TABLE_NAME: str

    class Config:
        env_file = ".env"


settings = Settings()