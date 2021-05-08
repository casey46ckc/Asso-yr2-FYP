import configparser
import json
import logging
import time
import readjson
from copy import deepcopy 
from hashlib import md5



import requests

config = configparser.ConfigParser()
config.read('config.ini')

logger = logging.getLogger(__name__)

# Load data from /json/*.json files
li_jsonFiles = readjson.read_path_jsons('json/responses/')

# String for comparison
# UGC-funded
cityu_str = ['city university of hong kong', 'city u', 'cityu']
hkbu_str = ['hong kong baptist university', 'hkbu']
lu_str = ['lingnan university', 'lu', 'lingu', 'ling u']
cuhk_str = ['the chinese university of hong kong', 'cuhk']
edu_str = ['the education university of hong kong', 'edu', 'ed u']
polyu_str = ['the hong kong polytechnic university', 'polyu', 'poly u']
hkust_str = [
    'the hong kong university of science and technology', 'hkust', 'ust']
hku_str = ['the university of hong kong', 'hku']
# Self-funded
hsu_str = ['hang seng university of hong kong', 'hang seng u', 'hsu']
syu_str = ['hong kong shue yan university', 'shue yan', 'syu']
hkou_str = ['the open university of hong kong', 'hkou',
            'open u', 'hong kong metropolitan university', 'hkmu']
# public exam
publicexam_str = ['ielts', 'igcse', 'igcse english', 'igcse chinese', 'toefl']

# nonjupas admission link
cityu_adm_link = 'https://www.admo.cityu.edu.hk/direct/'
hkbu_adm_link = 'https://admissions.hkbu.edu.hk/en/'
lu_adm_link = 'https://www.ln.edu.hk/admissions/ug/non-jupas/general-notes-to-applicants'
cuhk_adm_link = 'http://admission.cuhk.edu.hk/non-jupas-senior/application-details.html'
edu_adm_link = 'https://www.eduhk.hk/onlineappl/'
polyu_adm_link = 'https://www38.polyu.edu.hk/eAdmission/index.do'
hkust_adm_link = 'https://join.ust.hk/apply'
hku_adm_link = 'https://aal.hku.hk/admissions/international/admissions-information'

# for granted UNIVERSITY, source from wikipedia
li_u_str = ['1. City University of Hong Kong',
            '2. Hong Kong Baptist University',
            '3. Lingnan University',
            '4. The Chinese University of Hong Kong',
            '5. The Education University of Hong Kong',
            '6. The Hong Kong Polytechnic University',
            '7. The Hong Kong University of Science and Technology',
            '8. The University of Hong Kong',
            '9. Hang Seng University of Hong Kong',
            '10. Hong Kong Shue Yan University',
            '11. The Open University of Hong Kong']
li_uandlink_str = ['City University of Hong Kong:', cityu_adm_link,
                   'Hong Kong Baptist University:', hkbu_adm_link,
                   'Lingnan University:', lu_adm_link,
                   'The Chinese University of Hong Kong:', cuhk_adm_link,
                   'The Education University of Hong Kong:', edu_adm_link,
                   'The Hong Kong Polytechnic University:', polyu_adm_link,
                   'The Hong Kong University of Science and Technology:', hkust_adm_link,
                   'The University of Hong Kong:', hku_adm_link,
                   'Hang Seng University of Hong Kong:', '[HTTP]',
                   'Hong Kong Shue Yan University:', '[HTTP]',
                   'The Open University of Hong Kong:', '[HTTP]']

li_uandlink_str_json = ['City University of Hong Kong: https://www.admo.cityu.edu.hk/direct/', 
                   'Hong Kong Baptist University: https://admissions.hkbu.edu.hk/en/', 
                   'Lingnan University: https://www.ln.edu.hk/admissions/ug/non-jupas/general-notes-to-applicants',
                   'The Chinese University of Hong Kong: http://admission.cuhk.edu.hk/non-jupas-senior/application-details.html', 
                   'The Education University of Hong Kong: https://www.eduhk.hk/onlineappl/',
                   'The Hong Kong Polytechnic University: https://www38.polyu.edu.hk/eAdmission/index.do',
                   'The Hong Kong University of Science and Technology: https://join.ust.hk/apply', 
                   'The University of Hong Kong: https://aal.hku.hk/admissions/international/admissions-information', 
                   'Hang Seng University of Hong Kong: [HTTP]', 
                   'Hong Kong Shue Yan University: [HTTP]',
                   'The Open University of Hong Kong: [HTTP]']


