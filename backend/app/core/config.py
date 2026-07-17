from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 数据库配置
    db_host: str = "localhost"
    db_port: int = 3306
    db_user: str = "root"
    db_password: str = "123456"
    db_name: str = "blog"

    # JWT 配置
    jwt_secret_key: str = "change-me-to-a-real-secret-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24  # 登录有效期：24 小时

    @property
    def database_url(self) -> str:
        """拼接 MySQL 连接字符串"""
        return (
            f"mysql+pymysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


settings = Settings()
