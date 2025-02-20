import os

class Config:
    DB_HOST = os.getenv("DB_HOST", "postgis")
    DB_NAME = os.getenv("DB_NAME", "osm_data")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "1234")
    DB_PORT = os.getenv("DB_PORT", 9876)