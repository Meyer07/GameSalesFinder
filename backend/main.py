from fastapi import FastApi
from fastapi.middleware.cors import CORSMiddleware
from database import engine
import models
from routes import users, wishlist
from scheduler import startScheduler 

