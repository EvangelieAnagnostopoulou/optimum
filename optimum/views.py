import urllib2

from googleapiclient.discovery import build

__author__ = 'evangelie'
import webbrowser
import httplib2
from optimum.models import UserCredentials
from optimum.utils import creds_to_json, creds_from_json
from apiclient import errors
from apiclient import http
import os
from django.http import HttpResponse
from django.template.context import RequestContext
import requests
from django.shortcuts import render, redirect, render_to_response
from optimum.twitter import get_tweets
from optimum.personality import get_profil
import json
from pprint import pprint
from social.apps.django_app.default.models import UserSocialAuth
#from apiclient.discovery import build
import oauth2client
from oauth2client import client
from oauth2client import tools
import logging
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from apiclient import errors
from models import UserFacebookData

import datetime
from django.conf import settings
from oauth2client import GOOGLE_REVOKE_URI, GOOGLE_TOKEN_URI
from oauth2client.client import OAuth2Credentials, _extract_id_token
#from oauth2client.django_orm import Storage
from gcm import*

# Home page
def index(request):
    if request.method == 'GET':
        if not request.user:
            return redirect('/accounts/login')

        #Get all tweets of user written in English
        #all_tweets = get_tweets()
        #print all_tweets
        #Get Big 5 personality using IBM watson API
        '''response = get_profil(all_tweets)
        try:
            print json.loads(response.text)
            personality = json.loads(response.text)

        except:
            raise Exception("Error processing the request, HTTP: %d" % response.status_code)'''
        try:
            social_user = request.user.social_auth.filter(provider='facebook',).first()

            url = u'https://graph.facebook.com/{0}/' \
                  u'friends?fields=id,name,location,picture' \
                  u'&access_token={1}'.format(
                      social_user.uid,
                      social_user.extra_data['access_token'],
                  )
            url = u'https://graph.facebook.com/{0}/' \
                  u'likes?access_token={1}&limit=1000'.format(
                      social_user.uid,
                      social_user.extra_data['access_token'],
                  )
            #url = 'https://graph.facebook.com/v2.5/me/friends?access_token='+social_user.extra_data['access_token']
            print url
            res = requests.get(url)
            print res.text
            likes=json.loads(res.text)
            url2= u'https://graph.facebook.com/{0}/' \
                  u'photos?fields=source&limit=1000&access_token={1}'.format(
                      social_user.uid,
                      social_user.extra_data['access_token'],
                  )
            print url2
            res2 = requests.get(url2)
            print json.loads(res2.text)
            photos = json.loads(res2.text)
            url3= u'https://graph.facebook.com/{0}/' \
                  u'feed?limit=10000&access_token={1}'.format(
                      social_user.uid,
                      social_user.extra_data['access_token'],
                  )
            print url3
            res3 = requests.get(url3)
            print json.loads(res3.text)
            posts = json.loads(res3.text)

            user_facebook = UserFacebookData.objects.filter(user=social_user)
            if not user_facebook:
                new_user_data = UserFacebookData.objects.create(user = social_user, likes=likes, photos=photos, posts=posts)
            else:
                user_data = UserFacebookData.objects.get(user=social_user)
                user_data.likes = likes
                user_data.photos = photos
                user_data.posts = posts
                #user_data.update(likes = likes, photos = photos)'''
        except:
            print('not auth')
        data = open(os.path.join(os.path.dirname(os.path.dirname(__file__)),'optimum/static/files/new_2.gpx'), 'r')
        #return render(request, "map.html" )
        if request.is_ajax():
            data = open(os.path.join(os.path.dirname(os.path.dirname(__file__)),'optimum/static/files/new_2.gpx'), 'r')
            #data= open('/static/files/new.gpx', 'r')
            #origin lat="38.059016" lon="23.755915"
            #dest lat="38.012388" lon="23.637945"
            print data
            return HttpResponse(data)

        return render(request, "mainPage.html",)

'''def history_routes(request):
    if request.method == 'GET':

        data = open(os.path.join(os.path.dirname(os.path.dirname(__file__)),'optimum/static/files/new_2.gpx'), 'r')
        #return render(request, "map.html" )
        if request.is_ajax():
            data = open(os.path.join(os.path.dirname(os.path.dirname(__file__)),'optimum/static/files/new_2.gpx'), 'r')
            #data= open('/static/files/new.gpx', 'r')
            #origin lat="38.059016" lon="23.755915"
            #dest lat="38.012388" lon="23.637945"
            return HttpResponse(data)

        return render(request, "map.html")'''

def tracks(request):
    if request.method == 'GET':
        current_user = request.user
        try:
            instance = UserSocialAuth.objects.filter(provider='google-oauth2', user_id=current_user.id).get()

        except:
            data = open(os.path.join(os.path.dirname(os.path.dirname(__file__)),'optimum/static/files/new_2.gpx'), 'r')
            return redirect('/path')
        pprint(instance.tokens)
        print instance.tokens
        print instance.tokens['access_token']
        service= get_service(request)
        result = retrieve_all_files(service)
        print result
        return render(request, "tracks.html", {'result': result} )


