import os
import requests
import json
from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from marshmallow import Schema, fields

class WeatherQuerySchema(Schema):
    key1 = fields.Str(required=True)
    key2 = fields.Str(required=True)

app = Flask(__name__)
api = Api(app)
schema = WeatherQuerySchema()


api_key = os.environ['API_KEY']



class Weather(Resource):
    def get(self):
        errors = schema.validate(request.args)
        print(request.args)
        url = "https://api.openweathermap.org/data/2.5/weather?lat=%s&lon=%s&appid=%s" % (request.args['lat'], request.args['lon'], api_key)
        response = requests.get(url)
        data = json.loads(response.text)
        return data

api.add_resource(Weather, '/')

if __name__ == '__main__':
    app.run(debug=True,port=8081)
