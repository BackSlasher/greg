# Defines a server using lambda functions

import json

# Required event template (works as a contract):
"""
{
        "accountId": "$context.identity.accountId",
        "apiId": "$context.apiId",
        "apiKey": "$context.identity.apiKey",
        "caller": "$context.identity.caller",
        "headers": {
      #foreach( $key in $input.params().header.keySet() )
          "$key": "$util.escapeJavaScript($input.params().header.get($key))"#if( $foreach.hasNext ),#end
      #end
        },
        "httpMethod": "$context.httpMethod",
        "path": "$context.resourcePath",
        "pathParameters": {
      #foreach( $key in $input.params().path.keySet() )
          "$key": "$util.escapeJavaScript($input.params().path.get($key))"#if( $foreach.hasNext ),#end
      #end
        },
        "queryParameters": {
      #foreach( $key in $input.params().querystring.keySet() )
          "$key": "$util.escapeJavaScript($input.params().querystring.get($key))"#if( $foreach.hasNext ),#end
      #end
        },
        "requestId": "$context.requestId",
        "requestParameters": $input.json('$'),
        "resourceId": "$context.resourceId",
        "sourceIp": "$context.identity.sourceIp",
        "stage": "$context.stage",
        "user": "$context.identity.user",
        "userAgent": "$context.identity.userAgent",
        "userArn": "$context.identity.userArn"
}
"""

# Invoke using greg.lambda.lambda_handler

def lambda_handler(event, context):
  # Extract provider name from querystring
  payload = json.dumps(event['requestParameters']) #XXX it will be just parsed back to JSON, but this keeps compatibility with current contract
  headers = event['headers']
  querystring = event['queryParameters']
  path = event['path']
  import greg.logic
  if path == '/repo':
      greg.logic.repo(event['queryParameters']['provider'],payload,headers,querystring)
  elif path == '/build':
      greg.logic.build(event['queryParameters']['builder'],payload,headers,querystring)
  else:
      raise Exception('Unknown method')