def path(request):
    if request.method == 'GET':
        file=request.GET.get('file')
        if not file or file == 'None':
            data = open(os.path.join(os.path.dirname(os.path.dirname(__file__)),'optimum/static/files/new_2.gpx'), 'r')
        else:
            service = get_service(request)
        if request.is_ajax():
            if not file or file == 'None':
                data = open(os.path.join(os.path.dirname(os.path.dirname(__file__)),'optimum/static/files/new_2.gpx'), 'r')
            else:
                data = get_file_content(service, file)
            return HttpResponse(data)

        return render(request, "map.html", {'file': file})


def retrieve_all_files(service):
  """Retrieve a list of File resources.

  Args:
    service: Drive API service instance.
  Returns:
    List of File resources.
  """
  result = []
  page_token = None
  while True:
    try:
      param = {}
      if page_token:
        param['pageToken'] = page_token
      param['q'] = "fileExtension = 'gpx'"
      files = service.files().list(**param).execute()

      result.extend(files['items'])
      page_token = files.get('nextPageToken')
      if not page_token:
        break
    except errors.HttpError, error:
      print 'An error occurred: %s' % error
      break
  return result

def build_service(credentials):
  """Build a Drive service object.

  Args:
    credentials: OAuth 2.0 credentials.

  Returns:
    Drive service object.
  """
  http = httplib2.Http()
  http = credentials.authorize(http)
  return build('drive', 'v2', http=http)


def get_file_content(service, file_id):
  """Get a file's content.

  Args:
    service: Drive API service instance.
    file_id: ID of the file.

  Returns:
    File's content if successful, None otherwise.
  """
  try:
    return service.files().get_media(fileId=file_id).execute()
  except errors.HttpError, error:
    return 'An error occurred: %s' % error

def get_service(request):

        flow = flow_from_clientsecrets('optimum\static\json\json_credentials.json',
        #flow = flow_from_clientsecrets('/root/optimum/optimum/static/json/json_credentials.json',
                               scope='https://www.googleapis.com/auth/drive',
                               redirect_uri='http://snf-697531.vm.okeanos.grnet.gr:8088/')

        auth_uri = flow.step1_get_authorize_url()
        print auth_uri
        current_user = request.user
        user = UserSocialAuth.objects.get(provider='google-oauth2', user=current_user.id)
        q = UserCredentials.objects.filter(user=user.user)

        if not q:
            if request.GET.get('code'):
                code = request.GET.get('code')
                request.session['code'] = code
                credentials = flow.step2_exchange(code)
                cred = UserCredentials.objects.create(user=user.user, credentials=creds_to_json(credentials))
                service = build_service(credentials)
                return service
            else:
                return redirect(auth_uri)
        else:

            cred = UserCredentials.objects.get(user=user.user)
            print cred.id
            code = request.session.get('code', '')
            print code
            credentials = creds_from_json(cred.credentials)

            service = build_service(credentials)

        return service

def send_notification(request):
    #r = requests.get("http://snf-697531.vm.okeanos.grnet.gr:8888")
    #print r.text
    #import pdb;pdb.set_trace()
    gcm = GCM("AIzaSyADUIx64P0lGuxHhYfY67Jru2TAFtXONzk")
    data = {'the_message': 'You have x new friends', 'param2': 'value2'}

    #reg_id = 'APA91bHDRCRNIGHpOfxivgwQt6ZFK3isuW4aTUOFwMI9qJ6MGDpC3MlOWHtEoe8k6PAKo0H_g2gXhETDO1dDKKxgP5LGulZQxTeNZSwva7tsIL3pvfNksgl0wu1xGbHyQxp2CexeZDKEzvugwyB5hywqvT1-UxxxqpL4EUXTWOm0RXE5CrpMk'
    #reg_id = 'dzLX8Hohdkg:APA91bFoSI3exsxUZhiJPJm1qmBqyJbXPwmCTpV2iCfCSCLMNVeibHDKDX-mZQd7of_Yw9qevSmRWtTIknJtZE9rko8EbC0751DFeWm7TqO1z34DGwgInSgWPzIKI6fc70u3Jb4iEUVr'
    reg_id = 'dtI_FJY4PFI:APA91bE06xK0ps3sh15p34kntb4NYz2KeksYqLJwikkCPptDQgFDRapvaGkzLI8lpJlGNvfxXB4pbmi39gFt2fRrQlfKPKWsMtxcC1Q-lgRKPKVMzmxtCSksZ7Bsi5vnsegbecbLxsJa'
    notification = {'message': "hello, it's me.", 'click_action':  'Default', "sound": "default", "badge": 2}
    reg_ids = [reg_id]
    #res = gcm.plaintext_request(registration_id=reg_id, data=data)
    response = gcm.json_request(registration_ids=reg_ids, data=notification)
    return render(request, "mainPage.html",)

def get_facebook_data(request):
    social_user = request.user.social_auth.filter(provider='facebook',).first()
    if social_user:
        url = u'https://graph.facebook.com/{0}/' \
              u'friends?fields=id,name,location,picture' \
              u'&access_token={1}'.format(
                  social_user.uid,
                  social_user.extra_data['access_token'],
              )
        url = u'https://graph.facebook.com/{0}/' \
              u'likes?access_token={1}'.format(
                  social_user.uid,
                  social_user.extra_data['access_token'],
              )
        #url = 'https://graph.facebook.com/v2.5/me/friends?access_token='+social_user.extra_data['access_token']
        print url
        res = requests.get(url)
        print res.text
        '''request = urllib2.Request(url)
        friends = json.loads(urllib2.urlopen(request).read()).get('data')
        print friends'''
        #for friend in friends:
    return redirect('/')