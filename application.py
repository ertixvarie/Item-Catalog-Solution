from flask import Flask, session, render_template, url_for, request, redirect, jsonify, flash
from flask import make_response, session as login_session
from CRUD import makeSession, getJobs, getWeapons, addEntry, deleteEntry
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from database_setup import Base, Job, Weapon, User
import random, string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests
import os

app = Flask(__name__)


CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    login_session['access_token'] = access_token
    print login_session['access_token']
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    #login_session['access_token'] = access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session['access_token']
    print login_session.keys()
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:

        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/')
@app.route('/jobs/')
def displayJobs():
    session = makeSession()
    jobs = getJobs(session)
    try:
        login_session['username'] != None
        user = login_session['username']
        return render_template('jobs.html', jobs=jobs, user=user)
    except:
        return render_template('jobs.html', jobs=jobs, user=None)


@app.route('/weapons/')
def getAllWeapons():
    session = makeSession()
    weapons = getWeapons(session)
    return render_template('weapons.html', weapons=weapons)


@app.route('/jobs/<string:job_req>/')
def getWeaponFor(job_req):
    session = makeSession()
    weapons = session.query(Weapon).filter_by(job_req = job_req).all()
    try:
        login_session['user_id'] != None
        user_id = login_session['user_id']
        return render_template('weapons.html', weapons = weapons, job_req = job_req, user_id = user_id)
    except:
        return render_template('weapons.html', weapons = weapons, job_req = job_req, user_id = None)


@app.route('/jobs/<string:job_req>/<int:user_id>/new', methods=['GET','POST'])
def newWeapon(job_req, user_id):
    session = makeSession()
    if request.method == 'POST':
        job = session.query(Job).filter_by(name = job_req)
        weapon = Weapon(name = request.form['name'], level = request.form['level'], job_req = job_req, user_id=login_session['user_id'])
        addEntry(session, weapon)
        return redirect(url_for('getWeaponFor', job_req = job_req))
    else:
        return render_template('newweapon.html', job_req = job_req, user_id = login_session['user_id'])


@app.route('/jobs/<string:job_req>/<int:id>/edit/', methods=['GET','POST'])
def editWeapon(job_req, id):
    session = makeSession()
    weaponToEdit = session.query(Weapon).filter_by(id = id).one()
    if request.method == 'POST':
        if request.form['name']:
            weaponToEdit.name = request.form['name']
        if request.form['level']:
            weaponToEdit.level = request.form['level']
        addEntry(session, weaponToEdit)
        return redirect(url_for('getWeaponFor', job_req = job_req))
    else:
        return render_template('edit.html', job_req = job_req, id = id, weapon = weaponToEdit)


@app.route('/jobs/<string:job_req>/<int:id>/delete', methods=['GET','POST'])
def deleteWeapon(job_req, id):
    session = makeSession()
    weaponToDelete = session.query(Weapon).filter_by(id = id).one()
    if request.method == 'POST':
        deleteEntry(session, weaponToDelete)
        return redirect(url_for('getWeaponFor', job_req = job_req))
    else:
        return render_template('delete.html', job_req = job_req, id = id, weapon = weaponToDelete)


@app.route('/jobs/<string:job_req>/JSON')
def getWeaponsByJobForJSON(job_req):
    session = makeSession()
    weapons = session.query(Weapon).filter_by(job_req = job_req).all()
    return jsonify(weapon=[wpn.serialize for wpn in weapons])


@app.route('/jobs/<string:job_req>/<int:id>/JSON')
def getWeaponByIdForJSON(job_req, id):
    session = makeSession()
    weapons = session.query(Weapon).filter_by(id = id)
    return jsonify(weapon=[wpn.serialize for wpn in weapons])

# User Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session['email'], picture=login_session['picture'])
    session = makeSession()
    addEntry(session, newUser)
    user = session.query(User).filter_by(email=login_session['email']).first()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
