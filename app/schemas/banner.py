
from pydantic import BaseModel
from typing import Optional


class BannerBase(BaseModel):
    name: str
    description: Optional[str] = None


class BannerCreate(BannerBase):
    pass  # No image_url here


class BannerUpdate(BannerBase):
    pass  # No image_url here


class BannerOut(BannerBase):
    id: int
    image_url: Optional[str] = None  # Only here for response

    class Config:
        orm_mode = True
