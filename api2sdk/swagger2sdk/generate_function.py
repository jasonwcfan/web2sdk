import ast
from swagger2sdk.utils import AuthType, check_content_type, dash_to_snake
from typing import Tuple, List

def content_type_to_ast_node(content_type: str, class_name: str) -> ast.Call:
  if check_content_type(content_type, ['application/json']):
    # Get response.json()
    response_json_attr = ast.Attribute(
        value=ast.Name(id='response', ctx=ast.Load()),
        attr='json',
        ctx=ast.Load()
    )
    response_json_call = ast.Call(
        func=response_json_attr,
        args=[],
        keywords=[]
    )
    # Instantiate the response class with response.json()
    response_json_kwarg = ast.keyword(
      arg=None,  # None indicates **kwargs
      value=response_json_call
    )
    result_node = ast.Call(
        func=ast.Name(id=class_name, ctx=ast.Load()),
        args=[],
        keywords=[response_json_kwarg]
    )
  elif check_content_type(content_type, ['text/html', 'text/plain']):
    result_node = ast.Attribute(
      value=ast.Name(id='response', ctx=ast.Load()),
      attr='text',
      ctx=ast.Load()
    )
  else:
    result_node = ast.Name(id='response', ctx=ast.Load())
  return result_node

# Fallback in case a class could not be created for a particular endpoint. Return a primitive type instead.
def get_return_type(content_type: str) -> ast.Name:
  if check_content_type(content_type, ['application/json']):
    return 'dict'
  elif check_content_type(content_type, ['text/html', 'text/plain']):
    return 'str'
  else:
    return 'Any'

def generate_function_for_endpoint(endpoint: dict, auth_type: AuthType, types: Tuple[ast.ClassDef]) -> ast.FunctionDef:
  # Extract endpoint details
  request_path: str = endpoint['path']
  request_name: str = endpoint['name']
  request_parameters: dict = endpoint['parameters']
  request_method: str = endpoint['method']
  request_schema: dict = endpoint['request_body']
  request_content_type: str = next(iter(request_schema['content'].keys()), None) if request_schema else None
  response_content: dict = endpoint['responses'].get('200', {}).get('content', {})
  response_content_type: str = next(iter(response_content.keys()), "")
  
  request_parameters_class_name = types[0].name if types[0] else 'dict'
  request_body_class_name = types[1].name if types[1] else 'dict'
  response_class_name = types[2].name if types[2] else get_return_type(response_content_type)

  # Construct the function arguments
  args = ast.arguments(
    args=[arg for arg in [
      ast.arg(arg='self', annotation=None),
      ast.arg(arg='request_parameters', annotation=ast.Name(id=request_parameters_class_name, ctx=ast.Load())) if request_parameters else None,
      ast.arg(arg='request_body', annotation=ast.Name(id=request_body_class_name, ctx=ast.Load())) if request_schema else None
    ] if arg is not None],
    vararg=None,
    kwonlyargs=[],
    kw_defaults=[],
    kwarg=None,
    defaults=[]
  )

  # Return annotation
  return_annotation = ast.Name(id=response_class_name, ctx=ast.Load())

  # Construct the URL with parameters (dynamic based on `request_parameters`)
  path_assign = ast.Assign(
    targets=[ast.Name(id='path', ctx=ast.Store())],
    value=ast.Constant(value=request_path)
  )
  if request_parameters:
    parameter_assign = ast.Assign(
      targets=[ast.Name(id='params', ctx=ast.Store())],
      value=ast.Call(
        func=ast.Attribute(
          value=ast.Str(s="&"),
          attr="join",
          ctx=ast.Load()
        ),
        args=[ast.ListComp(
          elt=ast.BinOp(
            left=ast.BinOp(
              left=ast.Name(id='k', ctx=ast.Load()),
              op=ast.Add(),
              right=ast.Constant(value="=")
            ),
            op=ast.Add(),
            right=ast.Name(id='v', ctx=ast.Load())
          ),
          generators=[
            ast.comprehension(
              target=ast.Tuple(elts=[
                ast.Name(id='k', ctx=ast.Store()), 
                ast.Name(id='v', ctx=ast.Store())], ctx=ast.Store()),
              iter=ast.Call(
                func=ast.Attribute(
                  value=ast.Name(id='request_parameters', ctx=ast.Load()),
                  attr='items',
                  ctx=ast.Load()
                ),
                args=[], keywords=[]
              ),
              ifs=[], is_async=0
            )
          ]
        )],
        keywords=[]
      )
    )
  else:
    parameter_assign = ast.Assign(
      targets=[ast.Name(id='params', ctx=ast.Store())],
      value=ast.Constant(value="")
    )
  
  # Combine the base_url, path, and parameters into the final url_assign
  url_assign = ast.Assign(
    targets=[ast.Name(id='url', ctx=ast.Store())],
    value=ast.BinOp(
      left=ast.BinOp(
        left=ast.Name(id='self.base_url', ctx=ast.Load()),
        op=ast.Add(),
        right=ast.Name(id='path', ctx=ast.Load())
      ),
      op=ast.Add(),
      right=ast.Name(id='params', ctx=ast.Load())
    )
  )

  # Construct the HTTP request using the requests library
  keyword_args = []
  if request_schema:
    if check_content_type(request_content_type, ['application/json']):
      keyword_args.append(ast.keyword(arg='json', value=ast.Name(id='request_body', ctx=ast.Load())))
    elif check_content_type(request_content_type, ['application/x-www-form-urlencoded']):
      keyword_args.append(ast.keyword(arg='data', value=ast.Call(
        func=ast.Attribute(
          value=ast.Name(id='request_body', ctx=ast.Load()),
          attr='dict',
          ctx=ast.Load()
        ),
        args=[],
        keywords=[]
      )))
  if auth_type == AuthType.BASIC:
    keyword_args.append(ast.keyword(arg='auth', value=ast.Call(
      func=ast.Name(id='HTTPBasicAuth', ctx=ast.Load()),
      args=[
        ast.Name(id='self.username', ctx=ast.Load()), 
        ast.Name(id='self.password', ctx=ast.Load())
      ],
      keywords=[]
    )))
  elif auth_type == AuthType.BEARER:
    keyword_args.append(ast.keyword(arg='headers', value=ast.Dict(
      keys=[ast.Constant(value='Authorization')],
      values=[ast.BinOp(
        left=ast.Constant(value='Bearer '),
        op=ast.Add(),
        right=ast.Name(id='self.token', ctx=ast.Load())
      )]
    )))

  request_call = ast.Call(
    func=ast.Attribute(
      value=ast.Name(id='requests', ctx=ast.Load()),
      attr=request_method.lower(),
      ctx=ast.Load()
    ),
    args=[ast.Name(id='url', ctx=ast.Load())],
    keywords=keyword_args
  )

  # Assign the response to a variable
  response_assign = ast.Assign(
    targets=[ast.Name(id='response', ctx=ast.Store())],
    value=request_call
  )

  response_node = content_type_to_ast_node(response_content_type, response_class_name)
  # Return statement
  return_stmt = ast.Return(
    value=response_node
  )

  # Construct function body with the URL and response assignments
  function_body = [
    path_assign,
    parameter_assign,
    url_assign,
    response_assign,
    return_stmt
  ]

  # Create the function definition
  function_def = ast.FunctionDef(
    name=dash_to_snake(request_name),
    args=args,
    body=function_body,
    decorator_list=[],
    returns=return_annotation
  )

  return function_def