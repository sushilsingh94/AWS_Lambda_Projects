# -*- coding: utf-8 -*-
""" USA State fact and quiz.. """
from __future__ import print_function
import math
import string
import random
import get_rates_service as r1


MAX_QUESTION = 10

#This is the welcome message for when a user starts the skill without a specific intent.
WELCOME_MESSAGE = ("Welcome to the Caterpillar Procurement Routing guide!  For which Region and Mode"
                   " you want to search for the rates?"
                   "  What would you like to do?")
#This is the message a user will hear when they start a quiz.
SKILLTITLE = "States of the USA"


#This is the message a user will hear when they start a quiz.
START_QUIZ_MESSAGE = "OK.  I will ask you 10 questions about the United States."

#This is the message a user will hear when they try to cancel or stop the skill"
#or when they finish a quiz.
EXIT_SKILL_MESSAGE = "Thank you for using Caterpillar Procurement Routing guide!  Welcome back soon!"

#This is the message a user will hear after they ask (and hear) about a specific data element.
REPROMPT_SPEECH = "Which other Origin and destination and service you would like search rates for?"

#This is the message a user will hear when they ask Alexa for help in your skill.
HELP_MESSAGE = ("I can search for best Carrier rates for given Origin and Destination and service.  You can ask me about a PEORIA,IL "
                " to MORTON,IL for TL service, and I'll tell you best Caterpillar carriers.  "
                "What would you like to do?")

#If you don't want to use cards in your skill, set the USE_CARDS_FLAG to false.
#If you set it to true, you will need an image for each item in your data.
USE_CARDS_FLAG = False

STATE_START = "Start"
STATE_QUIZ = "Quiz"

STATE = STATE_START
COUNTER = 0
QUIZSCORE = 0


SAYAS_INTERJECT = "<say-as interpret-as='interjection'>"
SAYAS_SPELLOUT = "<say-as interpret-as='spell-out'>"
SAYAS = "</say-as>"
BREAKSTRONG = "<break strength='strong'/>"

 # --------------- speech cons -----------------

 # This is a list of positive/negative speechcons that this skill will use when a user
 # gets a correct answer. For a full list of supported speechcons, go here:
 # https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/docs/speechcon-reference
SPEECH_CONS_CORRECT = (["Booya", "All righty", "Bam", "Bazinga", "Bingo", "Boom", "Bravo",
                        "Cha Ching", "Cheers", "Dynomite", "Hip hip hooray", "Hurrah",
                        "Hurray", "Huzzah", "Oh dear.  Just kidding.  Hurray", "Kaboom",
                        "Kaching", "Oh snap", "Phew", "Righto", "Way to go", "Well done",
                        "Whee", "Woo hoo", "Yay", "Wowza", "Yowsa"])

SPEECH_CONS_WRONG = (["Argh", "Aw man", "Blarg", "Blast", "Boo", "Bummer", "Darn", "D'oh",
                      "Dun dun dun", "Eek", "Honk", "Le sigh", "Mamma mia", "Oh boy",
                      "Oh dear", "Oof", "Ouch", "Ruh roh", "Shucks", "Uh oh", "Wah wah",
                      "Whoops a daisy", "Yikes"])

# --------------- a class to contain states and their details -----------------
class Item:
    """ Item class """

    def __init__(self, region, origin, destination, service, shipdate):
        self.region = region
        self.origin = origin
        self.destination = destination
        self.service = service
        self.shipdate = shipdate


    @staticmethod
    def properties():
        """ get property name  """
        val = ["Region", "Mode", "Origin",
               "Destination", "Weight", "Service", "ShipDate"]
        return val

    def property_value(self, prop):
        """ get property value  """
        if prop == "region":
            return self.region
        elif prop == "origin" or prop == "from city":
            return self.origin
        elif prop == "destination" or prop == "to city":
            return self.destination
        elif prop == "service":
            return self.service
        elif prop == "shipdate":
            return self.shipdate
        return ""
    
    def get_text_description(self):
        """ get text details for card display """

        text = "region Name: " + self.region + "\n"
        text += "origin: " +self.origin + "\n"
        text += "destination: " +self.destination + "\n"
        text += "service: " +self.service + "\n"
        text += "shipdate: " +self.shipdate + "\n"
        return text


# --------------- our list of states -----------------
ITEMS = []
ITEMS.append(Item("North america","61615", "61550","TL","05/03/2018"))
ITEMS.append(Item("North america","61610", "61550","TL","05/03/2018"))
ITEMS.append(Item("North america","61612", "61550","TL","05/03/2018"))

