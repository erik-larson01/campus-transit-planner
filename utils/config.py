from dotenv import load_dotenv
import os

load_dotenv()

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
MAX_WALKING_DISTANCE_METERS = 800 #Approx a 10-minute walk