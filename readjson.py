import json

def response_OfficeHr(compare_str):
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

def replace_AbbrName(inStr):
    # read file
    myjsfile = open('json\\abbr.json', 'r')
    jsondata = myjsfile.read()

    # Parse
    obj = json.loads(jsondata)
    for i in range(len(obj)):
        for j in range(len(obj[i]['term'])):
            print(obj[i]['term'][j])
            if inStr.find(obj[i]['term'][j]) != -1:
                return obj[i]['term'][j], obj[i]['abbr']
    return "", ""
