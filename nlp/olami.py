import configparser
import json
import logging
import readjson
import time
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

    def nli(self, text, cusid=None):
        response = requests.post(
            self.URL, params=self._gen_parameters('nli', text, cusid))
        response.raise_for_status()
        response_json = response.json()
        if response_json['status'] != 'ok':
            raise NliStatusError(
                "NLI responded status != 'ok': {}".format(response_json['status']))
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
        obj = {'data_type': 'stt', 'data': {
            'input_type': self.input_type, 'text': text}}
        return json.dumps(obj)

    def intent_detection(self, nli_obj):
        def handle_selection_category(modifier, slots):
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
            elif modifier == 'location_nospecific':
                pass
            elif modifier == 'openinghour_facility_nospecific':
                pass
            elif modifier == 'yn_facility_open_nospecific':
                pass

        intent_category = nli_obj['type']
        desc = nli_obj['desc_obj']

# TODO: same codes have many copies across the same method
#       recommend to divide them into small function

        if len(intent_category) > 0:
            # debug
            intentTag = {'category':None,'modifier':None, 'slots':{}}
            intentTag['category'] = intent_category

            if 'semantic' in nli_obj:
                if 'modifier' in nli_obj['semantic'][0]:
                    modifier = nli_obj['semantic'][0]['modifier']
                    if len(modifier) > 0:

                        intentTag['modifier'] = modifier[0]

                        slots_ptr = nli_obj['semantic'][0]['slots']
                        for x in range(len(slots_ptr)):
                            intentTag['slots'][slots_ptr[x]['name']] = slots_ptr[x]['value']
                        print("intentTag: ", intentTag)
                        
                        for jsonObj in li_jsonFiles:
                            if intentTag == jsonObj['tag']:
                                return '\n'.join(jsonObj['response'])

                        if intent_category == "greet": #moved greet module to json
                            if 'greeting' in modifier:
                                return desc['result']
                            elif 'help' in modifier:
                                return desc['result']
                            elif 'guideline' in modifier:
                                return desc['result']
                            elif 'closing' in modifier:
                                return "See you again!Thank you for using spacebot"
                        elif intent_category == "nonjupas":
                            if 'whatis' in modifier:
                                # done
                                return 'Apart from getting a place into universities through JUPAS, students may consider applying post-secondary programmes not covered by JUPAS. There is a lot of information regarding non-JUPAS admissions. Gather your information in advance and plan ahead.'
                            elif 'whenis_open_nospecific' in modifier:
                                #done
                                return 'You can apply non-jupas application once it is open. Each university may vary.'
                            elif 'whenis_deadline_nospecific' in modifier:
                                if len(nli_obj['semantic'][0]['slots']) > 0:
                                    return 'Do you mean non-JUPAS deadline?\n Y - YES\n N - No'
                                else:
                                    return 'Each university may vary. Which university you want to apply / have applied?\n' + '\n'.join(li_u_str)
                            elif 'what_toprepare_general' in modifier:
                                #done
                                return 'Each university may vary. But Generally, you should better prepare your personal identify information(e.g. HKID / Passport / etc), public examination results(e.g. HKDSE / HKCEE /HKALE / IGCSE / IELTS / TOFEL / etc), official transcript, personal statement, other appropriate qualification documents (e.g. public non-academic awards / etc),  etc. Which university you want to apply / have applied?\n' + '\n'.join(li_u_str)
                            elif 'yn_apply_year1' in modifier:
                                #done
                                return 'You can apply non-jupas application when you are year 1 student,  but bare in mind that some universities may only consider senior level student and some might only consider junior level student.Which university you want to apply / have applied?\n' + '\n'.join(li_u_str)
                            elif 'schoolsupport_nospecific' in modifier:
                                #done ****but if the question is asked too long, and the bot may not be able to handle
                                return "HKUSPACE have setup an online platform in learner portal for student to apply for the reference letter from the professor.\nMake sure you have get the professor's approval before apply for the letter through the online platform.\nYou may refer to [HTTP] for further information."
                            elif 'whatis_requirement_nospecific' in modifier:
                                #done
                                return "It depends on the university you want to apply and the programme you want to apply. For general requirement in applying the universities in Hong Kong, you should as least have GRADE 3 for both Chinese and English language subject and 5 subjects in GRADE 2 for HKDSE result. For the language subject, you can use the result of IELTS and IGCSE instead but the requirement for each univerisity and programme may vary. Which programe and university you want to apply/ have applied?\n" + '\n'.join(li_u_str)
                            elif 'yn_apply_morethan1' in modifier:
                                #done
                                return 'Each university may vary. Which university you want to apply / have applied?\n' + '\n'.join(li_u_str)
                            elif 'action_latetosubmit' in modifier:
                                #done
                                return 'Indeed, late submission would not be allowed. Although the univerisities usually have many rounds of non-JUPAS application, it is recommended to submit the application as soon as possible. You may contact to their admission office directly if you want some help. Which programe and university you want to apply/ have applied?\n' + '\n'.join(li_u_str)
                            elif 'yn_essential_referenceletter' in modifier:
                                # done
                                return 'Each university may vary. Which programe and university you want to apply/ have applied?\n' + '\n'.join(li_u_str)
                            elif 'yn_essential_apply_year2' in modifier:
                                return 'Indeed. the associate programme is aimed to assist the students to promote their academic position to undergraduate level but not for profession purpose. Students are supposed to apply NON-JUPAS before they are graduated'
                            elif 'howto_apply_university_general' in modifier:
                                #can modify with json dynamically later********
                                return "You can apply the non-jupas from any University's non-jupas page. The links are as followed:\n" + '\n'.join(li_uandlink_str)
                            elif 'nonjupas_nospecific' in modifier:
                                return 'Which university are you refering to?' + '\n'.join(li_u_str)
                            elif 'howto_webpage_university' in modifier:
                                # done
                                if len(nli_obj['semantic'][0]['slots']) > 0:
                                    slot = nli_obj['semantic'][0]['slots'][0]
                                    if 'university' == slot['name']:
                                        tmp_str = slot['value'].lower()
                                        # need to update new link and new function call******************
                                        deadline, link, ready = readjson.response_nonjupas_deadline(
                                            tmp_str)
                                        if ready:
                                            return 'You can apply from ' + slot['value'] + ' non-jupas page. The link is as followed:\n' + link
                                        else:
                                            return 'Sorry. I do not have the non-JUPAS information of ' + slot['value'] + '. You may refer to the non-JUPAS information of universities as followed:\n' + '\n'.join(li_uandlink_str)
                                else:
                                    return 'Which programe and university you want to apply/ have applied?'
                            elif 'whenis_deadline' in modifier:
                                # done
                                slot = nli_obj['semantic'][0]['slots'][0]
                                if 'university' == slot['name']:
                                    tmp_str = slot['value'].lower()
                                    deadline, link, ready = readjson.response_nonjupas_deadline(
                                        tmp_str)
                                    if ready:
                                        return 'The non-JUPAS application deadline of ' + slot['value'] + ' is/are as followed:\n' + '\n'.join(deadline) + '\nYou may refer to the following link for more details:\n' + link
                            elif 'yn_num_referenceletter_matter' in modifier:
                                #done
                                return 'Each university and programme may vary. Which programe and university you want to apply/ have applied?'
                            elif 'whenis_start_publicexam' in modifier:
                                slot = nli_obj['semantic'][0]['slots'][0]
                                if 'publicexam' == slot['name']:
                                    tmp_str = slot['value'].lower()
                                    if tmp_str in publicexam_str:
                                        if tmp_str == publicexam_str[0]:
                                            return 'You may refer to [HTTP] for more information.'
                                        elif tmp_str == publicexam_str[1]:
                                            return 'You may refer to [HTTP] for more information.'
                                        elif tmp_str == publicexam_str[2]:
                                            return 'You may refer to [HTTP] for more information.'
                                        elif tmp_str == publicexam_str[3]:
                                            return 'You may refer to [HTTP] for more information.'
                                        elif tmp_str == publicexam_str[4]:
                                            return 'You may refer to [HTTP] for more information.'
                            elif 'whencan_apply_publicexam' in modifier:
                                slot = nli_obj['semantic'][0]['slots'][0]
                                if 'publicexam' == slot['name']:
                                    tmp_str = slot['value'].lower()
                                    if tmp_str in publicexam_str:
                                        if tmp_str == publicexam_str[0]:
                                            return 'You can apply it before [DEADLINE] / at anytime. Please refer to [HTTP] for more information.'
                                        elif tmp_str == publicexam_str[1]:
                                            return 'You can apply it before [DEADLINE] / at anytime. Please refer to [HTTP] for more information.'
                                        elif tmp_str == publicexam_str[2]:
                                            return 'You can apply it before [DEADLINE] / at anytime. Please refer to [HTTP] for more information.'
                                        elif tmp_str == publicexam_str[3]:
                                            return 'You can apply it before [DEADLINE] / at anytime. Please refer to [HTTP] for more information.'
                                        elif tmp_str == publicexam_str[4]:
                                            return 'You can apply it before [DEADLINE] / at anytime. Please refer to [HTTP] for more information.'
                            elif 'yn_igcse_replace_ielts' in modifier:
                                return 'Each university and programme may vary. Which programe and university you want to apply/ have applied?'
                        elif intent_category == "finance":  #moved finance module to json
                            if 'fs_ask' in modifier:
                                return desc['result']
                            elif 'fs_link' in modifier:

                                # future dynamic way******************************
                                # slot = nli_obj['semantic'][0]['slots'][0]
                                # if 'financial_support' == slot['name']:
                                #     tmp_str = slot['value'].lower()
                                #     x, y = getjson()
                                #     if ready:
                                #         return 'xxxxx' + x + 'xxxxxx' + y
                                # ***********************************
                                #testing
                                return 'You can get more information from:\n' + '1. FASP: ' + fasp_link + '\n2. NLSPS: ' + nlsps_link
                            elif 'fs_method' in modifier:
                                return 'You need to make the online application on ' + fs_apply_link + ' for both FASP and NLSPS.'
                        elif intent_category == "admin":
                            pass
                        elif intent_category == "facilities":
                            if 'place' in modifier:
                                slot = nli_obj['semantic'][0]['slots'][0]
                                if 'facilities' == slot['name']:
                                    tmp_str = slot['value'].lower()
                                    if tmp_str in dis_rm_str:
                                        return f'There are {len(disrm)} discussion rooms in KEC. They are ' + ','.join(disrm)
                                    elif tmp_str in cm_rm_str:
                                        return f"{slot['value'].lower()} is on the 3/F"
                                    elif tmp_str in lounge_str:
                                        return f"{slot['value'].lower()} is on the 3/F"
                                    elif tmp_str in comp_lab_str:
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
                                    contact, hr, ready = readjson.response_OfficeHr(
                                        tmp_str)
                                    if ready:
                                        return f'The office hotline is ' + contact + '. Please contact them within their office hour:\n' + "\n".join(hr)
                                    else:
                                        return 'Sorry. The contact of building office cannot be found. Please try again.'
                            elif 'location_nospecific' in modifier:
                                slot = nli_obj['semantic'][0]['slots'][0]
                                if 'facilities' == slot['name']:
                                    tmp_str = slot['value'].lower()
                            elif 'campus_have_nospecific' in modifier:
                                slot = nli_obj['semantic'][0]['slots'][0]
                                if 'campus' == slot['name']:
                                    tmp_str = slot['value'].lower()
                            elif 'campus_have' in modifier:
                                slots = nli_obj['semantic'][0]['slots']
                                if len(slots) == 2:
                                    if 'facilities' == slots[0]['name']:
                                        fac_name = slots[0]['value'].lower()
                                    if 'campus' == slots[1]['name']:
                                        cam_name = slots[1]['value'].lower()
                            elif 'openinghour_facility_nospecific' in modifier:
                                slot = nli_obj['semantic'][0]['slots'][0]
                                if 'facilities' == slot['name']:
                                    tmp_str = slot['value'].lower()
                            elif 'openinghour_facility' in modifier:
                                slots = nli_obj['semantic'][0]['slots']
                                if len(slots) == 2:
                                    if 'facilities' == slots[0]['name']:
                                        fac_name = slots[0]['value'].lower()
                                    if 'campus' == slots[1]['name']:
                                        cam_name = slots[1]['value'].lower()
                            elif 'yn_facility_open_nospecific' in modifier:
                                pass
                            elif 'yn_facility_open' in modifier:
                                slots = nli_obj['semantic'][0]['slots']
                                if len(slots) == 2:
                                    if 'facilities' == slots[0]['name']:
                                        fac_name = slots[0]['value'].lower()
                                    if 'campus' == slots[1]['name']:
                                        cam_name = slots[1]['value'].lower()
                        elif intent_category == "online":
                            pass
                        elif intent_category == "selection":
                            slots = nli_obj['semantic'][0]['slots']
                            handle_selection_category(modifier, slots)
            return 'Sorry. I cannot get your meaning. Can you ask in other manner?'
