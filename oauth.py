"""                _               
  __      _____| |__   _____  __
  \ \ /\ / / _ \ '_ \ / _ \ \/ /
   \ V  V /  __/ |_) |  __/>  <         @WebexDevs
    \_/\_/ \___|_.__/ \___/_/\_\

"""

# -*- coding:utf-8 -*-
from webbrowser import get
import requests
import json
import os


from flask import Flask, render_template, request, session, url_for, flash, redirect
from webexteamssdk import WebexTeamsAPI

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
app.secret_key = os.urandom(24)

clientID = "YOUR CLIENT ID"
secretID = "YOUR CLIENT SECRET"
redirectURI = "http://0.0.0.0:10060/oauth" #This could be different if you publicly expose this endpoint.


"""
Function Name : get_tokens
Description : This is a utility function that takes in the 
              Authorization Code as a parameter. The code 
              is used to make a call to the access_token end 
              point on the webex api to obtain a access token
              and a refresh token that is then stored as in the 
              Session for use in other parts of the app. 
              NOTE: in production, auth tokens would not be stored
              in a Session. This app will request a new token each time
              it runs which will not be able to check against expired tokens. 
"""
def get_tokens(code):
    print("code:", code)
    #STEP 3 : use code in response from webex api to collect the code parameter
    #to obtain an access token or refresh token
    url = "https://webexapis.com/v1/access_token"
    headers = {'accept':'application/json','content-type':'application/x-www-form-urlencoded'}
    payload = ("grant_type=authorization_code&client_id={0}&client_secret={1}&"
                    "code={2}&redirect_uri={3}").format(clientID, secretID, code, redirectURI)
    req = requests.post(url=url, data=payload, headers=headers)
    results = json.loads(req.text)
    access_token = results["access_token"]
    refresh_token = results["refresh_token"]
    session['oauth_token'] = access_token
    session['refresh_token'] = refresh_token
    return 

"""
Function Name : get_tokens
Description : This is a utility function that takes in the code
              and a Refresh Token as a parameter. The code 
              is used to make a call to the access_token end 
              point on the webex api to obtain a access token
              and a refresh token that is then stored as in the 
              Session for use in other parts of the app. 
"""
def get_tokens_refresh(refresh):
    print("refresh:", refresh)
    #STEP 3 : use code in response from webex api to collect the code parameter
    #to obtain an access token or refresh token
    url = "https://webexapis.com/v1/access_token"
    headers = {'accept':'application/json','content-type':'application/x-www-form-urlencoded'}
    payload = ("grant_type=refresh_token&client_id={0}&client_secret={1}&"
                    "refresh_token={2}").format(clientID, secretID, refresh)
    req = requests.post(url=url, data=payload, headers=headers)
    results = json.loads(req.text)
    access_token = results["access_token"]
    refresh_token = results["refresh_token"]

    session['oauth_token'] = access_token
    session['refresh_token'] = refresh_token
    return 

"""
Function Name : main_page
Description : when using the browser to access server at
              http://127/0.0.1:10060 this function will 
              render the html file index.html. That file 
              contains the button that kicks off step 1
              of the Oauth process with the click of the 
              grant button
"""
@app.route("/") 

def main_page():
    """Main Grant page"""
    return render_template("index.html")

"""
Function Name : oauth
Description : After the grant button is click from index.html
              and the user logs into thier Webex account, the 
              are redirected here as this is the html file that
              this function renders upon successful authentication
              is granted.html. else, the user is sent back to index.html
              to try again. This function retrieves the authorization
              code and calls get_tokens() for further API calls against
              the Webex API endpoints. 
"""
@app.route("/oauth") #Endpoint acting as Redirect URI.

def oauth():
    """Retrieves oauth code to generate tokens for users"""
    state = request.args.get("state")
    print('state : ' + state)
    if state == '1234abcd':
        code = request.args.get("code") # STEP 2 : Capture value of the 
                                        # authorization code.
        print("OAuth code:", code)
        print("OAuth state:", state)
        get_tokens(code)
        return render_template("granted.html")
    else:
        return render_template("index.html")

"""
Function Name : create
Description : This functions receives form data from granted.html
              and leverages the WebexTeams Python SDK to create a 
              Webex user within the org of the Admin that initiates 
              The OAuth flow.  
"""
@app.route("/create",methods=['GET', 'POST'])
def  create():
    #some improvements here could be to seet the oauth token into a
    #WEBEX_TEAMS_ACCESS_TOKEN environment variable and initiate the
    #sdk without any parameters in the constructor.
    api = WebexTeamsAPI(access_token=session["oauth_token"])
    emails = []
    if request.method == "POST":
       # getting data from HTML form and assigning variables
       emails.append(request.form.get("email"))
       display_name = request.form.get("displayname")
       first_name = request.form.get("firstname")
       last_name = request.form.get("lastname")
    #leveraging variables to create user. 
    # see https://webexteamssdk.readthedocs.io/en/latest/user/api.html#people 
    # see https://developer.webex.com/docs/api/v1/people/create-a-person for additional information
    joe = api.people.create(emails, displayName=display_name, firstName=first_name, lastName=last_name)
    print(joe.displayName + ' was created!')
    return render_template("granted.html")

if __name__ == '__main__':
    app.run("0.0.0.0", port=10060, debug=False)