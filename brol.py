import ujson
import datetime
from model.Client import Client
from django.forms.models import model_to_dict
from bson import json_util
import json

# data = '{"dateLogin":1524594373,"dateLogout":null,"email":"mlkj","messages":[],"name":"qdsfqsf","nickname":"lkqsdjmf","online":true}'
# dc = json.loads(data, object_hook=json_util.object_hook)
# print(dc)
# # print(datetime.datetime(dc["dateLogin"])

# cl = Client("Test", "jan", "jlkq")
# test = json.dumps(cl.__dict__, default=json_util.default)
# tlksdj = json.loads(data, object_hook=json_util.object_hook)
# print(tlksdj)

# # print(test)

# cl = Client("Jamie", "James", "meisje")
# jsonstring = json.dumps(cl.__dict__, default=json_util.default)
# print(jsonstring)
# print(json.loads(jsonstring, object_hook=json_util.object_hook))
# print(Client())

print(datetime.datetime.now())