# for KEC
dis_rm_str = ['discussion room', 'discussion rm', 'discuss rm']
sty_rm_str = ['study room', 'study rm', 'study rooms', 'study rms']
cm_rm_str = ['student common room', 'common room', 'cm room', 'cm rm',
             'student common rm', 'common rm', '大com', '大common', 'com room', 'com rm']
lounge_str = ['student lounge', 'lounge', '細com', '細common']
comp_lab_str = ['computer lab', 'comp lab']
lib_str = ['library', 'libra', 'lib']

# financial suport link
# fasp_link = 'https://www.wfsfaa.gov.hk/sfo/en/postsecondary/fasp/overview.htm'
# nlsps_link = 'https://www.wfsfaa.gov.hk/sfo/en/postsecondary/nlsps/overview.htm'
# fs_apply_link = 'https://ess.wfsfaa.gov.hk/essprd/jsp/app/apps0101.jsp?language=en'

# TODO: built objects by import .json instead of hard coding


class Building:
    def __init__(self, str_list: list, open_hour: list, close_hour: list, rooms_list: 'Room'):
        self.str_list = str_list
        self.open_hour = open_hour
        self.close_hour = close_hour
        self.contacts = contacts


class Room:
    def __init__(self, str_list: list, open_hour: list, close_hour: list, purpose: 'String'):
        self.str_list = str_list
        self.open_hour = open_hour
        self.close_hour = close_hour
        self.purpose = purpose


# Discussion room
disrm = ['KEC201', 'KEC202', 'KEC203', 'KEC204']

# Study room
study_rm = ['KEC403', 'KEC603', 'KEC610', 'KEC708']


class NliStatusError(Exception):
    """The NLI result status is not 'ok'"""


