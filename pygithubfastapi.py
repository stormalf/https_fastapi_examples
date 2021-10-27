#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
from typing import Optional
from fastapi import FastAPI
import uvicorn
from pygithubapi import pygithubapi as pg
'''
Example using uvicorn and fastapi sample and pygithubapi.


'''


certfile = os.environ.get("TLS_CERT_PATH") 
keyfile = os.environ.get("TLS_KEY_PATH")
itoken = os.environ.get("GITHUB_TOKEN")
user = os.environ.get("USER")
repo = "ansible_modules_customs"
host = "localhost"
port = 8443
reload = True


app = FastAPI(title="testing FastAPI",
    description="This API was built with FastAPI and has only for testing purpose",
    version="1.0.0")

#root api that returns the hello world
@app.get("/")
def read_root(api=f"/repos/{user}/{repo}", user=user, method="GET", url="https://api.github.com", json=""):
    result = pg.GithubApi.runGithubApi(api=api, method=method, url=url, user=user, token=itoken, json=json) 
    return result 


def run():
    #running uvicorn in https mode 
    uvicorn.run(
        f"pygithubfastapi:app",
        host=host, port=port, log_level="info", reload=reload, ssl_keyfile=keyfile, ssl_certfile=certfile, timeout_keep_alive=60
    )


if __name__ == '__main__':
    run()
