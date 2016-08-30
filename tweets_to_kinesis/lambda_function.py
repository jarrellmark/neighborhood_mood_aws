from __future__ import print_function
import base64
import json
import os
import xml.etree.ElementTree as ET

import boto3
from textblob import TextBlob

print('Loading function')

def parse_as_polygon(coordinate_string):
    point_strings = coordinate_string.split(' ')
    coordinate_triples = [point_string.split(',') for point_string in point_strings]
    # twitter geo coordinates are long,lat,altitude instead of lat,long so flip it around and ignore altitude
    coordinates = [(float(coordinate_triple[1]), float(coordinate_triple[0])) for coordinate_triple in coordinate_triples]
    return coordinates

# determine if a point is inside a given polygon or not
# Polygon is a list of (x, y) pairs.
# http://www.ariel.com.au/a/python-point-int-poly.html

def point_inside_polygon(x, y, poly):
    n = len(poly)
    inside = False

    p1x, p1y = poly[0]
    for i in range(n+1):
        p2x, p2y = poly[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside

def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))

    tree = ET.parse('Manhattan_Neighborhoods.kml')
    root = tree.getroot()

    kinesis = boto3.client('kinesis')

    for record in event['Records']:
        # Kinesis data is base64 encoded so decode here
        # sample record['kinesis']['data'] pre base64 encode:
        #   '{"message": "really good tweet", "location": [40.7142, -74.0064]}'
        message = json.loads(base64.b64decode(record['kinesis']['data']))

        text_blob = TextBlob(message['tweet'].decode('ascii', errors="replace"))
        sentiment = text_blob.sentiment.polarity

        tweet_location = [message['location'][0], message['location'][1]]
        tweet_neighborhood = None
        for placemark in root.iter('{http://www.opengis.net/kml/2.2}Placemark'):
            name = placemark.find('{http://www.opengis.net/kml/2.2}name').text
            coordinates = ''
            for coordinate in placemark.iter('{http://www.opengis.net/kml/2.2}coordinates'):
                coordinates = coordinate.text
            polygon = parse_as_polygon(coordinates)
            if point_inside_polygon(tweet_location[0], tweet_location[1], polygon):
                tweet_neighborhood = name
                break

        output = {
            'neighborhood': tweet_neighborhood,
            'sentiment': sentiment
        }
        kinesis_response = kinesis.put_records(
            Records=[
                {
                    'Data': json.dumps(output).encode('utf-8'),
                    'PartitionKey': 'string'
                },
            ],
            StreamName='processed_tweets'
        )

        print("Decoded payload: " + str(message))
        print("Decoded sentiment: " + str(sentiment))
        print("output: " + str(json.dumps(output)))
        print("kinesis_response: " + str(kinesis_response))
    return 'Successfully processed {} records.'.format(len(event['Records']))
