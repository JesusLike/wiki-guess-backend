from enum import Enum
import logging
from fastapi import APIRouter, HTTPException
from data import Countries, CountryModel

router = APIRouter(prefix="/countries", tags=["countries"])

class ReadCountryMode(Enum):
    NAMES = "names"
    DATA = "data"
    FULL = "full"

@router.get("/", status_code=200, response_model=list[CountryModel] | list[str] | dict[str, CountryModel])
def get_all_countries(mode: ReadCountryMode = ReadCountryMode.DATA):
    try:
        countries = Countries.get_all_countries() 
        
    except Exception as e:
        logging.warning(e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error occured")
    
    if mode == ReadCountryMode.NAMES:
        return list(countries.keys())
    if mode == ReadCountryMode.DATA:
        return list(countries.values())
    return countries

@router.get("/{country_name}", status_code=200, response_model=CountryModel)
def get_country_by_name(country_name: str):
    try:
        country = Countries.get_country_by_name(country_name)
    except Exception as e:
        logging.warning(e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error occured")
    else:
        if not country:
            raise HTTPException(status_code=404, detail=f"Country {country_name} not found")
        return country
