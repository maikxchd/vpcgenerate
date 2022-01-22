from flask import Flask, request
from flask_restful import Resource, Api
from awsgen import VpcConnection

app = Flask(__name__)
api = Api(app)


class NewVpc(Resource):
    def put(self):
        vpc = request.get_json()
        my_vpc = VpcConnection(vpc['name'], vpc['account'], vpc['ref'], vpc['vlan'], vpc['ipv4_network'],
                               vpc['bgp_auth_key'], vpc['bgp_community'],vpc['region_id'], serve=True)
        return {"route_map": my_vpc.vpc_route_map, "config": my_vpc.vpc_config}

api.add_resource(NewVpc, '/')

if __name__ == '__main__':
    app.run(debug=True)



"""
PYTHON SAMPLE:
import requests

url = "http://localhost:5000/"

payload = "{\"name\":\"test\",\n\"account\":1111111,\n\"ref\":\"dxcon-fgsezsn1\",\n\"vlan\":100,\n\"ip4_network\":\"1.1.1.0/31\",\n\"bgp_auth_key\":\"adfjalkdsjflajd\",\n\"bgp_community\":\"10001\"\n}"
headers = {
    'content-type': "application/json",
    'cache-control': "no-cache",
    'postman-token': "95c207b3-75cc-0373-796b-9f2de98ac3e7"
    }

response = requests.request("PUT", url, data=payload, headers=headers)

print(response.text)


---------------
CURL SAMPLE:
curl -X PUT \
  http://localhost:5000/ \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/json' \
  -H 'postman-token: 6905c439-49aa-f8b3-93c9-9d99cae68ba3' \
  -d '{"name":"test",
"account":1111111,
"ref":"dxcon-fgsezsn1",
"vlan":100,
"ip4_network":"1.1.1.0/31",
"bgp_auth_key":"adfjalkdsjflajd",
"bgp_community":"10001"
}'


---------------
WGET SAMPLE
wget --quiet \
  --method PUT \
  --header 'content-type: application/json' \
  --header 'cache-control: no-cache' \
  --header 'postman-token: 99b80cc9-1d38-4ea5-94b6-1b332dfbdc39' \
  --body-data '{"name":"test",\n"account":1111111,\n"ref":"dxcon-fgsezsn1",\n"vlan":100,\n"ip4_network":"1.1.1.0/31",\n"bgp_auth_key":"adfjalkdsjflajd",\n"bgp_community":"10001"\n}' \
  --output-document \
  - http://localhost:5000/

"""