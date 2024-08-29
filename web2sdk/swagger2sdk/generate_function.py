import ast
from swagger2sdk.utils import AuthType, check_content_type, dash_to_snake
from typing import Tuple, List
from  urllib.parse import urlparse

def content_type_to_ast_node(content_type: str, return_type: str) -> ast.Call:
  if check_content_type(content_type, ['application/json', 'application/x-www-form-urlencoded']):
    # json.loads(data)
    result_node = ast.Call(
      func=ast.Attribute(
        value=ast.Name(id='json', ctx=ast.Load()),
        attr='loads',
        ctx=ast.Load()
      ),
      args=[ast.Name(id='data', ctx=ast.Load())],
      keywords=[]
    )
  else:
    result_node = ast.Name(id='data', ctx=ast.Load())
  return result_node

# Fallback in case a class could not be created for a particular endpoint. Return a primitive type instead.
def get_return_type(content_type: str) -> ast.Name:
  if check_content_type(content_type, ['application/json']):
    return 'dict'
  elif check_content_type(content_type, ['text/html', 'text/plain']):
    return 'str'
  else:
    return 'Any'

def generate_function_for_endpoint(endpoint: dict, base_url: str, auth_type: AuthType, types: Tuple[ast.ClassDef]) -> ast.FunctionDef:
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
    kwonlyargs=[ast.arg(arg='override_headers', annotation=ast.Name(id='dict', ctx=ast.Load()))],
    kw_defaults=[ast.Dict(keys=[], values=[])],
    kwarg=None,
    defaults=[]
  )

  # Return annotation
  return_annotation = ast.Name(id=response_class_name, ctx=ast.Load())

  # Set up http.client connection
  # conn = http.client.HTTPSConnection(self.hostname)
  http_conn_assign = ast.Assign(
    targets=[ast.Name(id='conn', ctx=ast.Store())],
    value=ast.Call(
      func=ast.Attribute(
        value=ast.Name(id='http.client', ctx=ast.Load()),
        attr='HTTPSConnection',
        ctx=ast.Load()
      ),
      args=[ast.Attribute(
        value=ast.Name(id='self', ctx=ast.Load()),
        attr='hostname',
        ctx=ast.Load()
      )],
      keywords=[]
    )
  )

  # Prepare the payload, depending on the request content type
  if request_schema:
    if check_content_type(request_content_type, ['application/json', 'application/x-www-form-urlencoded']):
      payload_assign = ast.Assign(
        targets=[ast.Name(id='payload', ctx=ast.Store())],
        value=ast.Call(
          func=ast.Attribute(
            value=ast.Name(id='json', ctx=ast.Load()),
            attr='dumps',
            ctx=ast.Load()
          ),
          args=[ast.Name(id='request_body', ctx=ast.Load())],
          keywords=[]
        )
      )
    else:
      payload_assign = ast.Assign(
        targets=[ast.Name(id='payload', ctx=ast.Store())],
        value=ast.Name(id='request_body', ctx=ast.Load())
      )

  # Prepare headers
  header_keys = [ast.Constant(value='User-Agent')]
  header_values = [ast.Constant(value='Web2sdk/1.0')]
  if auth_type == AuthType.BASIC.value:
    header_keys.append(ast.Constant(value='Authorization'))
    header_values.append(
      ast.BinOp(
        left=ast.Constant(value='Basic '),
        op=ast.Add(),
        right=ast.Call(
          func=ast.Name(id='base64.b64encode', ctx=ast.Load()),
          args=[ast.BinOp(
            left=ast.BinOp(
              left=ast.Name(id='self.username', ctx=ast.Load()),
              op=ast.Add(),
              right=ast.Constant(value=':')
            ),
            op=ast.Add(),
            right=ast.Name(id='self.password', ctx=ast.Load())
          )],
          keywords=[]
        )
      )
    )
  elif auth_type == AuthType.BEARER.value:
    header_keys.append(ast.Constant(value='Authorization'))
    header_values.append(ast.BinOp(
      left=ast.Constant(value='Bearer '),
      op=ast.Add(),
      right=ast.Name(id='self.token', ctx=ast.Load())
    ))

  headers_assign = ast.Assign(
    targets=[ast.Name(id='headers', ctx=ast.Store())],
    value=ast.Dict(
      keys=header_keys,
      values=header_values
    )
  )

  # Update headers with override headers
  headers_update = ast.Expr(
    value=ast.Call(
      func=ast.Attribute(
        value=ast.Name(id='headers', ctx=ast.Load()),
        attr='update',
        ctx=ast.Load()
      ),
      args=[ast.Name(id='override_headers', ctx=ast.Load())],
      keywords=[]
    )
  )

  # Prepare the request params
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

  # Call the connection request
  # conn.request("GET", "/backend-api/conversations" + "?" + params, body=payload, headers=headers)
  full_url = urlparse(base_url + request_path)
  http_path = full_url.path + "?" if request_parameters else full_url.path
  conn_request = ast.Expr(
    value=ast.Call(
      func=ast.Attribute(
        value=ast.Name(id='conn', ctx=ast.Load()),
        attr='request',
        ctx=ast.Load()
      ),
      args=[
        ast.Constant(value=request_method.upper()),
        ast.BinOp(
          left=ast.BinOp(
            left=ast.Constant(value=http_path),
            op=ast.Add(),
            right=ast.Name(id='params', ctx=ast.Load())
          ),
          op=ast.Add(),
          right=ast.Constant(value="")
        )
      ],
      keywords=[kw for kw in [
        ast.keyword(arg='body', value=ast.Name(id='payload', ctx=ast.Load())) if request_schema else None,
        ast.keyword(arg='headers', value=ast.Name(id='headers', ctx=ast.Load()))
      ] if kw is not None]
    )
  )

  # Get the response
  # res = conn.getresponse()
  response_assign = ast.Assign(
    targets=[ast.Name(id='res', ctx=ast.Store())],
    value=ast.Call(
      func=ast.Attribute(
        value=ast.Name(id='conn', ctx=ast.Load()),
        attr='getresponse',
        ctx=ast.Load()
      ),
      args=[],
      keywords=[]
    )
  )

  # Read the response
  # data = res.read().decode("utf-8")
  data_assign = ast.Assign(
    targets=[ast.Name(id='data', ctx=ast.Store())],
    value=ast.Call(
      func=ast.Attribute(
        value=ast.Call(
          func=ast.Attribute(
            value=ast.Name(id='res', ctx=ast.Load()),
            attr='read',
            ctx=ast.Load()
          ),
          args=[],
          keywords=[]
        ),
        attr='decode',
        ctx=ast.Load()
      ),
      args=[ast.Str(s='utf-8')],
      keywords=[]
    )
  )

  # Return the decoded data
  return_stmt = ast.Return(
    value=content_type_to_ast_node(response_content_type, response_class_name)
  )

  # Construct function body with the URL and response assignments
  function_body = [
    http_conn_assign,
    parameter_assign,
    headers_assign,
    headers_update,
    payload_assign if request_schema else None,
    conn_request,
    response_assign,
    data_assign,
    return_stmt
  ]
  
  # Remove any None values from the function body
  function_body = [stmt for stmt in function_body if stmt is not None]

  # Create the function definition
  function_def = ast.FunctionDef(
    name=dash_to_snake(request_name),
    args=args,
    body=function_body,
    decorator_list=[],
    returns=return_annotation
  )

  return function_def