class Olami:
    URL = 'https://tw.olami.ai/cloudservice/api'

    def __init__(self, app_key=config['OLAMI']['APP_KEY'], app_secret=config['OLAMI']['APP_SECRET'], input_type=1):
        self.app_key = app_key
        self.app_secret = app_secret
        self.input_type = input_type

    def nli(self, text, cusid=None, intentTag=None):
        response = requests.post(
            self.URL, params=self._gen_parameters('nli', text, cusid))
        response.raise_for_status()
        response_json = response.json()
        if response_json['status'] != 'ok':
            raise NliStatusError(
                "NLI responded status != 'ok': {}".format(response_json['status']))
        else:
            nli_obj = response_json['data']['nli'][0]
            if intentTag is None:
                print("no Intent tag pass before intent_detection")
                return self.intent_detection(nli_obj)
            else:
                print("Intent tag pass before intent_detection\nintentTag:", intentTag)
                return self.intent_detection(nli_obj, intentTag)

    def _gen_parameters(self, api, text, cusid):
        timestamp_ms = (int(time.time() * 1000))
        params = {'appkey': self.app_key,
                  'api': api,
                  'timestamp': timestamp_ms,
                  'sign': self._gen_sign(api, timestamp_ms),
                  'rq': self._gen_rq(text)}
        if cusid is not None:
            params.update(cusid=cusid)
        return params

    def _gen_sign(self, api, timestamp_ms):
        data = self.app_secret + 'api=' + api + 'appkey=' + self.app_key + 'timestamp=' + \
            str(timestamp_ms) + self.app_secret
        return md5(data.encode('ascii')).hexdigest()

    def _gen_rq(self, text):
        obj = {'data_type': 'stt', 'data': {
            'input_type': self.input_type, 'text': text}}
        return json.dumps(obj)

    def intent_detection(self, nli_obj, intentTag=None) -> dict:
        # basic structure to return 
        ret_dict = {
            'tag':{
                'category':"",
                'modifier':"",
                'slots':[]
                },
            'response':None, 
            'status': "False",
            'keyBoardLayout': []
            }

        if intentTag is None:
            intentTagC = {}
            intentTagC['tag']={
                'category':"",
                'modifier':""
                }
        else:
            intentTagC = deepcopy(intentTag)
            print("Intent tag passed.\nintentTag:", intentTagC, "\nBefore combining")
        
        if len(intentTagC['tag']['modifier']) == 0:
            intentTagC['tag']['modifier'] = ""

        if 'slots' not in intentTagC['tag']:
            intentTagC['tag']['slots'] = []

        if 'slotsvalue' in intentTagC:
            slots_value = intentTagC['slotsvalue']
        else:
            slots_value = ""

        intent_category = nli_obj['type']
        if intent_category != 'ds':
            # desc = nli_obj['desc_obj']

            logger.info(f'{nli_obj}')

            if len(intent_category) > 0:
                intentTagC['tag']['category'] = intent_category

            if 'semantic' in nli_obj:
                if 'modifier' in nli_obj['semantic'][0]:
                    modifier = deepcopy(nli_obj['semantic'][0]['modifier'])
                    if len(modifier) > 0:
                        intentTagC['tag']['modifier'] = modifier[0]
                
                if 'slots' in nli_obj['semantic'][0]:
                    slots_ptr = deepcopy(nli_obj['semantic'][0]['slots'])
                    for x in range(len(slots_ptr)):
                        intentTagC['tag']['slots'].append(slots_ptr[x]['name'])
                        if len(slots_value) != 0:
                            slots_value += ('+' + slots_ptr[x]['value'])
                        else:
                            slots_value += slots_ptr[x]['value']
                    if len(slots_value) > 0:
                        print("slots_value:", slots_value)
                        
                # return response through Json

                logger.info(f'After mix: {intentTagC}')

                for jsonObj in li_jsonFiles:
                    if intentTagC['tag'] == jsonObj['tag']:
                        print("Tag found!\nintentTag: ", intentTagC)
                        if len(slots_ptr) > 0:
                            # print("Triggered success! A.1")
                            if slots_value in jsonObj:
                                logger.info(f"found return tag:{jsonObj[slots_value]['return tag']}")
                                ret_dict['tag'] = deepcopy(jsonObj[slots_value]['return tag'])
                                ret_dict['slotsvalue'] = slots_value
                                ret_dict['status'] = jsonObj[slots_value]['status']
                                ret_dict['response'] = deepcopy(jsonObj[slots_value]['response'])
                                if 'keyBoardLayout' in jsonObj[slots_value]:
                                    ret_dict['keyBoardLayout'] = deepcopy(jsonObj[slots_value]['keyBoardLayout'])
                                else:
                                    ret_dict['keyBoardLayout'] = ""
                                return ret_dict
                            else:
                                print("Error: no slot_value key can be found!")
                                break
                                
                        else:
                            print("noslot response return.")
                            if 'noslot' in jsonObj:
                                logger.info(f"found return tag:{jsonObj['noslot']['return tag']}")
                                ret_dict['tag'] = deepcopy(jsonObj['noslot']['return tag'])
                                ret_dict['slotsvalue'] = slots_value
                                ret_dict['status'] = jsonObj['noslot']['status']
                                ret_dict['response'] = deepcopy(jsonObj['noslot']['response'])
                                if 'keyBoardLayout' in jsonObj['noslot']:
                                    ret_dict['keyBoardLayout'] = deepcopy(jsonObj['noslot']['keyBoardLayout'])
                                else:
                                    ret_dict['keyBoardLayout'] = ""
                                return ret_dict
                            else:
                                print("Error: no noslot key can be found!")
                                break
                # Case: Tags cannot be handled
                ret_dict['response'] = ["Sorry. I cannot get your meaning. Can you ask in other manner?"]
                ret_dict['status'] = "True"
                return ret_dict
        else: # Case: Pattern cannot be identified
            print("Tag not found!\nintentTag: ", intentTagC['tag'])
            ret_dict['response'] = ["Sorry. I cannot get your meaning. Can you ask in other manner?"]
            ret_dict['status'] = "True"
            return ret_dict
