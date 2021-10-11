import requests
import json

diastema_analysis = {
  "diastema-token": "diastema-key",
  "analysis-id": "a22afdb473bce",
  "database-id": "METIS",
  "analysis-datetime": "2021-10-06 02:55:45:796",
  "jobs": [
    {
      "id": 1633477964372,
      "step": 1,
      "from": 0,
      "next": [
        2
      ],
      "title": "data-load",
      "save": False,
      "files": ["file1", "file2"],
      "dataset-name": "ships"
    },
    {
      "id": 1633478113563,
      "step": 2,
      "from": 1,
      "next": [
        3
      ],
      "title": "cleaning",
      "save": False,
      "max-shrink": 0.56
    },
    {
      "id": 1633478115115,
      "step": 3,
      "from": 2,
      "next": [
        4
      ],
      "title": "classification",
      "save": False,
      "algorithm": "logistic regression",
      "column": "Grade"
    },
    {
      "id": 1633478116819,
      "step": 4,
      "from": 3,
      "next": [
        0
      ],
      "title": "visualize",
      "save": False
    }
  ],
  "nodes": [
    {
      "_id": 1633477964372,
      "position": {
        "top": 268,
        "left": 344
      },
      "property": "Data Load",
      "type": "Data Load"
    },
    {
      "_id": 1633478113563,
      "position": {
        "top": 273,
        "left": 604
      },
      "property": "Cleaning",
      "field": "",
      "type": "Cleaning"
    },
    {
      "_id": 1633478115115,
      "position": {
        "top": 376.00000762939453,
        "left": 864
      },
      "property": "Select Algorithm",
      "field": "Grade",
      "type": "Classification"
    },
    {
      "_id": 1633478116819,
      "position": {
        "top": 286.00000762939453,
        "left": 1188
      },
      "property": "Visualize",
      "type": "Visualize"
    }
  ],
  "connections": [
    {
      "from": 1633477964372,
      "to": 1633478113563
    },
    {
      "from": 1633478113563,
      "to": 1633478115115
    },
    {
      "from": 1633478115115,
      "to": 1633478116819
    }
  ],
  "automodel": False
}
url = 'http://10.20.20.99:5000' + '/analysis'
data = {
    'json-playbook' : json.dumps(diastema_analysis)
}

files={
    'file1': open('1.csv','rb'),
    'file2': open('2.csv', 'rb'),
    'file3': open('3.csv', 'rb')
}

print("starting the call")
r = requests.post(url, data=data, files=files)
print(r.status_code)
