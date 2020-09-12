from flask import Flask,render_template,request,redirect,session,flash,url_for
import mysql.connector
from flask_mysqldb import MySQL
import MySQLdb.cursors
from surprise import Dataset, Reader, KNNBasic
import pickle
from surprise import KNNWithMeans
import numpy as np
import pandas as pd

import os
import json
app = Flask(__name__)
app.secret_key=os.urandom(24)

#config db
#db = yaml.load(open('db.yaml'))
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'pr'
conn = MySQL(app)
#conn=mysql.connector.connect(host="localhost",user="root",password="MySQL@2000",database="registration_sih")
#cursor = conn.cursor()


@app.route('/')
def First_home():
    return render_template('/login.html')

@app.route('/index')
def index():
    return render_template('E:/Job-Prediction/front-end/templates/index.html')

@app.route('/login')
def login():
    return render_template('E:/Job-Prediction/front-end/templates/login.html')

@app.route('/register')
def about():
    return render_template('E:/Job-Prediction/front-end/templates/register.html')

@app.route('/home')
def home():
    if 'ID' in session:
        return render_template('home.html')
    else:
        return redirect('/')




@app.route('/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        '''cursor = conn.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user_detail WHERE id = %s', (session['ID'],))
        account = cursor.fetchone()'''
        ID = session['ID']
        cursor = conn.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * from user_detail where Id=%s", (ID,))
        pro1 = cursor.fetchone()

        # Show the profile page with account info
        return render_template('profile.html', pro1=pro1)
    # User is not loggedin redirect to login page
    return redirect('/login')
@app.route('/profile_validation', methods=['GET', 'POST'])
def profile_validation():
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' :
        # Create variables for easy access
        contact_no = request.form.get('contact_no')
        location=request.form.get('location')
        age=request.form.get('age')

        ID=session['ID']

        cursor = conn.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * from user_detail where ID=%s", (ID,))
        pro1 = cursor.fetchone()

        cursor.execute('UPDATE user_detail set contact_no= %s, age= %d, location=%s   WHERE ID= %s',( contact_no , age,location,ID,));
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
    return render_template('about.html')


@app.route('/login_validation', methods=['POST'])
def login_validation():
    # Output message if something goes wrong...
    msg = ''
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
            # Redirect to home page
            return redirect('/profile')
        else:
            # Account doesnt exist or username/password incorrect
            flash('Incorrect username/password!')
            return render_template('login.html', msg=msg)
    # Show the login form with message (if any)


@app.route('/add_user', methods=['POST'])
def add_user():
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
    return redirect('/home')

@app.route('/logout')
def logout():
    session.pop('ID')
    return redirect('/')

@app.route('/cs_validation', methods=['POST','GET'])
def skill_validation():
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
#Display Cuisines
@app.route('/display_cs')
def display_cs():
        Id = session['ID']
        cur = conn.connection.cursor()
        resultValue= cur.execute("SELECT * from cs where ID=%s",(Id,))

        cuisineDetails= cur.fetchall()

        if resultValue > 0 :
            return render_template('cuisineset.html', skillDetails=cuisineDetails )
        else:
            flash("Add Cusine")
            return redirect(url_for('profile'))

# Restaurat
@app.route('/res',methods=['POST','GET'])
def res():
    result = []
    if request.method=='POST':
        User_key=request.form['Api']
        Lat=request.form['Lat']
        Long=request.form['Long']
        Cuisines=request.form['Cuisines']
        Sort_By=request.form['SortBy']
        Sort_Order=request.form['SortOrder']
        count=request.form['Count']
        q=request.form['Query']
        headers={'Accept': "application/json","user-key": str(User_key)}
        params={'lat':Lat,'lon':Long,'cuisines':Cuisines,'sort':Sort_By,'order':Sort_Order,'count':count,'q':q}
        r=requests.get('https://developers.zomato.com/api/v2.1/search',headers=headers,params=params)
        data=r.json()
        data=data['restaurants']

        for i in data:
            result.append((i['restaurant']['name'],i['restaurant']['location']['address'],i['restaurant']['average_cost_for_two'],i['restaurant']['user_rating']['aggregate_rating']))
        return render_template('response.html',data=result,length=len(result))
    return render_template('response.html', data=result, length=len(result))


    #return render_template('home.html', title='Find restaurants')


@app.route('/predict', methods=['POST', 'GET'])
def predict():
    ID = session['ID']
    cur = conn.connection.cursor()



    r1 = cur.execute('SELECT cuisine,rate FROM cs WHERE ID = %s ', (ID,))
    s1 = cur.fetchall()
    r2= cur.execute('SELECT name FROM user_detail WHERE ID = %s ', (ID,))
    user_name=cur.fetch()
    # Testing if the model is perfectly
    new_model_file = open("similarity_model.pkl", "rb")
    new_algo = pickle.load(new_model_file)

    def get_recommendations(user_name=None, cuisines=None, age=None, location=None, gender=None, num_recommendations=5):
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
        # data.loc["u_id"==user_name,"cusine"==k]
        # assert rows.shape[0]!=0, "User does not exist in dataset"
        #assert len(cuisines) == NUM_CUISINES, "Cuisines must be {NUM_CUISINES}"
        data.loc[df["u_id"] == user_name, "rating"] = list(map(float, cuisines.values()))

        # print(rows)
        # data[data["u_id"]==user_name] = rows
        # print(data[data["u_id"]==user_name])
        reader = Reader(rating_scale=RATING_SCALE)
        dataset = Dataset.load_from_df(data[["u_id", "cusine", "rating"]], reader)
        trainset = dataset.build_full_trainset()

        print("=" * 25)
        print("Getting Recommendations ready")
        print("=" * 25)


        new_algo.fit(trainset)

        # Now getting the predictions with temporarily updated dataset

        uid = trainset.to_inner_uid(user_name)
        pred = new_algo.get_neighbors(iid=uid, k=num_recommendations)
        # When using age, location and gender constraints, we need to take into
        # account all/more recommendations
        if len(pred) == 0:
            print("Oops! no results for these filter settings!")
        else:
            print("=" * 15)
            print("Top recommendations")
            print("=" * 15)

            for i in pred:
                print(trainset.to_raw_uid(i))






if __name__ == "__main__":
    app.run(debug=True)

##
 #create table user_detail(Id int not Null uique au' at line 1
#mysql>  create table user_detail(Id int not Null unique auto_increment, email varchar(255),name varchar(255) not null,password varchar(255) not null,contact_no int (11),age int(3),constraint check_contact_id check(contact_no like'[1-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]'),constraint check_mail check(email like '%@%.%'),primary key(email));