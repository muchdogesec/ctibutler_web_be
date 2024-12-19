# your_app/management/commands/your_command.py
import os
import json
import requests
import yaml

from django.core.management.base import BaseCommand
from django.conf import settings

CTIBUTLER_SERVICE_BASE_URL = settings.CTIBUTLER_SERVICE_BASE_URL


class CtiButlerSchemaGenerator():
    def get_paths(self, data_json):
        path_items = data_json["paths"].items()
        filtered_paths = list(filter(lambda item: "get" in item[1] and "schema" not in item[0] and "jobs" not in item[0], path_items))
        path_dict = {}
        security_requirement = [{'api_key': []}]
        for key, value in filtered_paths:
            get_value = value["get"]
            get_value['security'] = security_requirement
            path_dict['/ctibutler_api' + key] = {"get": get_value}
        return path_dict

    def get_schema_filename(self):
        return os.path.join('ctibutler_api', 'templates', 'ctibutler_api', 'schema.json')

    def generate(self):
        res = requests.get(CTIBUTLER_SERVICE_BASE_URL + '/api/schema/')
        data_json = yaml.safe_load(res.text)
        data_json["paths"] = self.get_paths(data_json)
        data_json['components']['securitySchemes'] = {
            'api_key': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'API-KEY'
            }
        }
        data_json['security'] = [{
            'api_key': []
        }]

        schema_filename = self.get_schema_filename()
        with open(schema_filename, 'w') as file:
            file.write(json.dumps(data_json))


class AdminCtiButlerSchemaGenerator(CtiButlerSchemaGenerator):
    def get_paths(self, data_json):
        path_items = data_json["paths"].items()
        filtered_paths = list(filter(lambda item: True, path_items))
        path_dict = {}
        security_requirement = [{'api_key': []}]
        for key, value in filtered_paths:
            if 'api/schema/' in key:
                continue
            path_dict['/ctibutler_api/admin' + key] = value
        return path_dict

    def get_schema_filename(self):
        return os.path.join('ctibutler_api', 'templates', 'ctibutler_api', 'admin-schema.json')
    
        
class Command(BaseCommand):
    
    def handle(self, *args, **kwargs):
        print("Generating User Schema")
        CtiButlerSchemaGenerator().generate()
        
        print("Generating Admin Schema")
        AdminCtiButlerSchemaGenerator().generate()
