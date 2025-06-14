# backend/main.py

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow frontend origin
origins = [
    "http://localhost:3000",  # frontend dev server
    "http://127.0.0.1:3000",
    "*"  # Optional for testing, use specific in production
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

from app.api.routes import loyalty
app.include_router(loyalty.router)



# Serve uploaded images
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
#media
# app.mount("/media", StaticFiles(directory="media"), name="media")



