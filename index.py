from __future__ import print_function
from watsonAlchemy import getSentiment
from findPlaylist import findPlaylist
import requests
import json

# --------------- Helpers that build all of the responses ----------------------
def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }

# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to Hash Hacks 2017 project High Spirits. " \
                    "Please tell me how your day was "
    reprompt_text = "I didn't catch that. " \
                    "Please tell me how your day was by saying something like " \
                    "My day was pretty good, thank you."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying High Spirits Hash Hacks 2017 Project. " \
                    "Have a nice day! "
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def convert_feelings_to_rating(feeling):
    ratingJSON = getSentiment(feeling)
    return ratingJSON['score']

def set_mood_in_session(intent, session):
    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    if 'feel' in intent['slots']:
        feeling = intent['slots']['feel']['value']
        score = convert_feelings_to_rating(feeling)
        session_attributes['userResponse'] = feeling
        session_attributes['score'] = score
        session_attributes['playlists'] = findPlaylist(float(score))
        session_attributes['index'] = 0
        currentPlaylist = session_attributes['playlists'][session_attributes['index']]['name']
        #score = float(score)
        score=0
        if score < -0.8:
            speech_output = "I'm sorry to hear that. I've curated some playlists based on your current mood. Would you like to listen to " + currentPlaylist
        elif score < -0.5:
            speech_output = "I'm sure your day will get better. I've curated some playlists based on your current mood. Would you like to listen to " + currentPlaylist
        elif score < 0:
            speech_output = "I feel you. I've curated some playlists based on your current mood. Would you like to listen to " + currentPlaylist
        elif score < 0.5:
            speech_output = "I'm glad to hear that. I've curated some playlists based on your current mood. Would you like to listen to " + currentPlaylist
        else:
            speech_output = "That's so lit. I've curated some playlists based on your current mood. Would you like to listen to " + currentPlaylist
        reprompt_text = ". Sorry, I didn't catch that. Would you like to listen to " + \
                        currentPlaylist
    else:
        speech_output = "I'm not sure how you're feeling. " \
                        "Please tell me how your day has been."
        reprompt_text = "I'm not sure how you're feeling. " \
                        "Please tell me how your day has been."
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def cheerUp(intent, session):
    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    if "playlists" in session.get('attributes', {}):
        score = 1
        session_attributes['score'] = score
        session['attributes']['playlists'] = findPlaylist(score)
        session['attributes']['index'] = 0
        currentPlaylist = session['attributes']['playlists'][session['attributes']['index']]['name']
        speech_output = "I'll make you feel better. Would you like to listen to " + \
                        currentPlaylist
        reprompt_text = ". Sorry, I didn't catch that. Would you like to listen to " + \
                        currentPlaylist
    else:
        speech_output = "I'm not sure how you're feeling. " \
                        "Please tell me how your day has been."
        reprompt_text = "I'm not sure how you're feeling. " \
                        "Please tell me how your day has been."
    return build_response(session['attributes'], build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_playlists_from_session_yes(intent, session):
    session_attributes = {}
    reprompt_text = None
    request = requests.Session()

    if "playlists" in session.get('attributes', {}):
        playlists = session['attributes']['playlists']
        index = session['attributes']['index']
        currentPlaylist = playlists[index]['name']
        #currentURI = playlists[index]['URI']
        #url = 'http://6da862e2.ngrok.io/AllTheFeels/webresources/allthefeels/spotify/'
        #request.get(url+str(currentURI))
        session['attributes']['index'] = index + 1
        speech_output = "Say no more, Now Playing " + currentPlaylist
        should_end_session = True
    else:
        speech_output = "I'm not sure what your favorite color is. " \
                        "You can say, my favorite color is red."
        should_end_session = False

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session['attributes'], build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))


def get_playlists_from_session_no(intent, session):
    session_attributes = {}

    if "playlists" in session.get('attributes', {}):
        playlists = session['attributes']['playlists']
        index = session['attributes']['index']
        session['attributes']['index'] = index + 1
        currentPlaylist = playlists[index+1]['name']

        if index < len(playlists):
            speech_output = "Alright, would you like to listen to " + currentPlaylist + \
                            " instead."
            reprompt_text = "Sorry, I didn't catch that. Would you like to listen to " + currentPlaylist + \
                            " instead. "
            should_end_session = False
        else:
            speech_output = "Okay, sorry you didn't like that, but we are all out of options."
            reprompt_text = None
            should_end_session = True
    else:
        speech_output = "I'm not sure what your favorite color is. " \
                        "You can say, my favorite color is red."
        reprompt_text = None
        should_end_session = False

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session['attributes'], build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))


# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "GetFeelIntent":
        return set_mood_in_session(intent, session)
    elif intent_name == "AMAZON.YesIntent":
        return get_playlists_from_session_yes(intent,session)
    elif intent_name == "AMAZON.NoIntent":
        return get_playlists_from_session_no(intent,session)
    elif intent_name == "CheerUp":
        return cheerUp(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])