class Result:
    """ Result class """

    def __init__(self, origin, destination, carriername, carriercode, rate, service, equipmenttype):
        self.origin = origin
        self.destination = destination
        self.carriername = carriername
        self.carriercode = carriercode
        self.rate = rate
        self.service = service
        self.equipmenttype = equipmenttype

    def property_value(self, prop):
        """ get property value  """
        if prop == "origin" or prop == "from city":
            return self.origin
        elif prop == "destination" or prop == "to city":
            return self.destination
        elif prop == "carriername":
            return self.carriername
        elif prop == "carriercode":
            return self.carriercode
        elif prop == "rate":
            return self.rate
        elif prop == "service":
            return self.service
        elif prop == "equipmenttype":
            return self.equipmenttype
        return ""


RESULTS = []
RESULTS.append(Result("61615", "61550","CH Robinson","CRS","12.2", "TL", "closed van"))
RESULTS.append(Result("61610", "61550","Trans air inc","TXHS","145.2", "LTL", "closed van"))
RESULTS.append(Result("61610", "61550","CEVA  inc","CEVA","245.2", "TL", "closed van"))
RESULTS.append(Result("61210", "61550","DHL inc","TXHS","145.2", "LTL", "closed van"))
RESULTS.append(Result("61310", "61550","DTDC air inc","TXHS","145.2", "LTL", "closed van"))
RESULTS.append(Result("61410", "61550","MEARSK inc","TXHS","145.2", "LTL", "closed van"))

# --------------- entry point -----------------

def lambda_handler(event, context):
    """ App entry point  """
    
    if event['request']['type'] == "LaunchRequest":
        return on_launch()
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'])


# --------------- response handlers -----------------

def on_intent(request, session):
    """ Called on receipt of an Intent  """

    intent = request['intent']
    intent_name = request['intent']['name']

    #print("on_intent " +intent_name)
    #get_state(session)

    if 'dialogState' in request:
        #delegate to Alexa until dialog sequence is complete
        if request['dialogState'] == "STARTED" or request['dialogState'] == "IN_PROGRESS":
            return dialog_response("", False)

    print("*****Intent name "+intent_name)
    # process the intents
    if intent_name == "RoutingGuide":
        return search_rates(request['intent'])
    elif intent_name == "AMAZON.HelpIntent":
        return do_help()
    elif intent_name == "AMAZON.StopIntent":
        return do_stop()
    elif intent_name == "AMAZON.CancelIntent":
        return do_stop()
    elif intent_name == "AMAZON.StartoverIntent":
        return search_rates(request)
    else:
        print("invalid intent reply with help")
        return do_help()


def search_rates(intent):
    """ return best carrier rates """
    print(intent)
    print("-----------intent")
    print(intent.get('slots'))
    attributes = {"state":globals()['STATE']}

    itemt, propname = get_item(intent.get('slots'))
    print("*****item value is :")
    print(itemt)
    if itemt is None:
        speech_message = get_nolanefound_answer(propname)
        attributes.update({"response": speech_message})
        return response(attributes, response_plain_text(speech_message, False))

    speech = get_rates_response(itemt)
    return response(attributes,
                        response_ssml_text_reprompt(speech, False, REPROMPT_SPEECH))

def get_item(slots):
    """ return the item matching the users request, if found, or original text if not """

    properties = Item.properties()
    propertyvaluetext = ""

    x = Item("","","","","")
    
    print(slots.items())
    
    for key, val in slots.items():
        print("---Key"+ key +" Value:"+ str(val.get('value')))
        
        
        if val.get('value') is None:
            print("value is none")
        else:
            #print(((val.get('resolutions').get('resolutionsPerAuthority')[0]).get('values')[0]).get('value').get('name'))
            tempvalue = ''
            if ((val.get('resolutions').get('resolutionsPerAuthority')[0]).get('values')[0]).get('value').get('name') is None:
                tempvalue = val.get('value')
            else:
                tempvalue = ((val.get('resolutions').get('resolutionsPerAuthority')[0]).get('values')[0]).get('value').get('name')
            
            print("tempvalue is :"+tempvalue)
            if key == 'Region':
                x.region = tempvalue
            elif key == 'Service':
                x.service = tempvalue
            elif key == 'ShipDate':
                x.shipdate = tempvalue
            elif key == 'Origin':
                x.origin = tempvalue
            elif key == 'Destination':
                x.destination = tempvalue

    print("data  x.origin:"+x.origin + " -x.origin:"+x.destination)
    
    
    for i in RESULTS:
        print("data matched x.origin:"+x.origin+" i.property_value(x.origin):"+i.property_value('origin'))
        print("data matched x.destination:"+x.destination+" i.property_value(x.destination):"+i.property_value('destination'))
        
        if x.origin != '' and x.destination != '' and x.service != '' and x.origin == i.property_value('origin') and x.destination == i.property_value('destination') and x.service == i.property_value('service'):
            print("data matched")
            return i, x.origin

    return (None, propertyvaluetext)


