import json


def read_json(compare_str):
    # read file
    myjsfile = open('json\campusoffice.json', 'r')
    jsondata = myjsfile.read()

    # Parse
    obj = json.loads(jsondata)

    # print(obj[i]['name'])
    for i in range(len(obj)):
        if compare_str in obj[i]['name']:
            return obj[i]['contact'], obj[i]['officehr'], True
    return None, None, False


# read_json()
