'''
Operations with data about countries
'''

import json
import logging
from pydantic import BaseModel, ValidationError

PATH = "/home/dyudovich/workspace/wiki-guess-backend/src/app_server/data/"

class CountryModel(BaseModel):
    country_name: str
    capital: str
    area_total: str
    area_rank: int
    gdp_total: str
    gdp_total_rank: int
    gdp_per_capita: str
    gdp_per_capita_rank: int
    population_total: str
    population_rank: int
    population_density: str
    population_density_rank: int
    established: int
    former_owner: str
    government: str
    religion: str
    currency: str
    languages: list[str]

class CountryDataProvider:
    cached_countries: dict[str, CountryModel] = None

    def __init__(self, datasource):
        self.datasource = datasource

    def get_all_countries(self) -> dict[str, CountryModel]:
        if self.cached_countries:
            return self.cached_countries
        
        with open(self.datasource, "r") as f:
            countries_data = json.load(f)
            for country_data in countries_data:
                try:
                    country_model = CountryModel.model_validate(country_data)
                except ValidationError:
                    print(country_data)
                    logging.warning("Invalid country data:\n" + json.dumps(country_data))
                    exit()
                else:
                    logging.info(f"Uploading country {country_model.country_name}")
                    if not self.cached_countries:
                        self.cached_countries = {}
                    self.cached_countries[country_model.country_name] = country_model
        
        return self.cached_countries
        
    def get_country_by_name(self, name: str) -> CountryModel | None:
        countries = self.get_all_countries()
        if not name in countries.keys():
            return None
        return countries[name]
        
    def get_country_names(self) -> list[str]:
        return list(self.get_all_countries().keys())
        
    
Countries = CountryDataProvider(PATH + "country_data.json")

if __name__ == "__main__":
    print(Countries.get_country_names())