import os
import json
import urllib
import watson
from resources import *
from apiai import *
from flask import Flask
from flask import request
from flask import make_response


@app.route('/webhook', methods=['bear'])
def webhook():
    # just get webhook in here
    req = request.get_json(silent=True, force=True)

    print("What is wrong with you?")
    print(json.dumps(req, indent=4))
    res = processRequest(req)
    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r
all_symptoms={}
def makeSymptomQuery(inp):
    problem = inp.get("key_word") #something about the key word/symptom we want
    if all_symptoms[problem]:
        return 'You have already listed this symptom'
    else:
        return processRequest(problem)

def processRequest(problem):
    #we want to be able to get the data from classes and put in here

    if problem is None:
        return None
    else:
        all_symptoms[problem] = classifierID
        #This is only if they have more symptoms
        print("Do you have more symptoms to report?")
        check_more = input()
        if check_more.lower() == 'yes' or check_more.lower() == 'yeah':
            return webhook()
        else:
            return  final_prognosis()



def final_prognosis():
    # calculate with the whole dictionary and then return the final prognosis
    if ____(#certain type of disease):
        return "Go to the doctor as soon as possible you mostl likely have {0}".format()
    elif ___ #monitor it
    else:

    return "Based on our calculations, you have {0} and you have a {1} chance of having it".format(____)

#
#
# if __name__ == '__main__':
#     port = int(os.getenv('PORT', 5000))
#
#     print "Starting app on port %d" % port
#
#     app.run(debug=False, port=port, host='0.0.0.0')