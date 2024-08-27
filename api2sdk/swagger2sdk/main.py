import pdb
import ast
import astor
import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Tuple, Type, Union
from enum import Enum
from swagger2sdk.generate_function import generate_function_for_endpoint
from swagger2sdk.generate_types import generate_types
from swagger2sdk.utils import AuthType, HTTPMethod

swagger_path = '/Users/jasonfan/Documents/code/api2sdk/api2sdk/specs.yml'

def load_yaml(file_path):
  with open(file_path, 'r') as file:
    return yaml.safe_load(file)


def generate_sdk_class(sdk_name: str, auth_type: AuthType) -> ast.ClassDef:
  # SDK should accept different arguments depending on the auth type
  auth_arguments = []
  auth_nodes = []
  if auth_type == AuthType.BASIC:
    auth_arguments.append(ast.arg(arg='username', annotation=ast.Name(id='str', ctx=ast.Load())))
    auth_arguments.append(ast.arg(arg='password', annotation=ast.Name(id='str', ctx=ast.Load())))
    auth_nodes.append(ast.Assign(
      targets=[ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='username', ctx=ast.Store())],
      value=ast.Name(id='username', ctx=ast.Load())
    ))
    auth_nodes.append(ast.Assign(
      targets=[ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='password', ctx=ast.Store())],
      value=ast.Name(id='password', ctx=ast.Load())
    ))
  elif auth_type == AuthType.BEARER:
    auth_arguments.append(ast.arg(arg='token', annotation=ast.Name(id='str', ctx=ast.Load())))
    auth_nodes.append(ast.Assign(
      targets=[ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='token', ctx=ast.Store())],
      value=ast.Name(id='token', ctx=ast.Load())
    ))
    

  args = ast.arguments(
    args=[
      ast.arg(arg='self', annotation=None),
      ast.arg(arg='base_url', annotation=ast.Name(id='str', ctx=ast.Load())),
      *auth_arguments
    ],
    vararg=None,
    kwonlyargs=[],
    kw_defaults=[],
    kwarg=None,
    defaults=[]
  )

  # Create the __init__ method
  init_body = [
    ast.Assign(
      targets=[ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='base_url', ctx=ast.Store())],
      value=ast.Name(id='base_url', ctx=ast.Load())
    ),
    *auth_nodes
  ]

  init_method = ast.FunctionDef(
    name='__init__',
    args=args,
    body=init_body,
    decorator_list=[],
    returns=None
  )

    # Create the base class definition
  class_def = ast.ClassDef(
    name=sdk_name,
    keywords=[],
    bases=[ast.Name(id='BaseModel', ctx=ast.Load())],
    body=[init_method],
    decorator_list=[],
  )

  # Convert AST to source code using ast.unparse
  return class_def

def save_class_to_file(module: ast.Module, file_path: str) -> None:
  code = astor.to_source(module)
  with open(file_path, 'w') as file:
    file.write(code)

def generate_imports() -> List[ast.Import]:
  imports = [
    ast.Import(names=[ast.alias(name='requests', asname=None)]),
    ast.ImportFrom(module='requests.auth', names=[ast.alias(name='HTTPBasicAuth', asname=None)], level=0),
    ast.ImportFrom(module='pydantic', names=[ast.alias(name='BaseModel', asname=None)], level=0),
    ast.ImportFrom(module='typing', names=[
      ast.alias(name='Optional', asname=None), 
      ast.alias(name='Dict', asname=None), 
      ast.alias(name='List', asname=None)], level=0),
  ]
  return imports

def construct_sdk(swagger_path: str, sdk_name: str, sdk_location: str = 'generated', base_url: str = None) -> None:
  swagger = load_yaml(swagger_path)
  base_url = swagger.get('servers', [{}])[0].get('url') if not base_url else base_url
  if not base_url:
    raise ValueError('Base URL is required, but was not provided in the OpenAPI spec or as an argument.')
  auth_type = AuthType.BEARER

  paths = swagger.get('paths', {})
  imports = generate_imports()

  class_def = generate_sdk_class(sdk_name, auth_type)
  types: List[ast.ClassDef] = []

  # Iterate through each path and method. Generate functions to call each endpoint, and types to validate request/response bodies
  for path, methods in paths.items():
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
      _function = generate_function_for_endpoint(endpoint, auth_type, _types)
      class_def.body.append(_function)
      types.extend([t for t in _types if t is not None])

  # Combine the imports, the SDK class, and generated types into a single module
  body = imports + types + [class_def]
  class_module = ast.Module(body=body, type_ignores=[])
  save_class_to_file(class_module, f'{sdk_location}/{sdk_name}.py')

if __name__ == '__main__':
  construct_sdk(swagger_path, 'FinicSDK', 'https://api.finic.com')