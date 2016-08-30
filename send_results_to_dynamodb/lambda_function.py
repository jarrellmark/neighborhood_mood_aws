from __future__ import print_function

import base64
from decimal import *
import json

import boto3

print('Loading function')

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

# sample message pre base64 encode:
#   {"average sentiment": 0.5, "neighborhood": "Wall Street"}
#   base64:
#     eyJhdmVyYWdlIHNlbnRpbWVudCI6IDAuNSwgIm5laWdoYm9yaG9vZCI6ICJXYWxsIFN0cmVldCJ9
def send_results_to_dynamodb(event, context):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('neighborhood_sentiments')

    for record in event['Records']:
        payload = json.loads(base64.b64decode(record['kinesis']['data']))
        print("Decoded payload: " + str(payload))

        dynamodb_response = table.put_item(
           Item={
                'neighborhood': payload['neighborhood'],
                'sentiment': Decimal(str(payload['average_sentiment']))
            }
        )
        print("Dynamodb response:")
        print(json.dumps(dynamodb_response, indent=4, cls=DecimalEncoder))

    return 'Successfully processed {} records.'.format(len(event['Records']))
