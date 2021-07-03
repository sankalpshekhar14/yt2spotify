# YT2Spotify - A program to create a Spotify playlist of songs liked on YouTube.

## Install All Dependencies

``` 
pip install -r requirements.txt 
```

## Get Spotify UserID and Oauth token

* To collect your UserID, log into Spotify then go here: Go to [Account Overview], it is your username.
* To collect Oauth token, go here: [GetOauth]

## Enable Oauth for Youtube and download client_secrets.json

Follow the link here [Set Up Youtube Oauth].

## Run the script 

```
python3 PlaylistHandler.py 
```

##ToDo

* Testing
* Error Handling

##Caution

Spotify Oauth token expires in a short time interval. If `KeyError` is seen, then regenerate the token.


[Get Oauth]: <https://developer.spotify.com/console/post-playlists/>
[Set Up Youtube Oauth]: <https://developers.google.com/youtube/v3/getting-started/>