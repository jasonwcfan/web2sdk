import ast
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Tuple, Type, Union
from enum import Enum
from swagger2sdk.utils import YAMLToPydanticType, check_content_type, snake_to_pascal, dash_to_snake, strip_special_chars

class ClassField(BaseModel):
  field_name: str
  field_type: str
  required: bool

def path_to_class_name(path: str) -> str:
  """
  Converts a URL path to a class name.
  """
  return strip_special_chars(snake_to_pascal(dash_to_snake(path)))
   

def generate_class_def(class_name: str, fields: List[ClassField]) -> ast.ClassDef:
    """
    Generates a Pydantic class definition with the given class name and fields.
    """
    # Create the class definition
    class_def = ast.ClassDef(
        name=class_name,
        bases=[ast.Name(id='BaseModel', ctx=ast.Load())],  # Inherit from Pydantic's BaseModel
        body=[],
        decorator_list=[]
    )
    
    # Add each field as a class attribute
    for field in fields:
      field_name, field_type, required = strip_special_chars(dash_to_snake(field.field_name)), field.field_type, field.required
      
      # If the field is not required, wrap the type in Optional
      if not required:
        field_annotation = ast.Subscript(
          value=ast.Name(id='Optional', ctx=ast.Load()),
          slice=ast.Index(value=ast.Name(id=field_type, ctx=ast.Load())),
          ctx=ast.Load()
        )
      else:
        field_annotation = ast.Name(id=field_type, ctx=ast.Load())
      
      # Add the field to the class body. If the field is not required, assign a default value of None.
      field_node = ast.AnnAssign(
        target=ast.Name(id=field_name, ctx=ast.Store()),
        annotation=field_annotation,
        value=None if required else ast.Constant(value=None),
        simple=True
      )
      
      class_def.body.append(field_node)
    
    return class_def

def parse_request_body(request_body: dict) -> List[ClassField]:
  if not request_body:
    return []
  fields = []
  content: dict = request_body['content']
  required: bool = request_body.get('required', False)

  for content_type, schema in content.items():
    if check_content_type(content_type, ['application/json', 'application/x-www-form-urlencoded']):
      schema = schema['schema']
      schema_type = YAMLToPydanticType[schema.get('type')]
      if schema.get('type') == 'object':
        required_properties: List[str] = schema.get('required', [])
        properties: dict = schema.get('properties', {})
        for name, prop in properties.items():
          field_type: str = YAMLToPydanticType[prop['type']]
          field_required: bool = name in required_properties
          fields.append(ClassField(field_name=name, field_type=field_type, required=field_required))
      else:
        fields.append(ClassField(field_name='data', field_type=schema_type, required=required))
  return fields

def parse_response_body(response_body: dict) -> List[ClassField]:
  if not response_body:
    return []
  fields = []
  content: dict = response_body['content']
  for content_type, schema in content.items():
    if content_type == 'application/json':
      schema = schema['schema']
      schema_type = schema.get('type')
      if schema_type == 'object':
        required_properties: List[str] = schema.get('required', [])
        properties: dict = schema.get('properties', {})
        for name, prop in properties.items():
          field_type: str = YAMLToPydanticType[prop['type']]
          is_required: bool = name in required_properties
          fields.append(ClassField(field_name=name, field_type=field_type, required=is_required))
      elif schema_type == 'array':
        item_type = schema['items'].get('type', 'unknown')
        fields.append(ClassField(field_name='data', field_type=f'List[{YAMLToPydanticType[item_type]}]', required=True))
      else:
        fields.append(ClassField(field_name='data', field_type=YAMLToPydanticType[schema_type], required=True))
  return fields

def generate_types(endpoint: dict) -> Tuple[ast.ClassDef]:
  # Extract endpoint details
  request_path: str = endpoint['path']
  request_name: str = snake_to_pascal(endpoint['name'])
  request_method: str = endpoint['method']
  request_parameters: dict = endpoint['parameters']
  request_body: dict = endpoint['request_body']
  responses: dict = endpoint['responses']


  # Generate Pydantic class for request parameters
  request_parameters_class = None
  if request_parameters:
    request_parameters_fields = []
    for param in request_parameters:
      field_type = YAMLToPydanticType[param['schema']['type']]
      field_name = param['name']
      required = param.get('required', False)
      request_parameters_fields.append(ClassField(field_name=field_name, field_type=field_type, required=required))
    if len(request_parameters_fields) > 0:
      request_parameters_class = generate_class_def(f'{path_to_class_name(request_name)}RequestParameters', request_parameters_fields)

  # Generate Pydantic class for request body
  request_body_class = None
  if request_body:
    request_body_fields = parse_request_body(request_body)
    if len(request_body_fields) > 0:
      request_body_class = generate_class_def(f'{path_to_class_name(request_name)}RequestBody', request_body_fields)

  # Generate Pydantic classes for responses
  successful_response = responses.get('200')
  response_class = None
  if successful_response:
    response_fields = parse_response_body(successful_response)
    if len(response_fields) > 0:
      response_class = generate_class_def(f'{path_to_class_name(request_name)}Response', response_fields)

  
  return (request_parameters_class, request_body_class, response_class)