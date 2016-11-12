import json
from watson_developer_cloud import NaturalLanguageClassifierV1
import sys

if __name__ == '__main__':

    natural_language_classifier = NaturalLanguageClassifierV1(username='9bb44fae-5d4f-4f55-a024-6278ae14c655', password='ITch7aNcuaa2')

    classifiers = natural_language_classifier.list()
    print(json.dumps(classifiers, indent=2))

    with open('resources/classes.csv', 'rb') as training_data:
        print(json.dumps(natural_language_classifier.create(training_data=training_data, name='symptoms'), indent=2))

    status = natural_language_classifier.status('e82f62x108-nlc-5198')
    print(json.dumps(status, indent=2))

    if status['status'] == 'Available':
        classes = natural_language_classifier.classify('e82f62x108-nlc-5198', sys.argv[1])
        print(json.dumps(classes, indent=2))
