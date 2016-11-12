import requests
import json

import hmac, hashlib
import base64

LANGUAGE = 'en-gb'

USERNAME = 'ajaynraj@gmail.com'
PASSWORD = 'Hw52Nbq9Y8Rfp3B7S'

AUTH_SERVICE_ENDPOINT = 'https://sandbox-authservice.priaid.ch/login'
SANDBOX_ENDPOINT = 'https://sandbox-healthservice.priaid.ch'
SYMPTOMS_ENDPOINT = 'symptoms'
ISSUES_ENDPOINT = 'issues'
DESCRIPTION_ENDPOINT = 'issues/{0}/info'
DIAGNOSIS_ENDPOINT = 'diagnosis'
PROPOSED_SYMPTOMS_ENDPOINT = 'symptoms/proposed'

class SymptomChecker():

    def __init__(self, username=USERNAME, password=PASSWORD):
        self.token = self.auth(username, password)
        self.params = {
            'token': self.token,
            'language': LANGUAGE,
            'format':'json'
        }
        self.symptoms = self.get_symptoms()
        self.issues = self.get_issues()

    def auth(self, username, password):
        raw_hash_string = hmac.new(bytes(PASSWORD, encoding='utf-8'), AUTH_SERVICE_ENDPOINT.encode('utf-8')).digest()
        computed_hash_string = base64.b64encode(raw_hash_string).decode()
        post_headers = {'Authorization': 'Bearer {0}:{1}'.format(USERNAME, computed_hash_string)}
        response = requests.post(AUTH_SERVICE_ENDPOINT, headers=post_headers)
        return response.json()['Token']

    def get(self, endpoint, params=None):
        if not params:
            params = self.params
        return requests.get('{0}/{1}'.format(SANDBOX_ENDPOINT, endpoint), params)

    def get_symptoms(self):
        response = self.get(SYMPTOMS_ENDPOINT)
        return {symptom['Name']: symptom['ID'] for symptom in response.json()}

    def get_issues(self):
        response = self.get(ISSUES_ENDPOINT)
        return {issue['Name']: issue['ID'] for issue in response.json()}

    def get_description(self, issue_id):
        response = self.get(DESCRIPTION_ENDPOINT.format(issue_id))
        return response.json()

    def specialized_get(self, endpoint, symptoms, gender, year_of_birth):
        symptom_ids = [self.symptoms[s] for s in symptoms]
        new_params = self.params.copy()
        new_params.update({
            'symptoms': str(["{0}".format(id) for id in symptom_ids]), 
            'gender': gender,
            'year_of_birth': year_of_birth
        })
        response = self.get(endpoint, params=new_params)
        return response.json()

    def get_diagnosis(self, symptoms, gender, year_of_birth):
        return self.specialized_get(DIAGNOSIS_ENDPOINT, symptoms, gender, year_of_birth)

    def get_proposed_symptoms(self, symptoms, gender, year_of_birth):
        return self.specialized_get(PROPOSED_SYMPTOMS_ENDPOINT, symptoms, gender, year_of_birth)
