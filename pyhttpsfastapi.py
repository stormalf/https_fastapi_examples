#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
from typing import Optional
from fastapi import FastAPI
import uvicorn

'''
Example using uvicorn and fastapi sample from https://fastapi.tiangolo.com starting on https

'''

certfile = os.environ.get("TLS_CERT_PATH") 
keyfile = os.environ.get("TLS_KEY_PATH")
host = "localhost"
port = 8443
reload = True

app = FastAPI(title="testing FastAPI",
    description="This API was built with FastAPI and has only for testing purpose",
    version="1.0.0")

#root api that returns the hello world
@app.get("/")
def read_root():
    return {"Hello": "World"}

#other api example that returns items info
@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}    

def run():
    #running uvicorn in https mode 
    uvicorn.run(
        f"pyhttpsfastapi:app",
        host=host, port=port, log_level="info", reload=reload, ssl_keyfile=keyfile, ssl_certfile=certfile, timeout_keep_alive=60
    )


if __name__ == '__main__':
    run()