def get_rates_response(item1):
    """ get response to the question based on correct or incorect response"""

    carriername = item1.carriername
    carriercode = item1.carriercode
    rate = item1.rate
    service = item1.service
    equipmenttype = item1.equipmenttype
    
    validLanes = r1.get_valid_rates(origin, destination, service)
    print("-----------got response from webservice call")
    return (
        ' For Origin '+item1.origin+ ' and Destination '+item1.destination+
        ' Best Caterpillar approved Carrier is ' +validLanes[0].carriername +
        '. Price charged by ' +validLanes[0].carriername +' for this lane and service '+validLanes[0].service +', is '+validLanes[0].rate +' dollars,'
        ' and the abbreviation for ' +validLanes[0].carriername +' is ' +validLanes[0].carrierscac +'.'
        ' Equipment type used by this carrier is '  +validLanes[0].equipmenttype +'. '
        ' For which other Origin and destination and service you would like to know carriers?'
    )


def do_stop():
    """  stop the app """

    attributes = {"state":globals()['STATE']}
    return response(attributes, response_plain_text(EXIT_SKILL_MESSAGE, True))

def do_help():
    """ return a help response  """

    global STATE
    STATE = STATE_START
    attributes = {"state":globals()['STATE']}
    return response(attributes, response_plain_text(HELP_MESSAGE, False))

def on_launch():
    """ called on Launch reply with a welcome message """
 
    return get_welcome_message()

def on_session_ended(request):
    """ called on session end  """

    if request['reason']:
        end_reason = request['reason']
        print("on_session_ended reason: " + end_reason)
    else:
        print("on_session_ended")

def get_state(session):
    """ get and set the current state  """

    global STATE

    if 'state' in session['attributes']:
        STATE = session['attributes']['state']
    else:
        STATE = STATE_START


# --------------- response string formatters -----------------
def get_welcome_message():
    """ return a welcome message """

    attributes = {"state":globals()['STATE']}
    return response(attributes, response_plain_text(WELCOME_MESSAGE, False))


def get_badanswer(outtext):
    """ bad answer response """

    if outtext == "":
        outtext = "This"
    return ("I'm sorry. " +outtext +" is not something I know very "
            "much about in this skill. " +HELP_MESSAGE)

def get_nolanefound_answer(outtext):
    """ No lane found answer response """

    return ("I'm sorry. I could not find any matching lanes for this combination, "
            "Please try with other combination. " +REPROMPT_SPEECH)

def get_smallimage(name):
    """ return image url """

    return ("https://m.media-amazon.com/images/G/01/mobile-apps/dex/alexa/alexa-skills-kit"
            "/tutorials/quiz-game/state_flag/720x400/" +name +"._TTH_.png")


def get_largeimage(name):
    """get large version of the card image.  It should be 1200x800 pixels in dimension."""

    return ("https://m.media-amazon.com/images/G/01/mobile-apps/dex/alexa/alexa-skills-kit"
            "/tutorials/quiz-game/state_flag/1200x800/" +name +"._TTH_.png")

# --------------- speech response handlers -----------------
#  for details of Json format see:
#  https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/docs/alexa-skills-kit-interface-reference

def response_plain_text(output, endsession):
    """ create a simple json plain text response  """

    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'shouldEndSession': endsession
    }


def response_ssml_text(output, endsession):
    """ create a simple json plain text response  """

    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': "<speak>" +output +"</speak>"
        },
        'shouldEndSession': endsession
    }

def response_ssml_text_and_prompt(output, endsession, reprompt_text):
    """ create a Ssml response with prompt  """

    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': "<speak>" +output +"</speak>"
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'SSML',
                'ssml': "<speak>" +reprompt_text +"</speak>"
            }
        },
        'shouldEndSession': endsession
    }


def response_ssml_cardimage_prompt(title, output, endsession, cardtext, abbreviation, reprompt):
    """ create a simple json plain text response  """

    smallimage = get_smallimage(abbreviation)
    largeimage = get_largeimage(abbreviation)
    return {
        'card': {
            'type': 'Standard',
            'title': title,
            'text': cardtext,
            'image':{
                'smallimageurl':smallimage,
                'largeimageurl':largeimage
            },
        },
        'outputSpeech': {
            'type': 'SSML',
            'ssml': "<speak>" +output +"</speak>"
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'SSML',
                'ssml': "<speak>" +reprompt +"</speak>"
            }
        },
        'shouldEndSession': endsession
    }

def response_ssml_text_reprompt(output, endsession, reprompt_text):
    """  create a simple json response with a card  """

    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': "<speak>" +output +"</speak>"
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'SSML',
                'ssml': "<speak>" +reprompt_text +"</speak>"
            }
        },
        'shouldEndSession': endsession
    }

def dialog_response(attributes, endsession):
    """  create a simple json response with card """

    return {
        'version': '1.0',
        'sessionAttributes': attributes,
        'response':{
            'directives': [
                {
                    'type': 'Dialog.Delegate'
                }
            ],
            'shouldEndSession': endsession
        }
    }

def response(attributes, speech_response):
    """ create a simple json response """

    return {
        'version': '1.0',
        'sessionAttributes': attributes,
        'response': speech_response
    }