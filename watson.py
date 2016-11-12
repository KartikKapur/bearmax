import json
from watson_developer_cloud import NaturalLanguageClassifierV1
import sys

USERNAME = '9bb44fae-5d4f-4f55-a024-6278ae14c655'
PASSWORD = 'ITch7aNcuaa2'

CLASSES_PATH = 'resources/normalized_classes.csv'

def get_symptoms(statement, natural_language_classifier, instance_id):

    status = natural_language_classifier.status(instance_id)
    print(json.dumps(status, indent=2))

    if status['status'] == 'Available':
        classes = natural_language_classifier.classify(instance_id, statement)
        print(json.dumps(classes, indent=2))
        return classes['top_class'], classes['classes']
    return None, []

def init_nat_lang_classifier(initialized=False):

    natural_language_classifier = NaturalLanguageClassifierV1(username=USERNAME, password=PASSWORD)

    classifiers = natural_language_classifier.list()
    print(json.dumps(classifiers, indent=2))

    if initialized and classifiers:
        return natural_language_classifier, classifiers['classifiers'][0]['classifier_id']

    if not initialized:
        with open(CLASSES_PATH, 'rb') as training_data:
            response = natural_language_classifier.create(training_data=training_data, name='symptoms'),
            print(json.dumps(response, indent=2))
            return natural_language_classifier, response[0]['classifier_id']

    return

def remove_classifier(natural_language_classifier, instance_id):
    natural_language_classifier.remove(instance_id)

if __name__ == '__main__':
    natural_language_classifier, instance_id = init_nat_lang_classifier(True)
    print(get_symptoms(sys.argv[1], natural_language_classifier, instance_id))
    # remove_classifier(natural_language_classifier, "e82f62x108-nlc-5217")