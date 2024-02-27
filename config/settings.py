from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    app_name: str = "5353"
    admin_email: str = "yovell04@gmail.com"

    MONGO_FULL_URL: str = 'mongodb://admin:admin@localhost:27017'
    DATABASE_NAME: str = 'rochash'
