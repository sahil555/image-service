from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "image-service"
    AWS_REGION: str = "ap-south-1"
    S3_BUCKET_NAME: str = "image-service-bucket-ap-south-1"
    DYNAMODB_TABLE_NAME: str = "image-service-table-ap-south-1"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()