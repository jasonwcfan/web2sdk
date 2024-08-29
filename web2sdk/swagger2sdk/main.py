import pdb
import ast
import astor
import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Tuple, Type, Union, Callable
from enum import Enum
from swagger2sdk.generate_function import generate_function_for_endpoint
from swagger2sdk.generate_types import generate_types, generate_class_def, ClassField
from swagger2sdk.utils import AuthType, HTTPMethod

swagger_path = '/Users/jasonfan/Documents/code/web2sdk/web2sdk/specs.yml'

def load_yaml(file_path):
  with open(file_path, 'r') as file:
    return yaml.safe_load(file)


def generate_sdk_class(sdk_name: str, auth_type: AuthType) -> ast.ClassDef:
  # SDK should accept different arguments depending on the auth type
  auth_arguments = []
  fields = [
    ClassField(field_name='hostname', field_type='str', required=True)
  ]
  if auth_type == AuthType.BASIC.value:
    fields.extend([ClassField(field_name='username', field_type='str', required=True), ClassField(field_name='password', field_type='str', required=True)])
  elif auth_type == AuthType.BEARER.value:
    fields.extend([ClassField(field_name='token', field_type='str', required=True)])

  class_def = generate_class_def(sdk_name, fields)

  return class_def

def save_class_to_file(module: ast.Module, file_path: str) -> None:
  code = astor.to_source(module)
  with open(file_path, 'w') as file:
    file.write(code)

def generate_imports() -> List[ast.Import]:
  imports = [
    ast.Import(names=[ast.alias(name='json', asname=None)]),
    ast.Import(names=[ast.alias(name='http.client', asname=None)]),
    ast.ImportFrom(module='urllib.parse', names=[ast.alias(name='urlparse', asname=None)], level=0),
    ast.ImportFrom(module='pydantic', names=[ast.alias(name='BaseModel', asname=None)], level=0),
    ast.ImportFrom(module='typing', names=[
      ast.alias(name='Optional', asname=None), 
      ast.alias(name='Dict', asname=None), 
      ast.alias(name='List', asname=None),
      ast.alias(name='Any', asname=None)], level=0),
  ]
  return imports

def construct_sdk(swagger_path: str, 
                  sdk_name: str, 
                  output_path: str, 
                  base_url: str = None, 
                  auth_type: AuthType = AuthType.NONE,
                  progress_callback: Callable[[float], None] = None) -> None:
  swagger = load_yaml(swagger_path)
  base_url = swagger.get('servers', [{}])[0].get('url') if not base_url else base_url
  if not base_url:
    raise ValueError('Base URL is required, but was not provided in the OpenAPI spec or as an argument.')

  paths = swagger.get('paths', {})
  imports = generate_imports()
  class_def = generate_sdk_class(sdk_name, auth_type)
  types: List[ast.ClassDef] = []

  # Iterate through each path and method. Generate functions to call each endpoint, and types to validate request/response bodies
  for index, (path, methods) in enumerate(paths.items()):
    for method, details in methods.items():
      endpoint = {
        'path': path,
        'method': method,
        'name': f"{method.lower()}{path.replace('/', '_').replace('{', '').replace('}', '')}",
        'parameters': details.get('parameters', None),
        'request_body': details.get('requestBody', None),
        'responses': details.get('responses', None)
      }
      _types = generate_types(endpoint)
      _function = generate_function_for_endpoint(endpoint, base_url, auth_type, _types)
      class_def.body.append(_function)
      types.extend([t for t in _types if t is not None])
    if progress_callback:
      progress_callback(float(index+1) / len(paths))

  # Combine the imports, the SDK class, and generated types into a single module
  body = imports + types + [class_def]
  class_module = ast.Module(body=body, type_ignores=[])
  save_class_to_file(class_module, f'{output_path}/{sdk_name}.py')