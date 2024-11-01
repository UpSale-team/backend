from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .v1.configs.swagger_config import swagger_config

#Define create app function
def create_app():
    #Create FastAPI instance
    app = FastAPI(**swagger_config)

    #Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


    return app