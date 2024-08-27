import requests
from requests.auth import HTTPBasicAuth
from pydantic import BaseModel
from typing import Optional, Dict, List


class GetApiInventoryImageRequestParameters(BaseModel):
    url: Optional[str] = None
    width: Optional[float] = None
    height: Optional[float] = None
    noEnlarge: Optional[str] = None


class GetApiSettingsCountriesResponse(BaseModel):
    value: Optional[List] = None
    success: Optional[bool] = None
    errors: Optional[List] = None
    errorTexts: Optional[str] = None


class GetApiDarkstoresResponse(BaseModel):
    value: Optional[List] = None
    success: Optional[bool] = None
    errors: Optional[List] = None
    errorTexts: Optional[str] = None


class GetApiDarkstoresDefaultResponse(BaseModel):
    value: Optional[Dict] = None
    success: Optional[bool] = None
    errors: Optional[List] = None
    errorTexts: Optional[str] = None


class PostApiUsersAnonymousRequestBody(BaseModel):
    data: Optional[str] = None


class PostApiUsersAnonymousResponse(BaseModel):
    value: Optional[Dict] = None
    success: Optional[bool] = None
    errors: Optional[List] = None
    errorTexts: Optional[str] = None


class GetApiInventorySettingsResponse(BaseModel):
    value: Optional[Dict] = None
    success: Optional[bool] = None
    errors: Optional[List] = None
    errorTexts: Optional[str] = None


class GetApiTransactionsettingsResponse(BaseModel):
    value: Optional[Dict] = None
    success: Optional[bool] = None
    errors: Optional[List] = None
    errorTexts: Optional[str] = None


class GetApiUsersProfileResponse(BaseModel):
    value: Optional[Dict] = None
    success: Optional[bool] = None
    errors: Optional[List] = None
    errorTexts: Optional[str] = None


class GetApiDeliveryfeesResponse(BaseModel):
    value: Optional[List] = None
    success: Optional[bool] = None
    errors: Optional[List] = None
    errorTexts: Optional[str] = None


class GetApiInventoryPromo5FullResponse(BaseModel):
    value: Optional[List] = None
    success: Optional[bool] = None
    errors: Optional[List] = None
    errorTexts: Optional[str] = None


class GetApiSliders5Response(BaseModel):
    value: Optional[List] = None
    success: Optional[bool] = None
    errors: Optional[List] = None
    errorTexts: Optional[str] = None


class GetApiInventory5Categories31ProductsResponse(BaseModel):
    value: Optional[Dict] = None
    success: Optional[bool] = None
    errors: Optional[List] = None
    errorTexts: Optional[str] = None


class GetApiInventory5Categories73ProductsResponse(BaseModel):
    value: Optional[Dict] = None
    success: Optional[bool] = None
    errors: Optional[List] = None
    errorTexts: Optional[str] = None


class GetApiInventory5StocksResponse(BaseModel):
    value: Optional[List] = None
    success: Optional[bool] = None
    errors: Optional[List] = None
    errorTexts: Optional[str] = None


