import json
import os
from os.path import join, dirname

from dotenv import load_dotenv
import boto3
import tweepy

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

auth = tweepy.OAuthHandler(
    os.environ.get("TWITTER_CONSUMER_TOKEN"),
    os.environ.get("TWITTER_CONSUMER_SECRET")
)
auth.set_access_token(
    os.environ.get("TWITTER_ACCESS_TOKEN"),
    os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")
)

kinesis = boto3.client(
    'kinesis',
    aws_access_key_id=os.environ.get("KINESIS_AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("KINESIS_AWS_SECRET_ACCESS_KEY")
)

api = tweepy.API(auth)

class MyStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        if status.geo is not None:
            print "status.geo: " + str(status.geo)
            if status.geo['type'] == 'Point':
                message = {
                    'tweet': status.text,
                    'location': status.geo['coordinates']
                }
                response = kinesis.put_records(
                    Records=[
                        {
                            'Data': json.dumps(message).encode('utf-8'),
                            'PartitionKey': 'string'
                        },
                    ],
                    StreamName='tweets'
                )
                print "message: " + str(json.loads(json.dumps(message)))
                print "kinesis response: " + str(response)
                print ""
            else:
                print "geo not a point"
                print ""
        else:
            print "no place"
            print ""

    def on_error(self, status_code):
        if status_code == 420:
            return False

stream_listener = MyStreamListener()
stream = tweepy.Stream(auth = api.auth, listener=stream_listener)

# Only listen for tweets in NYC
stream.filter(locations=[-74,40,-73,41])
