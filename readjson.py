import json

def response_OfficeHr(compare_str):
    # read file
    myjsfile = open('json/campusoffice.json', 'r')
    jsondata = myjsfile.read()

    # Parse
    obj = json.loads(jsondata)

    # print(obj[i]['name'])
    for i in range(len(obj)):
        if compare_str in obj[i]['name']:
            return obj[i]['contact'], obj[i]['officehr'], True
    return None, None, False

def response_nonjupas_deadline(compare_str):
    # read file
    myjsfile = open('json/_nonjupas.json', 'r')
    jsondata = myjsfile.read()

    # Parse
    obj = json.loads(jsondata)

    # print(obj[i]['name'])
    for i in range(len(obj)):
        if compare_str in obj[i]['name']:
            return obj[i]['deadline'], obj[i]['link'], True
    return None, None, False

def replace_AbbrName(inStr):
    # return text initiatation
    resultTxt = inStr

    # read file
    myjsfile = open('json/abbr.json', 'r')
    jsondata = myjsfile.read()

    # Parse
    obj = json.loads(jsondata)
    for i in range(len(obj)):
        for j in range(len(obj[i]['term'])):
            if inStr.find(obj[i]['term'][j]) != -1:
                resultTxt = resultTxt.replace(obj[i]['term'][j], obj[i]['abbr'])                
    return resultTxt

def display_json(obj):
    print(type(obj))
    if isinstance(obj, dict):
        for key in obj:
            print(f'[{key}]:')
            display_json(obj[key])
    elif isinstance(obj, list):
        for i in range(len(obj)):
            print(f'[{i}]:')
            display_json(obj[i])
    elif isinstance(obj, str):
        print(f': {obj}')


if __name__ == "__main__":
    inFile = open('json/campus_have.json', 'r')
    fileRead = inFile.read()
    jsonIn = json.loads(fileRead)
    print(f'len: {len(jsonIn)}')
    for key in jsonIn:
        if isinstance(jsonIn[key], dict):
            for secondKey in jsonIn[key]:
                if isinstance(jsonIn[key][secondKey], list):
                    for obj_index in range(len(jsonIn[key][secondKey])):
                        print(f'[{key}][{secondKey}][{obj_index}]: {type(jsonIn[key][secondKey][obj_index])} {jsonIn[key][secondKey][obj_index]}')
                elif isinstance(jsonIn[key][secondKey], dict):
                    for thirdkey in jsonIn[key][secondKey]:
                        print(f'[{key}][{secondKey}][{thirdkey}]: {type(jsonIn[key][secondKey][thirdkey])} {jsonIn[key][secondKey][thirdkey]}')
                elif isinstance(jsonIn[key][secondKey], str):
                    print(f'[{key}][{secondKey}]: {type(jsonIn[key][secondKey])} {jsonIn[key][secondKey]}')
        elif isinstance(jsonIn[key], list):
            for obj_index in range(len(jsonIn[key])):
                print(f'[{key}][{obj_index}]: {type(jsonIn[key][obj_index])} {jsonIn[key][obj_index]}')
        elif isinstance(jsonIn[key], str):
            print(f'[{key}]: {type(jsonIn[key])} {jsonIn[key]}')

    display_json(jsonIn)
