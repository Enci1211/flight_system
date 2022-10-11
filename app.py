# Name:  Enci Lyu
# Student ID: 1153399
####################################################

import mysql.connector
from mysql.connector import FieldType
import datetime
import connect_airline
import uuid
from flask import Flask,render_template,request,redirect

app = Flask(__name__)

def getCursor():
    global dbconn
    global connection
    connection = mysql.connector.connect(user=connect_airline.dbuser, \
    password=connect_airline.dbpass, host=connect_airline.dbhost, \
    database=connect_airline.dbname, autocommit=True)
    dbconn = connection.cursor()
    return dbconn

def genID():
    return uuid.uuid4().fields[1]
        
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/screen")
def screen():
    if request.method == 'POST':
        userSelect = request.form['select']
        cur = getCursor()
        dbsql = """SELECT r.flightnum, r.depcode, a.airportname as depairport, r.arrcode, aa.airportname as arrairport
                    from route as r
                    join airport as a
                    on r.depcode = a.airportcode
                    join airport as aa
                    on r.arrcode = aa.airportcode
                    where a.airportname = %s or aa.airportname = %s;"""
        parameters = (userSelect, userSelect)
        cur.execute(dbsql,parameters)
        dbOutput = cur.fetchall()
        return render_template("screenAD.html",userSelect = dbOutput)
        
    return render_template("screen.html")
   

