from pydantic import BaseModel, ConfigDict, Field, ValidationError
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Tuple, Type, Union
from enum import Enum

class AuthType(Enum):
  BASIC = 'basic'
  BEARER = 'bearer'

class HTTPMethod(Enum):
  GET = 'GET'
  POST = 'POST'
  PUT = 'PUT'
  PATCH = 'PATCH'
  DELETE = 'DELETE'

class YAMLToPydanticType(Enum):
  string = 'str'
  number = 'float'
  integer = 'int'
  boolean = 'bool'
  array = 'List'
  object = 'Dict'