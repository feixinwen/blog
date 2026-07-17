import logging

from sqlmodel import Session, SQLModel, select

from app.core.config import settings
from app.core.deps import engine
from app.core.security import hash_password
from app.models.article import Article, ArticleTagLink
from app.models.category import Category
from app.models.comment import Comment
from app.models.tag import Tag
from app.models.user import User

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)


def seed():
    logger.info("开始初始化种子数据...")

    # 先建表（如果表已存在则跳过）
    SQLModel.metadata.create_all(engine)

    with Session(engine) as db:
        # 1. 创建管理员账号
        existing = db.exec(
            select(User).where(User.username == "admin")
        ).first()
        if existing is None:
            admin = User(
                username="admin",
                password_hash=hash_password("admin123"),
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            logger.info("管理员账号已创建: admin / admin123")
        else:
            logger.info("管理员账号已存在，跳过")

        # 2. 创建示例分类
        cat_names = [
            ("Python", "python"),
            ("前端开发", "frontend"),
            ("数据库", "database"),
            ("部署运维", "devops"),
        ]
        categories = {}
        for name, slug in cat_names:
            exist = db.exec(select(Category).where(Category.slug == slug)).first()
            if exist:
                categories[slug] = exist
            else:
                cat = Category(name=name, slug=slug)
                db.add(cat)
                db.commit()
                db.refresh(cat)
                categories[slug] = cat
                logger.info(f"分类已创建: {name}")

        # 3. 创建示例标签
        tag_data = [
            ("FastAPI", "fastapi"),
            ("Vue", "vue"),
            ("TypeScript", "typescript"),
            ("MySQL", "mysql"),
            ("Docker", "docker"),
        ]
        tags = {}
        for name, slug in tag_data:
            exist = db.exec(select(Tag).where(Tag.slug == slug)).first()
            if exist:
                tags[slug] = exist
            else:
                tag = Tag(name=name, slug=slug)
                db.add(tag)
                db.commit()
                db.refresh(tag)
                tags[slug] = tag
                logger.info(f"标签已创建: {name}")

        # 4. 创建一篇示例文章
        exist = db.exec(select(Article).where(Article.slug == "hello-world")).first()
        if exist is None:
            article = Article(
                title="Hello World — 我的第一篇博客",
                slug="hello-world",
                content="""## 欢迎来到我的博客

大家好，这是我的个人博客的第一篇文章。

### 关于这个博客

这个博客使用以下技术栈构建：

- **后端**：FastAPI + SQLModel + MySQL
- **前端**：Vue 3 + TypeScript
- **部署**：Docker + Nginx

### 代码示例

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def hello():
    return {"message": "Hello World!"}
```

```typescript
const message: string = "Hello from TypeScript!"
console.log(message)
```

### 结语

> 博客不仅是记录，更是一种思考的方式。

我会在这里分享技术心得和学习笔记，希望对你也有帮助。
""",
                summary="这是我的第一篇博客文章，介绍博客的技术栈和初衷。",
                category_id=categories["python"].id,
                is_published=True,
            )
            db.add(article)
            db.commit()
            db.refresh(article)

            # 关联标签
            for slug in ["fastapi", "vue", "typescript", "mysql"]:
                db.add(ArticleTagLink(article_id=article.id, tag_id=tags[slug].id))
            db.commit()
            logger.info(f"示例文章已创建: {article.title}")
        else:
            logger.info("示例文章已存在，跳过")

        # 5. 创建一条示例评论
        exist = db.exec(select(Comment).where(Comment.content.like("%第一条评论%"))).first()  # type: ignore
        if exist is None:
            comment = Comment(
                article_id=db.exec(
                    select(Article).where(Article.slug == "hello-world")
                ).one().id,  # type: ignore
                author_name="小明",
                author_email="xiaoming@example.com",
                content="写得不错！期待更多技术文章。这是博客的第一条评论。",
            )
            db.add(comment)
            db.commit()
            logger.info("示例评论已创建")

    logger.info("种子数据初始化完成！")


if __name__ == "__main__":
    seed()
