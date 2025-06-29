
from pydantic import BaseModel
from typing import Optional

class TestimonialBase(BaseModel):
    name: str
    description: Optional[str] = None


class TestimonialCreate(TestimonialBase):
    pass  # No image_url here


class TestimonialUpdate(TestimonialBase):
    pass  # No image_url here


class TestimonialOut(TestimonialBase):
    id: int
    image_url: Optional[str] = None  # Only here for response

    class Config:
        orm_mode = True
