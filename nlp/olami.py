import configparser
import json
import logging
import time
from hashlib import md5

import requests

config = configparser.ConfigParser()
config.read('config.ini')

logger = logging.getLogger(__name__)

# String for comparison
# for granted UNIVERSITY, source from wikipedia
# UGC-funded
cityu_str = ['City University of Hong Kong', 'City U', 'CityU']
hkbu_str = ['Hong Kong Baptist University', 'HKBU']
lu_str = ['Lingnan University', 'LU', 'LingU', 'Ling U']
cuhk_str = [ 'The Chinese University of Hong Kong', 'CUHK']
edu_str = [ 'The Education University of Hong Kong', 'EdU', 'Ed U']
polyu_str = [ 'The Hong Kong Polytechnic University', 'PolyU', 'Poly U']
hkust_str = [ 'The Hong Kong University of Science and Technology', 'HKUST', 'UST']
hku_str = [ 'The University of Hong Kong', 'HKU']
# Self-funded
hsu_str = [ 'Hang Seng University of Hong Kong', 'Hang Seng U', 'HSU']
syu_str = [ 'Hong Kong Shue Yan University', 'Shue Yan', 'SYU']
hkou = [ 'The Open University of Hong Kong', 'HKOU', 'Open U']
# for KEC
dis_rm_str = ['discussion room','discussion rm','discuss rm']
sty_rm_str = ['study room', 'study rm']
cm_rm_str = ['student common room', 'common room', 'cm room', 'cm rm', 'student common rm', 'common rm','大com','大common', 'com room', 'com rm']
lounge_str = ['student lounge', 'lounge', '細com', '細common']
comp_lab_str = ['computer lab', 'comp lab']
lib_str = ['library', 'libra', 'lib']
# for the buildings
kec_str=['kowloon east campus','kec']
cita_str=['clothing industry training authority', 'cita']
iec_str=['island east campus', 'iec']
ftc_str=['fortress tower centre','fortress tower center','ftc']
adc_unc_str=['admiralty centre & united centre', 'admiralty centre and united centre', 'adc and unc', 'adc & unc', 'adc&unc']

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
disrm = ['KEC201','KEC202','KEC203','KEC204']

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

    def nli(self, text, cusid=None):
        response = requests.post(self.URL, params=self._gen_parameters('nli', text, cusid))
        response.raise_for_status()
        response_json = response.json()
        if response_json['status'] != 'ok':
            raise NliStatusError("NLI responded status != 'ok': {}".format(response_json['status']))
        else:
            nli_obj = response_json['data']['nli'][0]
            return self.intent_detection(nli_obj)

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
        obj = {'data_type': 'stt', 'data': {'input_type': self.input_type, 'text': text}}
        return json.dumps(obj)


    def intent_detection(self, nli_obj):
        def handle_selection_category(category, modifier):
            if category == 'nonjupas':
                if modifier == 'whenis_open_nospecific':
                    pass
                elif modifier == 'whenis_deadline_nospecific':
                    pass
                elif modifier == 'what_toprepare_general':
                    pass
                elif modifier == 'yn_apply_year1':
                    pass
                elif modifier == 'whatis_requirement_nospecific':
                    pass
                elif modifier == 'action_latetosubmit':
                    pass
                elif modifier == 'yn_essential_referenceletter':
                    pass
                elif modifier == 'howto_webpage_university':
                    pass
                elif modifier == 'nonjupas_nospecific':
                    pass
                elif modifier == 'whenis_deadline_nospecific':
                    pass
                elif modifier == 'yn_num_referenceletter_matter':
                    pass
                elif modifier == 'yn_igcse_replace_ielts':
                    pass
            elif category == 'facility':
                if modifier == 'location_nospecific': 
                    pass
                elif modifier == 'openinghour_facility_nospecific':
                    pass
                elif  modifier == 'yn_facility_open_nospecific':
                    pass

        intent_category = nli_obj['type']
        desc = nli_obj['desc_obj']
        print(nli_obj)
        if len(intent_category) > 0:
            if 'semantic' in nli_obj:
                if 'modifier' in nli_obj['semantic'][0]:
                    modifier = nli_obj['semantic'][0]['modifier']
                    if len(modifier) > 0:
                        if intent_category == "greet":
                            if 'greeting' in modifier:
                                return desc['result']
                            elif 'closing' in modifier:
                                return "See you again!"
                        elif intent_category == "nonjupas":
                            if 'whatis' in modifier:
                                return 'Apart from getting a place into universities through JUPAS, students may consider applying post-secondary programmes not covered by JUPAS. There is a lot of information regarding non-JUPAS admissions. Gather your information in advance and plan ahead.'
                            elif 'whenis_open_nospecific' in modifier:
                                return 'You can apply non-jupas application once it is open. Each university may vary.'
                            elif 'whenis_deadline_nospecific' in modifier:
                                slot = nli_obj['semantic'][0]['slots'][0]
                                if 'university' == slot['name']:
                                    tmp_str = slot['value'].lower()
                            elif 'what_toprepare_general' in modifier:
                                pass
                            elif 'yn_apply_year1' in modifier:
                                pass
                            elif 'schoolsupport_nospecific' in modifier:
                                pass
                            elif 'whatis_requirement_nospecific' in modifier:
                                pass
                            elif 'yn_apply_morethan1' in modifier:
                                pass
                            elif 'action_latetosubmit' in modifier:
                                pass
                            elif 'yn_essential_referenceletter' in modifier:
                                pass
                            elif 'yn_essential_apply_year2' in modifier:
                                pass
                            elif 'howto_webpage_university' in modifier:
                                slot = nli_obj['semantic'][0]['slots'][0]
                                if 'university' == slot['name']:
                                    tmp_str = slot['value'].lower()
                            elif 'howto_apply_university' in modifier:
                                pass
                            elif 'nonjupas_nospecific' in modifier:
                                pass
                            elif 'howto_webpage_university' in modifier:
                                pass
                            elif 'whenis_deadline' in modifier:
                                pass
                            elif 'howto_webpage_university' in modifier:
                                pass
                            elif 'whenis_deadline' in modifier:
                                pass
                            elif 'yn_num_referenceletter_matter' in modifier:
                                pass
                            elif 'whenis_start_publicexam' in modifier:
                                pass
                            elif 'whencan_apply_publicexam' in modifier:
                                pass
                            elif 'yn_igcse_replace_ielts' in modifier:
                                pass
                        elif intent_category == "finance":
                            pass
                        elif intent_category == "admin":
                            pass
                        elif intent_category == "facility":
                            if 'place' in modifier:
                                slot = nli_obj['semantic'][0]['slots'][0]
                                if 'facilities' == slot['name']:
                                    tmp_str = slot['value'].lower()
                                    if tmp_str in dis_rm_str:
                                        return f'There are {len(disrm)} discussion rooms in KEC. They are ' + ','.join(disrm)
                                    elif tmp_str in cm_rm_str or tmp_str in lounge_str or tmp_str in comp_lab_str:
                                        return f"{slot['value'].lower()} is on the 3/F"
                                    elif tmp_str in lib_str:
                                        return f"{slot['value'].lower()} is on the 4/F"
                                    elif tmp_str in sty_rm_str:
                                        return f'There are {len(study_rm)} study rooms in KEC. They are ' + ','.join(study_rm)
                                    else:
                                        return 'Sorry. The facilities cannot be found in KEC. Please try again.'
                            elif 'contact' in modifier:
                                slot = nli_obj['semantic'][0]['slots'][0]
                                if 'office' == slot['name']:
                                    tmp_str = slot['value'].lower()
                                    if tmp_str in kec_str:
                                        return f'The office hotline is {"3762 2000"}. Please contact them within their office hour:\n' + "\n".join(["0830 – 1930 (Weekdays)", "0830 – 1730 (Saturday)", "0830 – 1630 (Sunday)"])
                                    elif tmp_str in cita_str:
                                        return f'The office hotline is {"3762 0110"}. Please contact them within their office hour:\n' + "\n".join(["0900 – 2000 (Weekdays)", "0900 – 1800 (Saturday)"])
                                    elif tmp_str in iec_str:
                                        return f'The office hotline is {"3762 0033"}. Please contact them within their office hour:\n' + "\n".join(["0830 – 1930 (Weekdays)", "0830 – 1730 (Saturday)"])
                                    elif tmp_str in ftc_str:
                                        return f'The office hotline is {"3762 0988"}. Please contact them within their office hour:\n' + "\n".join(["0830 – 1930 (Weekdays)"])
                                    elif tmp_str in adc_unc_str:
                                        return f'The office hotline is {"2910 7620"}. Please contact them within their office hour:\n' + "\n".join(["0830 – 1930 (Weekdays)", "0830 – 1730 (Saturday)"])
                                    else:
                                        return 'Sorry. The contact of building office cannot be found. Please try again.'
                            elif 'location_nospecific' in modifier:
                                slot = nli_obj['semantic'][0]['slots'][0]
                                if 'facility' == slot['name']:
                                    tmp_str = slot['value'].lower()
                            elif 'campus_have_nospecific' in modifier:
                                slot = nli_obj['semantic'][0]['slots'][0]
                                if 'campus' == slot['name']:
                                    tmp_str = slot['value'].lower()
                            elif 'campus_have' in modifier:
                                slots = nli_obj['semantic'][0]['slots']
                                if len(slots) == 2:
                                    if 'facility' == slots[0]['name']:
                                        tmp_str = slots[0]['value'].lower()
                                    if 'campus' == slots[1]['name']:
                                        tmp_str = slots[1]['value'].lower()
                            elif 'openinghour_facility_nospecific' in modifier:
                                slot = nli_obj['semantic'][0]['slots'][0]
                                if 'facility' == slot['name']:
                                    tmp_str = slot['value'].lower()
                            elif 'openinghour_facility' in modifier:
                                slots = nli_obj['semantic'][0]['slots']
                                if len(slots) == 2:
                                    if 'facility' == slots[0]['name']:
                                        tmp_str = slots[0]['value'].lower()
                                    if 'campus' == slots[1]['name']:
                                        tmp_str = slots[1]['value'].lower()
                            elif 'yn_facility_open_nospecific' in modifier:
                                pass
                            elif 'yn_facility_open' in modifier:
                                slots = nli_obj['semantic'][0]['slots']
                                if len(slots) == 2:
                                    if 'facility' == slots[0]['name']:
                                        tmp_str = slots[0]['value'].lower()
                                    if 'campus' == slots[1]['name']:
                                        tmp_str = slots[1]['value'].lower()
                        elif intent_category == "online":
                            pass                  
            return 'Sorry. I cannot get your meaning. Can you ask in other manner?'
        