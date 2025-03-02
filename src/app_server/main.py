from fastapi import FastAPI
from endpoints import routers

app = FastAPI()

for router in routers:
    app.include_router(router=router)

