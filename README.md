# Tubearchivist subscription listener

so in tubearchist the "schedule" feature is not working at all (literally out of nowhere, i haven't modified any settings. no logs.)

this tool uses the youtube data api to check every channel for new videos. if there is any new videos, it will send tubearchivist those videos

i also saw that the tubearchivist project paywalled real time channel notifications. i make feature free.

## why cant you just fix the bug in tubearchivist?

not a fan of the codebase

this is somehow easier 

## usage 
can be used in a cli.
clone and install dependencies. then run `python main.py -h` 

### docker

```yaml
services:
    ta-sub-listener:
        image: thearyadev0/tubearchivist-subscription-listener:latest # or version tag
        environment:
            TUBEARCHIVIST_URL: ""
            API_TOKEN: "" # tubearchivist api token
            YOUTUBE_TOKEN: "" # youtube data v3 api token
            AUTOSTART: "True" # or False
            REPEAT: "50" # times to repeat in one day

            ## each channel uses 2 quota units per scan. if i have 100 channels * 2 units * 50 scans per day, it will use 10000 quota units.
            #
            # the youtube api provides you with 10000 units per day. You may be able to request mor
```

## youtube data api token
[youtube data api docs](https://developers.google.com/youtube/v3/getting-started)

1. go to yourg google cloud console
2. create a new project. 
3. enable the youtube data api
4. generate a new API key from the credentials tab.

license: wtfpl
