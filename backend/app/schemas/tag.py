from pydantic import BaseModel


class TagOut(BaseModel):
    id: int
    name: str
    slug: str
    article_count: int  # 该标签下有多少篇文章

    model_config = {"from_attributes": True}
