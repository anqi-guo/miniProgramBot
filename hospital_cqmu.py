from dotenv import load_dotenv
import os

load_dotenv()
DEPARTMENT = os.getenv("DEPARTMENT")
DOCTOR = os.getenv("DOCTOR")