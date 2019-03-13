from flask import Flask, render_template, url_for
from flask import request, redirect, flash, make_response, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, P_CompName, P_FridgeName, User
from flask import session as p_log_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests
import datetime

# to connect database

engine = create_engine('sqlite:///refrigarators.db',
                       connect_args={'check_same_thread': False}, echo=True)
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json',
                            'r').read())['web']['client_id']
APPLICATION_NAME = "REFRIGARATORS"

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create anti-forgery state token
pfridge_cat = session.query(P_CompName).all()


# User login
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    p_log_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    pshoes_cat = session.query(P_CompName).all()
    sc = session.query(P_FridgeName).all()
    return render_template('login.html',
                           STATE=state, pfridge_cat=pfridge_cat, sc=sc)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != p_log_session['state']:
        p_res = make_response(json.dumps('Invalid state parameter.'), 401)
        p_res.headers['Content-Type'] = 'application/json'
        return p_res
    # Obtain authorization code
    pcode = request.data

    try:
        # Upgrade the authorization code into a credentials object
        p_oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        p_oauth_flow.redirect_uri = 'postmessage'
        credentials = p_oauth_flow.step2_exchange(pcode)
    except FlowExchangeError:
        p_res = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        p_res.headers['Content-Type'] = 'application/json'
        return p_res

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    hp = httplib2.Http()
    result = json.loads(hp.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        p_res = make_response(json.dumps(result.get('error')), 500)
        p_res.headers['Content-Type'] = 'application/json'
        return p_res

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        p_res = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        p_res.headers['Content-Type'] = 'application/json'
        return p_res

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        p_res = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print ("Token's client ID does not match app's.")
        p_res.headers['Content-Type'] = 'application/json'
        return p_res

    stored_access_token = p_log_session.get('access_token')
    stored_gplus_id = p_log_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        p_res = make_response(json.dumps(
            'Current user already connected.'), 200)
        p_res.headers['Content-Type'] = 'application/json'
        return p_res

    # Store the access token in the session for later use.
    p_log_session['access_token'] = credentials.access_token
    p_log_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    p_log_session['username'] = data['name']
    p_log_session['picture'] = data['picture']
    p_log_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(p_log_session['email'])
    if not user_id:
        user_id = createUser(p_log_session)
    p_log_session['user_id'] = user_id

    pop = ''
    pop += '<h1>Welcome, '
    pop += p_log_session['username']
    pop += '!</h1>'
    pop += '<img src="'
    pop += p_log_session['picture']
    pop += ' " style = "width: 300px; height: 300px; border-radius: 150px;'
    '-webkit-border-radius: 150px; -moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % p_log_session['username'])
    print ("done!")
    return pop


# User Helper Functions
def createUser(p_log_session):
    User1 = User(name=p_log_session['username'], email=p_log_session[
                   'email'], picture=p_log_session['picture'])
    session.add(User1)
    session.commit()
    user = session.query(User).filter_by(email=p_log_session['email']).one()
    return user.id


# Uet user information
def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


# get user email address
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except Exception as error:
        print(error)
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session

# Home


@app.route('/')
@app.route('/home')
def home():
    pfridge_cat = session.query(P_CompName).all()
    return render_template('myhome.html', pfridge_cat=pfridge_cat)


# Shoe Category for admins


@app.route('/refrigarators')
def refrigarators():
    try:
        if p_log_session['username']:
            name = p_log_session['username']
            pfridge_cat = session.query(P_CompName).all()
            psm = session.query(P_CompName).all()
            psc = session.query(P_FridgeName).all()
            return render_template('myhome.html', pfridge_cat=pfridge_cat,
                                   psm=psm, psc=psc, uname=name)
    except:
        return redirect(url_for('showLogin'))

######
# Showing shoes based on shoes category


@app.route('/refrigarators/<int:pscid>/AllCompanys')
def showFridges(pscid):
    '''showing all fridges'''
    pfridge_cat = session.query(P_CompName).all()
    psm = session.query(P_CompName).filter_by(id=pscid).one()
    psc = session.query(P_FridgeName).filter_by(compnameid=pscid).all()
    try:
        if p_log_session['username']:
            return render_template('showFridges.html', pfridge_cat=pfridge_cat,
                                   psm=psm, psc=psc,
                                   uname=p_log_session['username'])
    except:
        return render_template('showFridges.html',
                               pfridge_cat=pfridge_cat, psm=psm, psc=psc)


# Add New Fridge Company


@app.route('/refrigarators/addFridgeCompany', methods=['POST', 'GET'])
def addFridgeCompany():
    '''checking if the user is login or not'''
    if 'username' not in p_log_session:
        return redirect(url_for('showLogin'))
    if request.method == 'POST':
        company = P_CompName(
            p_name=request.form['psname'],
            user_id=p_log_session['user_id'])
        session.add(company)
        session.commit()
        return redirect(url_for('refrigarators'))
    else:
        return render_template(
            'addFridgeCompany.html', pfridge_cat=pfridge_cat)


# Edit Fridge Company name


@app.route('/refrigarators/<int:pscid>/edit', methods=['POST', 'GET'])
def editFridgeCompany(pscid):
    pseditFridge = session.query(P_CompName).filter_by(id=pscid).one()
    creator = getUserInfo(pseditFridge.user_id)
    user = getUserInfo(p_log_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != p_log_session['user_id']:
        flash("You cannot edit this  Fridge Company."
              "This is belongs to %s" % creator.name)
        return redirect(url_for('refrigarators'))
    if request.method == "POST":
        if request.form['psname']:
            pseditFridge.p_name = request.form['psname']
        session.add(pseditFridge)
        session.commit()
        flash("Fridge Company Edited Successfully")
        return redirect(url_for('refrigarators'))
    else:
        # shoes_cat is global variable we can them in entire application
        return render_template('editFridgeCompany.html',
                               ptb=pseditFridge, pfridge_cat=pfridge_cat)


# Delete Fridge Company

@app.route('/refrigarators/<int:pscid>/delete', methods=['POST', 'GET'])
def deleteFridgeCompany(pscid):
    ptb = session.query(P_CompName).filter_by(id=pscid).one()
    creator = getUserInfo(ptb.user_id)
    user = getUserInfo(p_log_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != p_log_session['user_id']:
        flash("You cannot Delete this Fridge Company."
              "This is belongs to %s" % creator.name)
        return redirect(url_for('refrigarators'))
    if request.method == "POST":
        session.delete(ptb)
        session.commit()
        flash("Fridge Company Deleted Successfully")
        return redirect(url_for('refrigarators'))
    else:
        return render_template(
            'deleteFridgeCompany.html', ptb=ptb,
            pfridge_cat=pfridge_cat)


# Add New Fridge Details


@app.route(
    '/refrigarators/addFridgeCompany/addFridgeDetails/<string:psmname>/add',
    methods=['GET', 'POST'])
def addFridgeDetails(psmname):
    psm = session.query(P_CompName).filter_by(p_name=psmname).one()
    # See if the logged in user is not the owner of shoes
    creator = getUserInfo(psm.user_id)
    user = getUserInfo(p_log_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != p_log_session['user_id']:
        flash("You can't add new Fridge Details"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('refrigarators', pscid=psm.id))
    if request.method == 'POST':
        f_name = request.form['f_name']
        f_color = request.form['f_color']
        f_capacity = request.form['f_capacity']
        f_doors = request.form['f_doors']
        f_doorlock = request.form['f_doorlock']
        f_price = request.form['f_price']
        f_starrating = request.form['f_starrating']
        fridgedetails = P_FridgeName(f_name=f_name, f_color=f_color,
                                     f_capacity=f_capacity,
                                     f_doors=f_doors,
                                     f_doorlock=f_doorlock,
                                     f_price=f_price,
                                     f_starrating=f_starrating,
                                     f_date=datetime.datetime.now(),
                                     compnameid=psm.id,
                                     user_id=p_log_session['user_id'])
        session.add(fridgedetails)
        session.commit()
        return redirect(url_for('refrigarators', pscid=psm.id))
    else:
        return render_template('addFridgeDetails.html',
                               psmname=psm.p_name, pfridge_cat=pfridge_cat)


# Edit Fridge details


@app.route('/refrigarators/<int:pscid>/<string:psmmname>/edit',
           methods=['GET', 'POST'])
def editFridgeDetails(pscid, psmmname):
    ptb = session.query(P_CompName).filter_by(id=pscid).one()
    fridgedetails = session.query(P_FridgeName).filter_by(
        f_name=psmmname).one()
    # See if the logged in user is not the owner of Shoe
    creator = getUserInfo(ptb.user_id)
    user = getUserInfo(p_log_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != p_log_session['user_id']:
        flash("You can't edit this Fridge Details"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('refrigarators', pscid=ptb.id))
    # POST methods
    if request.method == 'POST':
        fridgedetails.f_name = request.form['f_name']
        fridgedetails.f_color = request.form['f_color']
        fridgedetails. f_capacity = request.form['f_capacity']
        fridgedetails.f_doors = request.form['f_doors']
        fridgedetails.f_doorlock = request.form['f_doorlock']
        fridgedetails. f_price = request.form['f_price']
        fridgedetails. f_starrating = request.form['f_starrating']
        fridgedetails.f_date = datetime.datetime.now()
        session.add(fridgedetails)
        session.commit()
        flash("Fridge Details Edited Successfully")
        return redirect(url_for('refrigarators', pscid=pscid))
    else:
        return render_template('editFridgeDetails.html',
                               pscid=pscid, fridgedetails=fridgedetails,
                               pfridge_cat=pfridge_cat)


# Delte Fridge Details


@app.route('/refrigarators/<int:pscid>/<string:psmmname>/delete',
           methods=['GET', 'POST'])
def deleteFridgeDetails(pscid, psmmname):
    ptb = session.query(P_CompName).filter_by(id=pscid).one()
    fridgedetails = session.query(P_FridgeName).filter_by(
        f_name=psmmname).one()
    # See if the logged in user is not the owner of shoes
    creator = getUserInfo(ptb.user_id)
    user = getUserInfo(p_log_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != p_log_session['user_id']:
        flash("You can't delete this Fridge details"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('refrigarators', pscid=ptb.id))
    if request.method == "POST":
        session.delete(fridgedetails)
        session.commit()
        flash("Deleted Fridge Details Successfully")
        return redirect(url_for('refrigarators', pscid=pscid))
    else:
        return render_template('deleteFridgeDetails.html',
                               pscid=pscid, fridgedetails=fridgedetails,
                               pfridge_cat=pfridge_cat)


# Logout from current user


@app.route('/logout')
def logout():
    access_token = p_log_session['access_token']
    print ('In gdisconnect access token is %s', access_token)
    print ('User name is: ')
    print (p_log_session['username'])
    if access_token is None:
        print ('Access Token is None')
        p_res = make_response(
            json.dumps('Current user not connected....'), 401)
        p_res.headers['Content-Type'] = 'application/json'
        return response
    access_token = p_log_session['access_token']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    hp = httplib2.Http()
    result = \
        hp.request(uri=url, method='POST', body=None, headers={
            'content-type': 'application/x-www-form-urlencoded'})[0]

    print (result['status'])
    if result['status'] == '200':
        del p_log_session['access_token']
        del p_log_session['gplus_id']
        del p_log_session['username']
        del p_log_session['email']
        del p_log_session['picture']
        p_res = make_response(json.dumps(
            'Successfully disconnected user..'), 200)
        p_res.headers['Content-Type'] = 'application/json'
        flash("Successful logged out")
        return redirect(url_for('showLogin'))
        # return response
    else:
        p_res = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        p_res.headers['Content-Type'] = 'application/json'
        return p_res


# Json
####


@app.route('/refrigarators/JSON')
def allFridgesJSON():
    '''shows all fridge companies and thier fridge models'''
    fridgecategories = session.query(P_CompName).all()
    category_dict = [c.serialize for c in fridgecategories]
    for c in range(len(category_dict)):
        fridges = [i.serialize for i in session.query(
                 P_FridgeName).filter_by(
                     compnameid=category_dict[c]["id"]).all()]
        if fridges:
            category_dict[c]["fridge"] = fridges
    return jsonify(P_CompName=category_dict)


@app.route('/refrigarators/fridgeCompanies/JSON')
def categoriesJSON():
    '''shows all fridge companies'''
    fridges = session.query(P_CompName).all()
    return jsonify(fridgeCategories=[c.serialize for c in fridges])

####


@app.route('/refrigarators/fridges/JSON')
def itemsJSON():
    '''shows all fridges'''
    items = session.query(P_FridgeName).all()
    return jsonify(fridges=[i.serialize for i in items])

#####


@app.route('/refrigarators/<path:fridge_name>/fridges/JSON')
def categoryItemsJSON(fridge_name):
    '''shows specific company fridges'''
    fridgeCategory = session.query(
        P_CompName).filter_by(p_name=fridge_name).one()
    fridges = session.query(P_FridgeName).filter_by(
        compname=fridgeCategory).all()
    return jsonify(fridgeEdtion=[i.serialize for i in fridges])


@app.route('/refrigarators/<path:fridge_name>/<path:edition_name>/JSON')
def ItemJSON(fridge_name, edition_name):
    '''shows specific fridge of specific company'''
    fridgeCategory = session.query(
        P_CompName).filter_by(p_name=fridge_name).one()
    fridgeEdition = session.query(P_FridgeName).filter_by(
           f_name=edition_name, compname=fridgeCategory).one()
    return jsonify(fridgeEdition=[fridgeEdition.serialize])

if __name__ == '__main__':
    app.secret_key = "super_secret_key"
    app.debug = True
    app.run(host='127.0.0.1', port=8000)