class FinicSDK(BaseModel):

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.token = token

    def get_api_inventory_image(self, request_parameters:
        GetApiInventoryImageRequestParameters) ->dict:
        url = '/api/inventory/image?' + '&'.join([(k + '=' + v) for k, v in
            request_parameters.items()])
        response = requests.get(url, headers={'Authorization': 'Bearer ' +
            self.token})
        return dict(**response.json())

    def get_api_settings_countries(self) ->GetApiSettingsCountriesResponse:
        url = '/api/settings/countries'
        response = requests.get(url, headers={'Authorization': 'Bearer ' +
            self.token})
        return GetApiSettingsCountriesResponse(**response.json())

    def options_api_settings_countries(self) ->dict:
        url = '/api/settings/countries'
        response = requests.options(url, headers={'Authorization': 
            'Bearer ' + self.token})
        return dict(**response.json())

    def get_api_darkstores(self) ->GetApiDarkstoresResponse:
        url = '/api/darkstores'
        response = requests.get(url, headers={'Authorization': 'Bearer ' +
            self.token})
        return GetApiDarkstoresResponse(**response.json())

    def options_api_darkstores(self) ->dict:
        url = '/api/darkstores'
        response = requests.options(url, headers={'Authorization': 
            'Bearer ' + self.token})
        return dict(**response.json())

    def get_api_darkstores_default(self) ->GetApiDarkstoresDefaultResponse:
        url = '/api/darkstores/default'
        response = requests.get(url, headers={'Authorization': 'Bearer ' +
            self.token})
        return GetApiDarkstoresDefaultResponse(**response.json())

    def options_api_darkstores_default(self) ->dict:
        url = '/api/darkstores/default'
        response = requests.options(url, headers={'Authorization': 
            'Bearer ' + self.token})
        return dict(**response.json())

    def post_api_users_anonymous(self, request_body:
        PostApiUsersAnonymousRequestBody) ->PostApiUsersAnonymousResponse:
        url = '/api/users/anonymous'
        response = requests.post(url, json=request_body, headers={
            'Authorization': 'Bearer ' + self.token})
        return PostApiUsersAnonymousResponse(**response.json())

    def options_api_users_anonymous(self) ->dict:
        url = '/api/users/anonymous'
        response = requests.options(url, headers={'Authorization': 
            'Bearer ' + self.token})
        return dict(**response.json())

    def get_api_inventory_settings(self) ->GetApiInventorySettingsResponse:
        url = '/api/inventory/settings'
        response = requests.get(url, headers={'Authorization': 'Bearer ' +
            self.token})
        return GetApiInventorySettingsResponse(**response.json())

    def options_api_inventory_settings(self) ->dict:
        url = '/api/inventory/settings'
        response = requests.options(url, headers={'Authorization': 
            'Bearer ' + self.token})
        return dict(**response.json())

    def get_api_transactionsettings(self) ->GetApiTransactionsettingsResponse:
        url = '/api/transactionsettings'
        response = requests.get(url, headers={'Authorization': 'Bearer ' +
            self.token})
        return GetApiTransactionsettingsResponse(**response.json())

    def options_api_transactionsettings(self) ->dict:
        url = '/api/transactionsettings'
        response = requests.options(url, headers={'Authorization': 
            'Bearer ' + self.token})
        return dict(**response.json())

    def get_api_users_profile(self) ->GetApiUsersProfileResponse:
        url = '/api/users/profile'
        response = requests.get(url, headers={'Authorization': 'Bearer ' +
            self.token})
        return GetApiUsersProfileResponse(**response.json())

    def options_api_users_profile(self) ->dict:
        url = '/api/users/profile'
        response = requests.options(url, headers={'Authorization': 
            'Bearer ' + self.token})
        return dict(**response.json())

    def get_api_deliveryfees(self) ->GetApiDeliveryfeesResponse:
        url = '/api/deliveryfees'
        response = requests.get(url, headers={'Authorization': 'Bearer ' +
            self.token})
        return GetApiDeliveryfeesResponse(**response.json())

    def options_api_deliveryfees(self) ->dict:
        url = '/api/deliveryfees'
        response = requests.options(url, headers={'Authorization': 
            'Bearer ' + self.token})
        return dict(**response.json())

    def get_api_inventory_promo_5_full(self
        ) ->GetApiInventoryPromo5FullResponse:
        url = '/api/inventory/promo/5/full'
        response = requests.get(url, headers={'Authorization': 'Bearer ' +
            self.token})
        return GetApiInventoryPromo5FullResponse(**response.json())

    def options_api_inventory_promo_5_full(self) ->dict:
        url = '/api/inventory/promo/5/full'
        response = requests.options(url, headers={'Authorization': 
            'Bearer ' + self.token})
        return dict(**response.json())

    def get_api_sliders_5(self) ->GetApiSliders5Response:
        url = '/api/sliders/5'
        response = requests.get(url, headers={'Authorization': 'Bearer ' +
            self.token})
        return GetApiSliders5Response(**response.json())

    def options_api_sliders_5(self) ->dict:
        url = '/api/sliders/5'
        response = requests.options(url, headers={'Authorization': 
            'Bearer ' + self.token})
        return dict(**response.json())

    def get_api_inventory_5_categories_31_products(self
        ) ->GetApiInventory5Categories31ProductsResponse:
        url = '/api/inventory/5/categories/31/products'
        response = requests.get(url, headers={'Authorization': 'Bearer ' +
            self.token})
        return GetApiInventory5Categories31ProductsResponse(**response.json())

    def options_api_inventory_5_categories_31_products(self) ->dict:
        url = '/api/inventory/5/categories/31/products'
        response = requests.options(url, headers={'Authorization': 
            'Bearer ' + self.token})
        return dict(**response.json())

    def get_api_inventory_5_categories_73_products(self
        ) ->GetApiInventory5Categories73ProductsResponse:
        url = '/api/inventory/5/categories/73/products'
        response = requests.get(url, headers={'Authorization': 'Bearer ' +
            self.token})
        return GetApiInventory5Categories73ProductsResponse(**response.json())

    def options_api_inventory_5_categories_73_products(self) ->dict:
        url = '/api/inventory/5/categories/73/products'
        response = requests.options(url, headers={'Authorization': 
            'Bearer ' + self.token})
        return dict(**response.json())

    def get_api_inventory_5_stocks(self) ->GetApiInventory5StocksResponse:
        url = '/api/inventory/5/stocks'
        response = requests.get(url, headers={'Authorization': 'Bearer ' +
            self.token})
        return GetApiInventory5StocksResponse(**response.json())

    def options_api_inventory_5_stocks(self) ->dict:
        url = '/api/inventory/5/stocks'
        response = requests.options(url, headers={'Authorization': 
            'Bearer ' + self.token})
        return dict(**response.json())
