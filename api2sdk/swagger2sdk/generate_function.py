import ast
from swagger2sdk.types import AuthType
from typing import Tuple

def generate_function_for_endpoint(endpoint: dict, auth_type: AuthType, types: Tuple[ast.ClassDef]) -> ast.FunctionDef:
  # Extract endpoint details
  request_path: str = endpoint['path']
  request_name: str = endpoint['name']
  request_parameters: dict = endpoint['parameters']
  request_method: str = endpoint['method']
  request_schema: dict = endpoint['request_body']
  request_parameters_class_name = types[0].name if types[0] else 'dict'
  request_body_class_name = types[1].name if types[1] else 'dict'
  response_class_name = types[2].name if types[2] else 'dict'

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
  if request_parameters:
    url_assign = ast.Assign(
      targets=[ast.Name(id='url', ctx=ast.Store())],
      value=ast.BinOp(
        left=ast.Constant(value=request_path + "?"),
        op=ast.Add(),
        right=ast.Call(
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
    )
  else:
    url_assign = ast.Assign(
      targets=[ast.Name(id='url', ctx=ast.Store())],
      value=ast.Constant(value=request_path)
    )

  # Construct the HTTP request using the requests library
  keyword_args = []
  if request_schema:
    keyword_args.append(ast.keyword(arg='json', value=ast.Name(id='request_body', ctx=ast.Load())))
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
  response_class_call = ast.Call(
      func=ast.Name(id=response_class_name, ctx=ast.Load()),
      args=[],
      keywords=[response_json_kwarg]
  )
  # Return statement
  return_stmt = ast.Return(
    value=response_class_call
  )

  # Construct function body with the URL and response assignments
  function_body = [
    url_assign,
    response_assign,
    return_stmt
  ]

  # Create the function definition
  function_def = ast.FunctionDef(
    name=request_name,
    args=args,
    body=function_body,
    decorator_list=[],
    returns=return_annotation
  )

  return function_def