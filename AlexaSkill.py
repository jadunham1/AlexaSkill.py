import json
import pprint
import collections
import random
import logging

def named_tuple(mapping):
    if (isinstance(mapping, collections.Mapping)):
        for key, value in mapping.iteritems():
            mapping[key] = named_tuple(value)
        return namedtuple_from_mapping(mapping)
    return mapping

def namedtuple_from_mapping(mapping, name="NamedTuple"):
    this_namedtuple_maker = collections.namedtuple(name, mapping.iterkeys())
    return this_namedtuple_maker(**mapping)

class AlexaSkill:
    def __init__(self, app_id=None, event=None):
        self.app_id = app_id
        self.request = named_tuple(event['request'])
        self.session = event['session']
        self.response = None

    def process_event(self):
        events = {
            'IntentRequest': self.intentHandler,
            'LaunchRequest': self.launchHandler,
            'SessionEndedRequest': self.sessionEndHandler
        }
        print "Event type found: {}".format(self.request.type)
        return events[self.request.type]()

    def ask(self, *args):
        response = AlexaResponse(session=self.session)
        return response.ask(*args)

    def tell(self, *args):
        response = AlexaResponse(session=self.session)
        return response.tell(*args)

    def tellWithCard(self, *args, **kwargs):
        response = AlexaResponse(session=self.session)
        return response.tellWithCard(*args, **kwargs)


class AlexaResponse:
    def __init__(self, request=None, session={}):
        self._request = request
        self._session = session

    def tell(self, speechOutput):
        return self._buildResponse({
                                        'session': self._session,
                                        'output': speechOutput,
                                        'shouldEndSession': True
                                   })

    def tellWithCard(self, speechOutput, cardTitle, cardContent, repromptText=None, shouldEndSession=True):
        return self._buildResponse({
                                        'session': self._session,
                                        'output': speechOutput,
                                        'cardTitle': cardTitle,
                                        'cardContent': cardContent,
                                        'shouldEndSession': shouldEndSession,
                                        'reprompt': repromptText
                                   })

    def ask(self, speechOutput, repromptText):
        return self._buildResponse({
                                        'session': self._session,
                                        'output': speechOutput,
                                        'reprompt': repromptText,
                                        'shouldEndSession': False
                                })

    def _buildResponse(self, options):
        response = {
            'outputSpeech': {
                'type': 'SSML',
                'ssml': options['output']
            },
            'shouldEndSession': options['shouldEndSession']
        }

        if 'cardTitle' in options and 'cardContent' in options:
            response['card'] = {
                'type': "Simple",
                'title': options['cardTitle'],
                'content': options['cardContent']
            }

        if 'reprompt' in options:
            response['reprompt'] = {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': options['reprompt']
                }
            }

        returnResult = {
            'version': '1.0',
            'response': response
        }

        if 'session' in options:
            print options['session']
            if 'attributes' in options['session']:
                returnResult['sessionAttributes'] = options['session']['attributes']
        print "Sending response back: {}".format(returnResult)
        return returnResult
