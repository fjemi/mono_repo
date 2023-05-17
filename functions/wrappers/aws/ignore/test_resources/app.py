from wrappers.aws import app

response = app.get_response('lambda.list_functions', None)
responses = [
  app.get_response('s3.list_buckets', None),
  app.get_response('s3.list_objects', {'Bucket': 'oj-aws-s3-bucket-01'}),
  app.process_response(
    response=response,
    parse_response='Functions'
  )
]
print(responses)


