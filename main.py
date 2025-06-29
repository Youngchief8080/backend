# backend/main.py

from fastapi import FastAPI
import uvicorn
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
import os
from pathlib import Path

app = FastAPI()

# Allow frontend origin
origins = [
    "http://localhost:3000",  # frontend dev server
    "http://127.0.0.1:3000",
    "https://www.ptownentertainment.com",
    "https://www.ptownentertainment.com/"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Now include your routers below this
from app.api.routes.auth import router as auth_router
app.include_router(auth_router, prefix="/auth")

# For services
from app.api.routes import service
app.include_router(service.router)

# ✅ For sub-services
from app.api.routes import sub_service
app.include_router(sub_service.router)
# for banners
from app.api.routes import banners
app.include_router(banners.router)
# for pastevent 
from app.api.routes import pastevent
app.include_router(pastevent.router)
#for technician fetch
from app.api.routes import fetchTechnician
app.include_router(fetchTechnician.router)

#for bookings 
from app.api.routes import booking
app.include_router(booking.router, tags=["Bookings"])
#update users
from app.api.routes.updateUser import router as update_router
app.include_router(update_router, prefix="/users")  # New update routes

#from gallery
from app.api.routes import gallery
app.include_router(gallery.router)

#for news
from app.api.routes import news
app.include_router(news.router)

#for chat routes 
from app.api.routes import chats
app.include_router(chats.router)

#for contact 
from app.api.routes import contact
app.include_router(contact.router)

#for points

from app.api.routes import loyalty
app.include_router(loyalty.router)

#for Teams Members
from app.api.routes import teams
app.include_router(teams.router)

#for Testimonial 
from app.api.routes import Testimonial
app.include_router(Testimonial.router)

#for getintouch
from app.api.routes import getintouch
app.include_router(getintouch.router)

# Serve uploaded images
# uploads_dir = Path(__file__).resolve().parent / "uploads"
# app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
#media
# app.mount("/media", StaticFiles(directory="media"), name="media")
uploads_dir = Path(__file__).resolve().parent / "uploads"
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

if __name__ == "__main__":
    environment = settings.ENVIRONMENT

    port = int(os.environ.get("PORT", 8000))

    host="0.0.0.0"

    workers = 4 if environment =="production" else 1


    if environment == "production" :
        uvicorn.run("main:app" , host=host, port=port , workers=workers , reload=False)
    else :
        uvicorn.run("main:app" , host=host, port=port , reload=True)


