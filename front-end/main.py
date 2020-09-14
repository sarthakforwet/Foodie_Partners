import os
import json
import pickle
import requests
import numpy as np
import pandas as pd
import MySQLdb.cursors
from io import StringIO
from flask_mysqldb import MySQL
from surprise import KNNWithMeans
from surprise import Dataset, Reader, KNNBasic
from flask import Flask,render_template,request,redirect,session,flash,url_for

# Initializing the app
app = Flask(__name__)
app.secret_key=os.urandom(24)

#CONFIGRATIONS
config_file = open("../config.json", "r")
config = json.load(config_file)

#config db
db_config_file = open("../db_config.json")
db_cfg = json.load(db_config_file)
app.config['MYSQL_HOST'] = db_cfg["MYSQL_HOST"]
app.config['MYSQL_USER'] = db_cfg["MYSQL_USER"]
app.config['MYSQL_PASSWORD'] = db_cfg["MYSQL_PASSWORD"]
app.config['MYSQL_DB'] = db_cfg["MYSQL_DB"]
conn = MySQL(app)

# ===== ROUTES ======= #
@app.route('/')
def First_home():
    return render_template('/login.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def about():
    return render_template('register.html')

@app.route('/home')
def home():
    if 'ID' in session:
        return render_template('home.html')
    else:
        return redirect('/')

@app.route('/profile')
def profile():
    """Function to lookup profile"""
    # Check if user is logged in
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        ID = session['ID']
        cursor = conn.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * from user_detail where Id=%s", (ID,))
        pro1 = cursor.fetchone()

        # Show the profile page with account info
        return render_template('profile.html', pro1=pro1)

    # If user is not logged in, redirect to login page
    return redirect('/login')

@app.route('/profile_validation', methods=['GET', 'POST'])
def profile_validation():
    """Function to check and maintain profile"""
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' :
        # Create variables for easy access
        contact_no = request.form.get('contact_no')
        location=request.form.get('location')
        age=int(request.form.get('age'))
        ID=session['ID']

        cursor = conn.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * from user_detail where ID=%s", (ID,))
        pro1 = cursor.fetchone()

        # WIP
        cursor.execute(f"UPDATE user_detail SET contact_no={contact_no}, \
        age={age}, location={location} WHERE ID= {ID}")

        conn.connection.commit()
        flash('You have successfully updated your profile!')
        return render_template('profile.html',pro1=pro1)

    else:
        ID = session['ID']
        cursor = conn.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * from user_detail where ID=%s", (ID,))
        pro1 = cursor.fetchone()
        flash('Enter valid response')
        return render_template('profile.html',pro1=pro1)

@app.route('/about')
def about_home():
    """Redirect to About page"""
    # WIP
    return render_template('about.html')

@app.route('/login_validation', methods=['POST'])
def login_validation():
    """Function to check login credentials"""
    # Output message if something goes wrong...
    msg = 'Opps! Forgot your credentials?'

    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        # Create variables for easy access
        email = request.form['email']
        password = request.form['password']

        # Check if account exists using MySQL
        cursor = conn.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user_detail WHERE email = %s AND password = %s', (email, password,))

        # Fetch one record and return result
        account = cursor.fetchone()

        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['ID'] = account['Id']
            session['email'] = account['email']
            flash('Logged in Successfully!')
            return redirect('/profile') # redirect to profile page
        else:
            # Account does not exist or username/password incorrect
            # WIP
            flash(msg, "error")
            return render_template('login.html', msg=msg)

@app.route('/add_user', methods=['POST'])
def add_user():
    """Function to add new user."""
    name=request.form.get('username')
    email= request.form.get('email')
    password = request.form.get('password')

    cursor = conn.connection.cursor()
    cursor.execute("""INSERT INTO `user_detail` (`ID`, `name`,`email`,`password`) VALUES
        (NULL,'{}','{}','{}')""".format(name,email,password))
    conn.connection.commit()

    cursor.execute("""SELECT * FROM `user_detail` WHERE `email` LIKE '{}'""".format(email))
    myuser=cursor.fetchall()
    session['ID']=myuser[0][0]
    return redirect('/profile')

@app.route('/logout')
def logout():
    """Function to log out from app"""
    session.pop('ID')
    return redirect('/')

@app.route('/cs_validation', methods=['POST','GET'])
def cs_validation():
    """Function to validate cuisine from database."""
    Id = session['ID']
    cuisine = request.form.get('cuisine')
    rate = request.form.get('rate')

    cursor = conn.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM cs WHERE ID = %s and cuisine = %s', (Id,cuisine,))
    account1 = cursor.fetchone()

    if account1:
        flash("Cuisine already exists")
        return redirect(url_for('profile'))
    else:
        cursor.execute("""INSERT INTO `cs` ( `Id`,`cuisine`,`rate`) VALUES
                        ('{}','{}','{}')""".format(Id, cuisine, rate))
        conn.connection.commit()
        flash("Cuisine added")
        return redirect(url_for('profile'))
    return redirect('/profile')

@app.route('/display_cs')
def display_cs():
    """Function to display current cuisine information for
    the user currently logged in."""
    Id = session['ID']
    cur = conn.connection.cursor()
    resultValue= cur.execute("SELECT * from cs where ID=%s",(Id,))
    cuisineDetails= cur.fetchall()
    if resultValue > 0 :
        return render_template('cuisineset.html', skillDetails=cuisineDetails )
    else:
        flash("Add Cusine")
        return redirect(url_for('profile'))

@app.route('/find_match', methods=['POST', 'GET'])
def find_match():
    """Function to find a match."""
    Id = session['ID']
    cur = conn.connection.cursor()
    resultValue= cur.execute("SELECT * from cs where ID=%s",(Id,))
    cuisineDetails = cur.fetchall()
    if resultValue > 0 :
        return render_template('findmatch.html', skillDetails=cuisineDetails )
    else:
        flash("Add Cusine")
        return redirect(url_for('profile'))

@app.route('/update_tech_validation',methods=['GET','POST'])
def update_tech_validation():
    """Function to update ratings for particular
    cuisines corresponding to the particular logged in user."""
    Id = session['ID']

    # Getting cuisine and rating (updated) info
    u_skill= request.form.get('u_skill')
    u_rate = request.form.get('u_rate')

    # Update in database.
    cursor = conn.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('UPDATE cs set rate=%s WHERE ID = %s and cuisine = %s', (u_rate,Id, u_skill,))
    conn.connection.commit()
    cursor.execute(f"select name from user_detail where ID={Id}")
    user_name = cursor.fetchone()

    # Update the pickle file
    user = {}
    user["u_id"] = [user_name["name"]]
    user["cusine"] = u_skill
    user["rating"] = u_rate
    tmp = load_data()
    tmp = tmp.append(pd.DataFrame(user))
    tmp = tmp.reset_index()
    tmp = tmp.drop("index", axis=1)
    dump_data(tmp)

    flash("Cuisine Updated")
    return redirect(url_for('display_cs'))

# Find Restraunts
@app.route('/res',methods=['POST','GET'])
def res():
    """Function to find nearby restaurants."""
    if request.method=='POST':
        address = request.form['address']
        count=request.form['Count']
        headers={'Accept': "application/json","user-key": "6f1a6514744476d55591d9dd25198c4c"}
        headers2 = {'Authorization': 'prj_live_pk_feddf0d04ae764d8157faf0d35e0926e711d8c8d',}
        params2 = (('query', address),)
        response2 = requests.get('https://api.radar.io/v1/geocode/forward', headers=headers2, params=params2)
        data2 = response2.json()
        Lat = data2['addresses'][0]['latitude']
        Long = data2['addresses'][0]['longitude']
        params={'lat':Lat,'lon':Long,'count':count}
        r=requests.get('https://developers.zomato.com/api/v2.1/search',headers=headers,params=params)

        data=r.json()
        data=data['restaurants']

        result=[]
        name = []
        address = []
        rating = []
        images = ['static/food1.jpg','static/food2.jpg','static/food3.jpg','static/food4.jpg',
                'static/food5.jpg','static/food6.jpg', 'static/food7.jpg','static/food8.jpg',
                'static/food9.jpg','static/food10.jpg','static/food11.jpg','static/food12.jpg',
                'static/food13.jpg','static/food14.jpg','static/food15.jpg']

        for i in data:
            name.append((i['restaurant']['name']))
            address.append((i['restaurant']['location']['address']))
            rating.append((i['restaurant']['user_rating']['aggregate_rating']))

            result.append((i['restaurant']['name'],i['restaurant']['location']['address'],
            i['restaurant']['average_cost_for_two'],i['restaurant']['user_rating']['aggregate_rating']))
        return render_template('cards.html',address=address,name=name,rating=rating,count=int(count),image_url=images)

    return render_template('restaurants.html',title='Find restaurants')

@app.route('/predict', methods=['POST', 'GET'])
def predict():
    """Function predicting the matches for the
    user taking dynamic ratings from him/her."""

    # Template render and get info
    ID = session['ID']
    cur = conn.connection.cursor()
    r1 = cur.execute('SELECT cuisine, rate FROM cs WHERE ID = %s ', (ID,))
    s1 = cur.fetchall()

    cusines = {}
    if request.method == "POST":
        # Getting updated (temporary) ratings information.
        d = request.form
        d = d.to_dict(flat=False)
        for cus, rate in zip(d["u_skill"], d["u_rate"]):
            cusines[cus] = float(rate)

    # Extracting info from database to predict from.
    # WIP for age, location and gender personalization.
    r2= cur.execute('SELECT name, age, location FROM user_detail WHERE ID = %s ', (ID,))
    res = cur.fetchone()
    user_name = res[0]
    age = res[1]
    location = res[2]

    # Loading the saved model from pickle file.
    model_file = open("../pickle_files/similarity_model.pkl", "rb")
    model = pickle.load(model_file)

    def get_recommendations(user_name=None, cuisines=None, age=None, location=None, gender=None):
        """Function for getting recommendations by retraining the model on new cuisines
        for a particular user and re-filter the results for the introduced constraints
        Args:
        user_name: str
        Name of the user for whom recommendations are to be found out.

        cuisines: dict
        A mapping of cuisine type to new value

        age: int
        Age range to select from

        location: str
        Location in which to go for.

        gender: str
        Gender preference
        """

        assert len(cuisines) == len(config["CUSINES"]), \
        "Cuisines must be %d"%(len(config["CUSINES"]))

        # Loading DataFrame object from pickle
        data_file = open("../pickle_files/user_data.pkl", "rb")
        data = pickle.load(data_file)

        # Updating the rows for the current user.
        data.loc[data["u_id"] == user_name, "rating"] = list(map(float, cuisines.values()))

        # Preparing surprise compatible dataset object.
        reader = Reader(rating_scale=config["RATING_SCALE"])
        dataset = Dataset.load_from_df(data[["u_id", "cusine", "rating"]], reader)
        trainset = dataset.build_full_trainset()

        # Re-training the model on updated dataset.
        model.fit(trainset)

        # Getting the predictions with temporarily updated dataset
        uid = trainset.to_inner_uid(user_name)
        pred = model.get_neighbors(iid=uid, k=config["NUM_RECOMMENDATIONS"])

        # When using age, location and gender constraints, we need to take into
        # account all/more recommendations
        if len(pred) == 0:
            flash("Oops! no results for these filter settings!")
        else:
            # Getting information of the predicted users.
            # WIP
            outs = []
            ages = []
            locations = []
            contacts = []
            for i in pred:
                uname = trainset.to_raw_uid(i)
                data = cur.execute('select age, location, contact_no from user_detail where name= %s ',(uname,))
                r = cur.fetchone()
                ages.append(r[0])
                locations.append(r[1])
                contacts.append(r[2])
                outs.append(trainset.to_raw_uid(i))

        return outs, locations, contacts, ages
    outs, locations, contacts, ages = get_recommendations(user_name, cusines, age, location)
    return render_template("match_info.html", outs=outs, l=len(outs), loc=locations, cont=contacts, age=ages)


def load_data():
    """Function to load data from pickle file"""
    data_file = open("../pickle_files/user_data.pkl", "rb")
    df = pickle.load(data_file)
    return df

def dump_data(df):
    """Function to dump data to pickle file"""
    data_file = open("../pickle_files/user_data.pkl", "wb")
    pickle.dump(df, data_file)

if __name__ == "__main__":
    app.run(debug=True)
