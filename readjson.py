import json


def read_json(compare_str):
    # read file
    myjsfile = open('json\campusoffice.json', 'r')
    jsondata = myjsfile.read()

    # Parse
    obj = json.loads(jsondata)

    # print(obj[0]['name'])
    n = 0
    for data in obj:
        if compare_str in obj[n]['name']:
            x = obj[n]['contact']
            y = obj[n]['officehr']
            z = True
        n = n+1
    return x, y, z


# read_json()
