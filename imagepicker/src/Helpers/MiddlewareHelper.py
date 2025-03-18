from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yaml

class MiddlewareHelper:
    __yaml_path = 'src/Config/middleware.yaml'

    def setCors(app: FastAPI):
        with open(MiddlewareHelper.__yaml_path, "r") as middleware:
            yaml_data = yaml.safe_load(middleware)

            app.add_middleware(
                CORSMiddleware,
                allow_origins=yaml_data['origins'],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )