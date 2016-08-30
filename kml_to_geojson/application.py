import json
import os
import xml.etree.ElementTree as ET

def parse_as_polygon(coordinate_string):
    point_strings = coordinate_string.split(' ')
    coordinate_triples = [point_string.split(',') for point_string in point_strings]
    coordinates = [[float(coordinate_triple[0]), float(coordinate_triple[1])] for coordinate_triple in coordinate_triples]
    return coordinates

tree = ET.parse('Manhattan_Neighborhoods.kml')
root = tree.getroot()

geojson = {
  'type': 'FeatureCollection',
  'features': []
}

index = 0
for placemark in root.iter('{http://www.opengis.net/kml/2.2}Placemark'):
    name = placemark.find('{http://www.opengis.net/kml/2.2}name').text
    coordinates = ''
    for coordinate in placemark.iter('{http://www.opengis.net/kml/2.2}coordinates'):
        coordinates = coordinate.text
    polygon = parse_as_polygon(coordinates)

    feature = {
        'type': 'Feature',
        'id': str(index),
        'properties': {
            'name': name
        },
        'geometry': {
            'type': 'Polygon',
            'coordinates': [
                polygon
            ]
        }
    }
    geojson['features'].append(feature)

    index += 1

print json.dumps(geojson)
geo_file = open('Manhattan_Neighborhoods.geojson', 'w')
geo_file.write(json.dumps(geojson))
