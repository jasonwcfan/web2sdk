import re
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Tuple, Type, Union
from enum import Enum

class AuthType(Enum):
  BASIC = 'basic'
  BEARER = 'bearer'
  NONE = 'none'

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

def check_content_type(input_string: str, patterns: List[str]):
    regex_pattern = "|".join(re.escape(pattern) for pattern in patterns)
    if re.search(regex_pattern, input_string):
        return True
    return False

def snake_to_pascal(snake_str: str) -> str:
    components = snake_str.split('_')
    return ''.join(x.capitalize() for x in components)

def dash_to_snake(dash_str: str) -> str:
    return dash_str.replace('-', '_')