# Cisco Spark bot example
This projects provides you with everything you need to set up a Cisco Spark bot.

The bot can process incoming webhook requests and respond to certain events that occur in Spark using the [Cisco Spark REST API](https://developer.ciscospark.com/getting-started.html). Alternatively, you can use the appropiate [Spark SDK](https://github.com/ciscospark) of your choosing.

Before you start, make sure you have a Cisco Spark account by signing up at https://www.ciscospark.com/.

## Getting Started
- Once you have an account, go to the [Cisco Spark Developer portal](https://developer.ciscospark.com/apps.html)
- Go to My Apps and use the green plus icon to create a new Bot
- Give your bot a name, username, icon and description
- Save the bot details and copy the access token
- At the bottom of the `sparkbot.py` file, update the bot details and set the `bearer` variable equal to the bot's access token 

```python
#Replace these next three lines with your own Spark bot's information
bot_email = "yourbot@sparkbot.io"
bot_name = "yourbot"
bearer = "YOUR_TOKEN_HERE"
```

### Creating a webhook
You can use the [Cisco Spark Webhooks API](https://developer.ciscospark.com/endpoint-webhooks-post.html) to create a new webhook, update an existing webhook, or delete a webhook when it's no longer needed.

When you create a webhook for a particular event, the notification data will be sent as an HTTP POST, in JSON format, to a URL of your choosing, each time it is triggered. 

Please note, that this URL must be publicly reachable and Internet-accessible by Cisco Spark, where your application will be listening for inbound HTTP requests. 

You can find a list of all the possible resources, filters, and events [here](https://developer.ciscospark.com/webhooks-explained.html#resources-events).

### Secret Validation

```python
@post('/')
def index(request):
    """
    When messages come in from the webhook, they are processed here.
    X-Spark-Signature - The header containing the sha1 hash we need to validate
    request.body - the Raw JSON String we need to use to validate the X-Spark-Signature
    """
    raw = request.body
    #Let's create the SHA1 signature 
    #based on the request body JSON (raw) and our passphrase (key)
    hashed = hmac.new(key, raw, hashlib.sha1)
    validatedSignature = hashed.hexdigest()
    
    print 'validatedSignature', validatedSignature
    print 'X-Spark-Signature', request.headers.get('X-Spark-Signature')
    print 'Equal?', validatedSignature == request.headers.get('X-Spark-Signature')
    
    return "true"

#Replace this with the secret phrase you used in the webhook creation
key = "somesupersecretphrase"
```

### Downloading files

```python
@post('/')
def index(request):
    webhook = json.loads(request.body)
    if webhook['data'].has_key('files'):
        for file_url in webhook['data']['files']:
            response = sendSparkGET(file_url)
            content_disp = response.headers.get('Content-Disposition', None)
            if content_disp is not None:
                filename = content_disp.split("filename=")[1]#split on the string "filename=", then save the second item as name
                filename = filename.replace('"', '')
                with open(filename, 'w') as f:
                    f.write(response.read())
                    print 'Saved-', filename
            else:
                print "Cannot save file- no Content-Disposition header received."
    else:
        print "No files attached to retrieve!"
    return "true"
```

### Uploading local files

```python
from requests_toolbelt import MultipartEncoder
import requests

filepath    = '/Users/taylorhanson/Desktop/screenshot.png'
filetype    = 'image/png'
roomId      = 'SOME ROOM'
token       = 'YOUR ACCOUNT BEARER TOKEN'
url         = "https://api.ciscospark.com/v1/messages"

my_fields={'roomId': roomId, 
           'text': 'Hello World',
           'files': ('screenshot', open(filepath, 'rb'), filetype)
           }
m = MultipartEncoder(fields=my_fields)
r = requests.post(url, data=m,
                  headers={'Content-Type': m.content_type,
                           'Authorization': 'Bearer ' + token})
print r.json()
```

You can also upload files to a specific room using a URL like so:

```python
my_url = "linkToImage.jpg"
sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "files": my_url})
```

## Alternatives

Need more examples? Check out some of our open source [starter kits and more bots](https://ciscosparkambassadors.github.io/StarterKits/).

Our starter kits abstract all the webhook processing away by using [BotKit](https://botkit.ai/).

