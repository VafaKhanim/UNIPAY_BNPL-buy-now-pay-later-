from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db

# Bütün route-larda bu type alias istifadə olunur
DB = Annotated[Session, Depends(get_db)]