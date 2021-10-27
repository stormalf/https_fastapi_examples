#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
from requests.sessions import Request
import uvicorn
from pygithubapi import pygithubapi as pg
from fastapi.security.api_key import APIKeyHeader, APIKey, APIKeyQuery, APIKeyCookie
from fastapi import FastAPI, Depends, Security, HTTPException, Form, status
from pydantic import BaseSettings
from functools import lru_cache
from fastapi.responses import RedirectResponse,HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from cryptography.fernet import Fernet

'''
Example using uvicorn and fastapi sample and pygithubapi.
Updated to use an API KEY to be able to use the api

'''

#some constants and environment variables
certfile = os.environ.get("TLS_CERT_PATH") 
keyfile = os.environ.get("TLS_KEY_PATH")
itoken = os.environ.get("GITHUB_TOKEN")
user = os.environ.get("USER")
repo = "ansible_modules_customs"
host = "localhost"
port = 8443
reload = True
API_KEY = os.environ.get("API_KEY")
API_KEY_NAME = "Authorization"
COOKIE_DOMAIN = "localhost"
pth = os.path.dirname(__file__)
privkey = Fernet.generate_key() 
cipher_suite = Fernet(privkey)

#from https://medium.com/data-rebels/fastapi-authentication-revisited-enabling-api-key-authentication-122dc5975680
api_key_query = APIKeyQuery(name=API_KEY_NAME, auto_error=False)
api_key_cookie = APIKeyCookie(name=API_KEY_NAME, auto_error=False)
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

#return the encrypted password/token
def encrypted(token):
    ciphered_text = cipher_suite.encrypt(token.encode())
    encrypted_token = str(ciphered_text, "utf-8")
    return encrypted_token

#return the decrypted password/token
def decrypted(token):
    tokenbytes = bytes(token, "utf-8")
    decrypted_text = cipher_suite.decrypt(tokenbytes)
    decrypted_text = decrypted_text.decode()
    return decrypted_text

#more example and information at https://retz.blog/posts/adding-api-key-authorization
class Settings(BaseSettings):
    API_KEY: str

#should be executed before the app = FastAPi() and @lru_cache to be executed only one time
@lru_cache()
def get_settings():
    return Settings()

#possibility to create with no doc, no redoc by settings none for each parameter
#app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app = FastAPI(title="testing FastAPI",
    description="This API was built with FastAPI and has only for testing purpose",
    version="1.0.0")

#check if the header contains the correct api key 
async def get_api_key(
    api_key_query: str = Security(api_key_query),
    api_key_header: str = Security(api_key_header),
    api_key_cookie: str = Security(api_key_cookie),
    ):
    if api_key_cookie != None:
        decrypted_apikeycookie = decrypted(api_key_cookie)
    else: 
        decrypted_apikeycookie = api_key_cookie        
    if api_key_query == API_KEY:
        return api_key_query
    elif api_key_header == API_KEY:
        return api_key_header
    elif decrypted_apikeycookie == API_KEY:
        return decrypted_apikeycookie
    else:
        raise HTTPException(status_code=403, detail="Bad credentials")


#api that needs to be authenticated before using it        
@app.get("/repos")
async def get_repos(
    api_key: APIKey = Depends(get_api_key),
    api=f"/users/{user}/repos", user=user, method="GET", url="https://api.github.com", json=""
    ):
    result = pg.GithubApi.runGithubApi(api=api, method=method, url=url, user=user, token=itoken, json=json) 
    return result 


#root api that returns a custom message
@app.get("/",response_class=HTMLResponse)
def read_root():
    #return {"FastAPI": "Testing!"}
    with open(os.path.join(pth, "login.html")) as f:
        return HTMLResponse(content=f.read())


#if authentication succeeds, create the cookie with token encrypted
@app.post("/auth/login")
def login(data: OAuth2PasswordRequestForm = Depends()):
    username = data.username
    apikey = data.password
    if username != user:
        raise HTTPException(status_code=403, detail="Incorrect login!")
    elif apikey != API_KEY:
        raise HTTPException(status_code=403, detail="Incorrect apikey!")
    response = RedirectResponse(url="/repos",status_code=302)
    encrypted_apikey= encrypted(apikey)
    response.set_cookie(API_KEY_NAME, encrypted_apikey)
    return response

#remove the cookie
@app.get("/logout")
async def route_logout_and_remove_cookie():
    response = RedirectResponse(url="/")
    response.delete_cookie(API_KEY_NAME, domain=COOKIE_DOMAIN)
    return response


def run():
    #running uvicorn in https mode 
    uvicorn.run(
        f"pygithubfastapi:app",
        host=host, port=port, log_level="info", reload=reload, ssl_keyfile=keyfile, ssl_certfile=certfile, timeout_keep_alive=60, 
    )


if __name__ == '__main__':
    run()
