from pydantic import BaseModel


class CategoryOut(BaseModel):
    id: int
    name: str
    slug: str
    article_count: int  # 该分类下有多少篇文章

    model_config = {"from_attributes": True}
