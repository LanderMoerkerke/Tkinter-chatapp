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

# print(datetime.datetime.now())

# obj = [{"test": "jefke"}, "nickname"]
# jsonstring = json.dumps(obj)
# print(jsonstring)
# print(json.loads(jsonstring))

# test = json.loads('{"status": "error"}')
# # test = "ok"
# if isinstance(test, dict) and "status" in test.keys():
#     print("ok")

# clients = [{
#     'name': 'jan',
#     'nickname': 'jan',
#     'email': 'jan',
#     'dateLogin': datetime.datetime(2018, 5, 4, 20, 34, 55, 833000),
#     'dateLogout': None,
#     'online': True,
#     'messages': []
# }, {
#     'name': 'karel',
#     'nickname': 'karel',
#     'email': 'karel',
#     'dateLogin': datetime.datetime(2018, 5, 4, 20, 35, 7, 502000),
#     'dateLogout': None,
#     'online': True,
#     'messages': []
# }]
# lstOnline = [client for client in clients if client["online"]]
# print(lstOnline)
# test = "bljqlfj lldkqsfj closed"
# print(test[-6:])

clients = []
for i in range(3):
    cl = Client("Jamie", "James", i)
    clients.append(cl)
    if i == 2:
        del cl
        # print(cl)

print(clients)