import requests
from requests.auth import HTTPBasicAuth
from pydantic import BaseModel
from typing import Optional, Dict, List


class GetRequestParameters(BaseModel):
    p: Optional[float] = None


class GetItemRequestParameters(BaseModel):
    id: Optional[float] = None


class GetThreadsRequestParameters(BaseModel):
    id: Optional[str] = None


class hnAPI(BaseModel):

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.token = token

    def get_(self, request_parameters: GetRequestParameters) ->dict:
        url = '/?' + '&'.join([(k + '=' + v) for k, v in request_parameters
            .items()])
        response = requests.get(url, headers={'Authorization': 'Bearer ' +
            self.token})
        return dict(**response.json())

    def get_item(self, request_parameters: GetItemRequestParameters) ->dict:
        url = '/item?' + '&'.join([(k + '=' + v) for k, v in
            request_parameters.items()])
        response = requests.get(url, headers={'Authorization': 'Bearer ' +
            self.token})
        return dict(**response.json())

    def get_newest(self) ->dict:
        url = '/newest'
        response = requests.get(url, headers={'Authorization': 'Bearer ' +
            self.token})
        return dict(**response.json())

    def get_show(self) ->dict:
        url = '/show'
        response = requests.get(url, headers={'Authorization': 'Bearer ' +
            self.token})
        return dict(**response.json())

    def get_jobs(self) ->dict:
        url = '/jobs'
        response = requests.get(url, headers={'Authorization': 'Bearer ' +
            self.token})
        return dict(**response.json())

    def get_submit(self) ->dict:
        url = '/submit'
        response = requests.get(url, headers={'Authorization': 'Bearer ' +
            self.token})
        return dict(**response.json())

    def get_ask(self) ->dict:
        url = '/ask'
        response = requests.get(url, headers={'Authorization': 'Bearer ' +
            self.token})
        return dict(**response.json())

    def get_newcomments(self) ->dict:
        url = '/newcomments'
        response = requests.get(url, headers={'Authorization': 'Bearer ' +
            self.token})
        return dict(**response.json())

    def get_front(self) ->dict:
        url = '/front'
        response = requests.get(url, headers={'Authorization': 'Bearer ' +
            self.token})
        return dict(**response.json())

    def get_threads(self, request_parameters: GetThreadsRequestParameters
        ) ->dict:
        url = '/threads?' + '&'.join([(k + '=' + v) for k, v in
            request_parameters.items()])
        response = requests.get(url, headers={'Authorization': 'Bearer ' +
            self.token})
        return dict(**response.json())

    def post_comment(self, request_body: dict) ->dict:
        url = '/comment'
        response = requests.post(url, json=request_body, headers={
            'Authorization': 'Bearer ' + self.token})
        return dict(**response.json())
