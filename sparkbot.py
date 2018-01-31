from itty import *
import urllib2
import json

"""
Spark REST API functions
"""
def sendSparkGET(url):
    request = urllib2.Request(url,
                            headers={"Accept" : "application/json",
                                     "Content-Type":"application/json"})
    request.add_header("Authorization", "Bearer "+bearer)
    contents = urllib2.urlopen(request).read()
    return contents
    
def sendSparkPOST(url, data):
    request = urllib2.Request(url, json.dumps(data),
                            headers={"Accept" : "application/json",
                                     "Content-Type":"application/json"})
    request.add_header("Authorization", "Bearer "+bearer)
    contents = urllib2.urlopen(request).read()
    return contents

"""
Handle POST requests incoming from the webhook
"""
@post('/')
def index(request):
    raw = request.body
    hashed = hmac.new(key, raw, hashlib.sha1)
    validatedSignature = hashed.hexdigest()
    print 'validatedSignature', validatedSignature
    print 'X-Spark-Signature', request.headers.get('X-Spark-Signature')
    returnVal = ""
    if validatedSignature == request.headers.get('X-Spark-Signature'):
        webhook = json.loads(raw)
        print webhook['data']['id']
        requester = webhook['data']['personEmail']
        if requester != bot_email:
            #get person information, specifically need the person's orgId
            person = sendSparkGET('https://api.ciscospark.com/v1/people/{0}'.format(webhook['data']['personId']))
            if json.loads(person)['orgId'] == my_org_id or requester in auth_users:
                result = sendSparkGET('https://api.ciscospark.com/v1/messages/{0}'.format(webhook['data']['id']))
                result = json.loads(result)
                in_message = result.get('text', '').lower()
                in_message = in_message.replace(bot_name, '')
                #echo the message back to the same room
                sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "text": in_message})
                returnVal = "success"
            else:
                print "orgId does not match or person not in list of authorized users"
    else:
        print "Secret does not match!"
    return returnVal


#Replace this with the secret phrase you used in the webhook creation
key = "webhook_secret_phrase"

#Change to your email, or list of correct email addresses
auth_users = ['youremail@yourdomain.com'] 

#Change below line to be your own OrgId
my_org_id = "ORG_ID_HERE"

#Replace these next three lines with your own Spark bot's information
bot_email = "yourbot@sparkbot.io"
bot_name = "yourbot"
bearer = "YOUR_TOKEN_HERE"

run_itty(server='wsgiref', host='0.0.0.0', port=10010)