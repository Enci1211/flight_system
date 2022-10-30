# Name:  Enci Lyu
# Student ID: 1153399
####################################################



import mysql.connector
from mysql.connector import FieldType
import datetime
from datetime import timedelta
import connect_airline
import uuid
from flask import Flask,render_template,request,redirect
from flask import url_for

#from symbol import parameters

#from symbol import parameters

app = Flask(__name__)

current_time = datetime.datetime(2022,10,28,17,0,0)
current_date = datetime.date(2022,10,28)

current_hms = datetime.time(17,0,0)

print(current_hms)

passengerid = """select passengerid from passenger;"""
passengerid_list = [item for t in passengerid for item in t]

isManager = """SELECT staffid FROM staff where IsManager = "1";"""


def getCursor():
    global dbconn
    global connection
    connection = mysql.connector.connect(user=connect_airline.dbuser, \
    password=connect_airline.dbpass, host=connect_airline.dbhost, \
    database=connect_airline.dbname, autocommit=True)
    dbconn = connection.cursor()
    return dbconn
def columnOutput(dbData,cols,formatStr):
    print(formatStr.format(*cols))
    for row in dbData:
        rowList=list(row)
        for index,item in enumerate(rowList):
            if item==None:      
                rowList[index]=""       
            elif type(item)==datetime.date or type(item)==datetime.datetime or type(item)==datetime.time or type(item)==datetime.timedelta:    
                rowList[index]=str(item)
        print(formatStr.format(*rowList))  

def genID():
    return uuid.uuid4().fields[1]
        
@app.route("/")
def home():
    return render_template("home.html")


@app.route("/screen/" , methods = ['POST','GET'])#select an airport, display info dep/arr at this airport
def screen():
    date_before = current_date - timedelta(days=2) #create a date 2days before "current day"
    date_after = current_date + timedelta(days=5)  #create a date 5days after "current day"
    
    if request.method == 'POST':
        userSelect = request.form['select']
                          
        cur = getCursor() #Shows appropriate arrivals and departures information for a selected airport
        dbsql = ("""SELECT r.flightnum, f.flightdate, r.depcode, a.airportname as depairport, f.deptime, r.arrcode, aa.airportname as arrairport,f.ArrTime
                   from route as r
                   join airport as a
                   on r.depcode = a.airportcode
                   join airport as aa
                   on r.arrcode = aa.airportcode
                   join flight as f
                   on f.flightnum = r.flightnum
                   where (f.flightdate >= %s and f.flightdate <= %s AND
                         a.airportcode = %s) or 
                         (f.flightdate >= %s and f.flightdate <= %s AND 
                         aa.airportcode = %s)
                   order by f.flightdate;""")
        parameters = (date_before,date_after,userSelect, date_before,date_after,userSelect)
        cur.execute(dbsql,parameters) 
        dbOutput = cur.fetchall()
        return render_template("screen.html",userSelect = dbOutput)
        
    return render_template("screen.html")

@app.route("/login/", methods = ['POST','GET'])#enter id to login,if successfull, display all the booking under this user(email)
def login():
    cur = getCursor()
    cur.execute("""SELECT emailaddress FROM passenger;""")#get all the id from database
    dbOutput = cur.fetchall()
    emailList = [item for t in dbOutput for item in t]
    
    if request.method == 'POST':
        userEmail = request.form['email'] #user fill in the form with the email
        cur = getCursor()
        sql = ("""select passengerid from passenger
                  where emailaddress = %s;""")
        parameter = (userEmail,)
        cur.execute(sql,parameter)
        dbOutput = cur.fetchall()
        passengerID = dbOutput[0][0]
        print(passengerID)

        if userEmail in emailList:    
            print(userEmail)
            cur = getCursor()  #fetch the user details
            dbsql = ("""select passengerid, firstname, lastname, emailaddress
                        from passenger
                        where emailaddress = %s""")
            parameter = (userEmail,) 
            cur.execute(dbsql,parameter)
            dbOutput = cur.fetchall()  
                 
            cur2 = getCursor()#fetch the details of all the bookings this user(with this email above) had made            
            dbsql2=("""SELECT p.passengerid, f.flightid, f.flightnum, f.flightdate,f.deptime,a.airportname as depairport
                            from passenger as p
                            join passengerflight as pf
                            on pf.PassengerID = p.PassengerID
                            join flight as f
                            on f.Flightid = pf.flightid 
                            join route as r
                            on f.flightnum = r.flightnum
                            join airport as a
                            on r.depcode = a.airportcode
                            where p.emailaddress = %s
                            order by f.flightdate;""")
            parameter2 = (userEmail,)
            cur2.execute(dbsql2,parameter2)
            
            dbOutput2 = cur2.fetchall()
            
            cur3 = getCursor()  #fetch the passengerID
            dbsql3 = ("""select passengerid from passenger
                         where EmailAddress = %s;""")
            parameter3 = (userEmail,)
            cur3.execute(dbsql3,parameter3)
            dbOutput3 = cur3.fetchall()
            passengerID = dbOutput3[0][0]  
            
              
            return render_template("login.html", userInfo=dbOutput, userSelect=dbOutput2, passengerID=passengerID,userEmail=userEmail,emailList=emailList)  
        else:
           return render_template("login.html", failure = "please try agian or click register button if you are new, thank you!")
    

    return render_template("login.html")


@app.route("/cancel/")#cancel the booking
def cancel():
    flightID = request.args.get("flightID")
    passengerID = request.args.get("passengerID")

    print(flightID)
    print(passengerID)
    
    cur = getCursor()
    sql = ("""DELETE FROM passengerflight
              where flightID = %s and passengerid = %s;""")
    parameters=(flightID, passengerID)
    cur.execute(sql,parameters)
    connection.commit()

    print(cur.statement)
    
    return render_template('login.html',cancel= "this booking had been canceled, please login again to check!")

    
@app.route("/login/edit/",methods = ['POST','GET'])
def edit():
    
     #passengerID 这里还可以顺利抓取，但是在下面if POST 以后print（passengerID)就是none了？？？？？？？？？？
    
    if request.method == 'POST':
        userDetails = request.form
        print(userDetails)
        
        
        passengerID = userDetails['passengerID']
        print(passengerID)

        firstName = userDetails['firstname']
        lastName = userDetails['lastname']
        emailAddress = userDetails['email']
        phoneNum = userDetails['phonenum']
        passportNum = userDetails['passportnum']
        dateBirth = userDetails['datebirth']
    
        
        cur = getCursor()   #update the new details into the db 没有成功！！！！测试了并不是datetime的格式问题，是上面没有抓到Passengeid的问题！！！！
        dbsql = """update passenger
                   set firstname=%s,lastname=%s,emailaddress=%s,phonenumber=%s,passportnumber=%s,dateofbirth=%s
                   where passengerid = %s;"""
        parameters = (firstName,lastName,emailAddress,phoneNum,passportNum,dateBirth,passengerID)
        cur.execute(dbsql,parameters) 
        connection.commit()
        
        return redirect(url_for('login'))
    
    
    else: 
        passengerID = request.args.get("passengerID")
        print(passengerID)
        cur = getCursor() #fetch the details for this specific passenger
        dbsql = ("""select firstname, lastname, emailaddress, phonenumber, passportnumber, dateofbirth,passengerid 
                from passenger
                where passengerid = %s""")
        parameter = (passengerID,)
        cur.execute(dbsql,parameter)
        dbOutput = cur.fetchall()
        print(dbOutput)
    
        firstname = dbOutput[0][0]  #pass these value to frontend to remind user the current value
        lastname = dbOutput[0][1]
        emailaddress = dbOutput[0][2]
        phonenumber = dbOutput[0][3]
        passportnumber = dbOutput[0][4]
        dateofbirth = dbOutput[0][5]
        passengerID = dbOutput[0][6]
    
    
        return render_template("edit.html", firstname = firstname, lastname = lastname, 
                           emailaddress=emailaddress, phonenumber=phonenumber,passportnumber=passportnumber,
                           dateofbirth= dateofbirth,passengerID=passengerID)
                
@app.route("/add/",methods = ['POST','GET'])# 想加入current_hsm 不知道语法对不对？？？？？？？？
def add():
    
    if request.method == 'POST':
        date_7after = current_date + timedelta(days=7) 
        userSelect = request.form['select']
        passengerID = request.form['passengerID']
        print(userSelect)  
        print(passengerID) 

        cur = getCursor()   #User selects departure airport. All flights from that airport are displayed for the selected date and 7 days after that date
        dbsql = """SELECT DISTINCT f.FlightID, r.FlightNum, f.FlightDate, a.Airportname AS DepartAirport, 
                   f.deptime, a.AirportName AS ArrivalAirpot, f.ArrTime, ac.Seating - COUNT(pf.PassengerID) AS seatAvailable, f.FlightStatus, s.statusdesc
                   FROM flight AS f
                   JOIN route AS r
                   ON f.FlightNum = r.FlightNum
                   JOIN airport AS a
                   ON r.DepCode = a.AirportCode                   
                   JOIN aircraft AS ac
                   ON f.Aircraft = ac.RegMark
                   JOIN passengerFlight AS pf
                   ON f.FlightID = pf.FlightID                  
                   join STATUS AS S
                   on f.FlightStatus = s.FlightStatus
                   where r.DepCode = %s and f.flightdate >= %s and flightdate <= %s
                   GROUP BY f.FlightID, r.FlightNum, f.FlightDate, r.DepCode, f.Deptime, a.AirportName, f.ArrTime                                   
                   order by f.flightdate;"""
        parameters = (userSelect, current_date,date_7after)# 想加入current_hsm 不知道语法对不对？？？？？？？？
        cur.execute(dbsql,parameters) 
        dbOutput = cur.fetchall()

        return render_template("add.html",userSelect = dbOutput,passengerID = passengerID) 
    else:
        passengerID = request.args.get("passengerID")
        print(passengerID)

        return render_template("add.html",passengerID=passengerID)  

@app.route("/add/success/") 
def addSuccess():
    passengerID = request.args.get("passengerID") 
    flightID = request.args.get("flightID") 

    cur = getCursor()
    dbsql = ("""select * from passengerflight
                where flightid = %s and passengerid = %s;""")
    parameters=(flightID,passengerID)
    cur.execute(dbsql,parameters)
    dbOutput = cur.fetchall()
    print(dbOutput)

    if len(dbOutput) == 0:

       cur = getCursor()
       dbsql = """INSERT INTO passengerflight(flightid,passengerid)
                   VALUES(%s,%s);"""
       parameters = (flightID,passengerID)
       cur.execute(dbsql,parameters)

       return render_template("login.html",success = "the passenger had booked this flight successfully,please login again to check!")
    return render_template('login.html',success = "the passenger had booked this flight successfully,please login again to check!")
      
@app.route("/register/" ,methods = ['POST','GET'])
def register():
    if request.method == 'POST':
        userDetails = request.form
        print(userDetails)
        
        firstName = userDetails['firstname']
        lastName = userDetails['lastname']
        emailAddress = userDetails['email']
        phoneNum = userDetails['phonenum']
        passportNum = userDetails['passportnum']
        dateBirth = userDetails['datebirth']
        
        cur = getCursor()
        dbsql = """INSERT INTO passenger(FirstName,LastName,EmailAddress,PhoneNumber,PassportNumber,DateOfBirth,LoyaltyTier)
                   VALUES(%s,%s,%s,%s,%s,%s,'1');"""
        parameters = (firstName,lastName,emailAddress,phoneNum,passportNum,dateBirth)
        cur.execute(dbsql,parameters) 
        
        return render_template("login.html",register="new passenger had been registered!")
    return render_template("register.html")
        
 
 
    
#Administrative system for staff

def CheckManager(staffID):
    # SQL with staff ID returning IsManager
    cur = getCursor()
    sql = ("""SELECT ismanager from staff
                   WHERE staffid = %s;""")
    parameter = (staffID,)
    cur.execute(sql,parameter)
    dbOutput = cur.fetchall()
    isManagerNum = dbOutput[0][0]
    if isManagerNum == 1:
        return True
    else:
        return False
    

@app.route("/admin/", methods = ['POST','GET']) 
def admin():   
    if request.method == 'POST':
        
       staffID = request.form.get("staff")
       
       return render_template("adminLogin.html",staffID=staffID)
    return render_template("admin.html")

@app.route("/admin/passenger/", methods = ['POST','GET']) #staff can get all passenger info in a table in this page
def adminPassenger():
    if request.method == 'POST':
       staffID = request.args.get("staffID")
       lastname = request.form.get("search") #fetch the value the staff entered
       print(lastname)

       cur = getCursor()
       cur.execute("""SELECT lastname FROM passenger;""")#get all the lastname from database
       dbOutput = cur.fetchall()
       lastname_list = [item for t in dbOutput for item in t]

       if lastname in lastname_list:

           cur = getCursor()
           sql = ("""select * from passenger where lastname = %s;""") #display the passenger details with the lastname staff entered
           parameter = (lastname,)
           cur.execute(sql,parameter)
           dbOutput = cur.fetchall()
           return render_template("adminPassenger.html", userSelect = dbOutput,staffID = staffID)
       else:
            staffID = request.args.get("staffID") #if staff entered a wrong/invalid value, just display all the passeger details
            cur = getCursor()
            cur.execute("""SELECT * FROM passenger
                     order by lastname, firstname;""")        
            dbOutput = cur.fetchall()
            return render_template("adminPassenger.html", userSelect = dbOutput,staffID = staffID)

    else: 
       staffID = request.args.get("staffID") 
       cur = getCursor()  #display all the passeger details
       cur.execute("""SELECT * FROM passenger 
                     order by lastname, firstname;""")        
       dbOutput = cur.fetchall()
       return render_template("adminPassenger.html", userSelect = dbOutput,staffID = staffID)


@app.route("/admin/passenger/register/", methods = ['POST','GET']) 
def adminRegister():
    staffID = request.args.get("staffID")
    if request.method == 'POST':
        userDetails = request.form
        print(userDetails)
        
        firstName = userDetails['firstname']
        lastName = userDetails['lastname']
        emailAddress = userDetails['email']
        phoneNum = userDetails['phonenum']
        passportNum = userDetails['passportnum']
        dateBirth = userDetails['datebirth']
        
        cur = getCursor()
        dbsql = """INSERT INTO passenger(FirstName,LastName,EmailAddress,PhoneNumber,PassportNumber,DateOfBirth,LoyaltyTier)
                   VALUES(%s,%s,%s,%s,%s,%s,'1');"""
        parameters = (firstName,lastName,emailAddress,phoneNum,passportNum,dateBirth)
        cur.execute(dbsql,parameters) 
        
        return render_template("adminLogin.html",success= "already added new passenger!")
    return render_template("adminRegister.html")  


@app.route("/admin/passenger/details/",methods = ['POST','GET']) 
def adminDetails():             ##staff can get a specific passenger info in this page as well as his(her) booking table
    passengerID = request.args.get("passengerID")# get the passengerID=value in url
    staffID = request.args.get("staffID")
    cur = getCursor()
    dbsql = ("""SELECT * FROM passenger
                    where passengerid = %s;""")    #fetch the specific passenger info
    parameter = (passengerID,)
    cur.execute(dbsql,parameter)
    dbOutput = cur.fetchall()
    
    cur2 = getCursor()
    dbsql2 = ("""SELECT p.passengerid, p.firstname, p.lastname, f.flightid, f.flightnum, f.flightdate
                 FROM flight as f
                 join passengerflight as pf
                 on f.flightid = pf.flightid
                 join passenger as p
                 on pf.PassengerID = p.passengerid
                 where p.passengerid = %s;""") #fetch all the booking under the specific passenger
    parameter2 = (passengerID,)
    cur2.execute(dbsql2,parameter2)
    dbOutput2 = cur2.fetchall()
    
    return render_template("adminDetails.html", passenger = dbOutput, passengerBooking = dbOutput2, staffID = staffID,passengerID= passengerID)
                          
@app.route("/admin/passenger/add/",methods = ['POST','GET'])# 想加入current_hsm 不知道语法对不对？？？？？？？
def adminAdd():
    
    if request.method == 'POST':
        date_7after = current_date + timedelta(days=7) 
        userSelect = request.form['select']
        passengerID = request.form['passengerID']
        print(userSelect)   
        print(passengerID)
        cur = getCursor()   #User selects departure airport. All flights from that airport are displayed for the selected date and 7 days after that date
        dbsql = """SELECT DISTINCT f.FlightID, r.FlightNum, f.FlightDate, a.Airportname AS DepartAirport, 
                   f.deptime, aa.AirportName AS ArrivalAirpot, f.ArrTime, ac.Seating - COUNT(p.PassengerID) AS seatAvailable, f.FlightStatus, s.statusdesc
                   FROM flight AS f
                   LEFT JOIN route AS r
                   ON f.FlightNum = r.FlightNum
                   LEFT JOIN airport AS a
                   ON r.DepCode = a.AirportCode
                   LEFT JOIN airport AS aa
                   ON r.DepCode = aa.AirportCode
                   LEFT JOIN aircraft AS ac
                   ON f.Aircraft = ac.RegMark
                   LEFT JOIN passengerFlight AS pf
                   ON f.FlightID = pf.FlightID
                   LEFT JOIN passenger AS p
                   ON pf.PassengerID = p.PassengerID
                   left join STATUS AS S
                   on f.FlightStatus = s.FlightStatus
                   where a.airportcode = %s and f.flightdate >= %s and flightdate <= %s
                   GROUP BY f.FlightID, r.FlightNum, f.FlightDate, a.AirportCode, f.DepEstAct, aa.AirportName, f.ArrTime, ac.Seating;                                    
                   order by f.flightdate;"""
        parameters = (userSelect, current_date,date_7after)
        cur.execute(dbsql,parameters) 
        dbOutput = cur.fetchall()
        return render_template("adminAdd.html",userSelect = dbOutput,passengerID = passengerID) 
    else:
        passengerID = request.args.get("passengerID")
        return render_template("adminAdd.html",passengerID=passengerID)  

@app.route("/admin/passenger/add/success/") 
def adminAddSuc():
    passengerID = request.args.get("passengerID") 
    flightID = request.args.get("flightID") 

    cur = getCursor()
    dbsql = ("""select * from passengerflight
                where flightid = %s and passengerid = %s;""")
    parameters=(flightID,passengerID)
    cur.execute(dbsql,parameters)
    dbOutput = cur.fetchall()
    print(dbOutput)

    if len(dbOutput) == 0:

       cur = getCursor()
       dbsql = """INSERT INTO passengerflight(flightid,passengerid)
                   VALUES(%s,%s);"""
       parameters = (flightID,passengerID)
       cur.execute(dbsql,parameters)

       return render_template("admin.html",success = "new booking have been added to the passenger!") 
    return render_template("admin.html",success = "the booking is exist!") 

@app.route("/admin/passenger/edit/",methods = ['POST','GET'])
def adminEdit():
    
    if request.method == 'POST':
        userDetails = request.form    #fetch the new details of this passenger
        print(userDetails)
        
        firstName = userDetails['firstname']
        lastName = userDetails['lastname']
        emailAddress = userDetails['email']
        phoneNum = userDetails['phonenum']
        passportNum = userDetails['passportnum']
        dateBirth = userDetails['datebirth']
        passengerID = userDetails['passengerID']
        
        cur = getCursor()   #update the new details into the db为什么没成功？？datebirth要从str变成date？？？？？？？？？
        dbsql = """update passenger
                   set firstname=%s,lastname=%s,emailaddress=%s,phonenumber=%s,passportnumber=%s,dateofbirth=%s
                   where passengerid = %s;"""
        parameters = (firstName,lastName,emailAddress,phoneNum,passportNum,dateBirth,passengerID)
        cur.execute(dbsql,parameters) 
        connection.commit()
        return redirect(url_for('admin'))
    
    
    else: 
        passengerID = request.args.get("passengerID")
        staffID = request.args.get("staffID")
        cur = getCursor() #fetch the details for this specific passenger
        dbsql = ("""select firstname, lastname, emailaddress, phonenumber, passportnumber, dateofbirth, passengerid
                from passenger
                where passengerid = %s""")
        parameter = (passengerID,)
        cur.execute(dbsql,parameter)
        dbOutput = cur.fetchall()
        print(dbOutput)
    
        firstname = dbOutput[0][0]  #pass these value to frontend to remind user the current value
        lastname = dbOutput[0][1]
        emailaddress = dbOutput[0][2]
        phonenumber = dbOutput[0][3]
        passportnumber = dbOutput[0][4]
        dateofbirth = dbOutput[0][5]
        passengerID = dbOutput[0][6]
    
    
        return render_template("adminEdit.html", firstname = firstname, lastname = lastname, 
                           emailaddress=emailaddress, phonenumber=phonenumber,passportnumber=passportnumber,
                           dateofbirth= dateofbirth,passengerID=passengerID)
                
                     
@app.route("/admin/passenger/cancel/")
def adminCancel():
    flightID = request.args.get("flightID")
    passengerID = request.args.get("passengerID")

    print(passengerID)
    print(flightID)
    
    cur = getCursor() #delete the booking 
    sql = ("""DELETE FROM passengerflight
              where flightid = %s and passengerid = %s;""")
    paremeters =(flightID,passengerID)
    cur.execute(sql,paremeters)
    connection.commit()

    print(cur.statement)
    
    return render_template("admin.html",cancel = "the booking have been canceled")

   
    
@app.route("/admin/flight/", methods = ['POST','GET']) #staff can get all the flights info in a talbe in this page,only manager can add flights in this page
def adminFlight():  
    staffID = request.args.get("staffID")
    isManager = CheckManager(staffID)
    print(isManager)

    date_7after = current_date + timedelta(days=7) 

    cur = getCursor()
    sql = ("""SELECT DISTINCT f.FlightID, r.FlightNum, f.FlightDate, a.Airportname AS DepartAirport, 
                   f.deptime, aa.AirportName AS ArrivalAirpot, f.ArrTime,f.Aircraft, COUNT(p.PassengerID) as seatBooked, ac.Seating - COUNT(p.PassengerID) AS seatAvailable, f.FlightStatus
                   FROM flight AS f
                   LEFT JOIN route AS r
                   ON f.FlightNum = r.FlightNum
                   LEFT JOIN airport AS a
                   ON r.DepCode = a.AirportCode
                   LEFT JOIN airport AS aa
                    ON r.DepCode = aa.AirportCode
                   LEFT JOIN aircraft AS ac
                   ON f.Aircraft = ac.RegMark
                   LEFT JOIN passengerFlight AS pf
                   ON f.FlightID = pf.FlightID
                   LEFT JOIN passenger AS p
                   ON pf.PassengerID = p.PassengerID
                   left join STATUS AS S
                   on f.FlightStatus = s.FlightStatus
                   where f.flightdate >= %s and f.flightdate <= %s
                   GROUP BY f.FlightID, r.FlightNum, f.FlightDate, a.AirportCode, f.DepEstAct, aa.AirportName, f.ArrTime, ac.Seating
                  order by f.FlightDate, f.deptime,a.Airportname;""")        
    parameter = (current_date,date_7after)
    cur.execute(sql,parameter)
    dbOutput = cur.fetchall()
    return render_template("adminFlight.html", userSelect = dbOutput, staffID = staffID, isManager=isManager)
    
    
@app.route("/admin/flight/details/", methods = ['POST','GET'])   #update the new details into the db 
def flightDetail():
    if request.method == 'POST':  #if the staff change the flight info
        flightDetails=request.form
        staffID = flightDetails['staffID']
        flightID = flightDetails['flightID']

        print(staffID)
        print(flightID)

        isManager = CheckManager(staffID)
        if isManager:
           deptime = flightDetails['deptime']
           arrtime = flightDetails['arrtime']
           regMark = flightDetails['regMark']
           status = flightDetails['status']
           flightID = flightDetails['flightID']

           print(flightID)
           print(deptime)
           print(arrtime)
           print(regMark)
           print(status)
           


           cur = getCursor() 
           dbsql = """update flight
                   set deptime=%s,arrtime=%s,aircraft =%s,flightstatus=%s
                   where flightid = %s;"""
           parameters = (deptime,arrtime,regMark,status,flightID)
           cur.execute(dbsql,parameters) 
           connection.commit()

           print(cur.statement)

           return render_template("admin.html",edit_flight="flight details had been changed!")
        else:
            deptime = flightDetails['deptime']
            arrtime = flightDetails['arrtime']
            status = flightDetails['status']

            cur = getCursor()  
            dbsql = """update flight
                   set deptime=%s,arrtime=%s,flightstatus=%s
                   where flightid = %s;"""
            parameters = (deptime,arrtime,status,flightID)
            cur.execute(dbsql,parameters) 
            connection.commit()
            return render_template("admin.html",edit_flight="flight details had been changed!")        
    else:
       staffID = request.args.get("staffID")
       flightID = request.args.get("flightID")
       isManager = CheckManager(staffID)      
       cur3 = getCursor()
       cur3.execute("""select regmark from aircraft;""") #fetch all the regmark for manager to choose
       dbOutput3=cur3.fetchall()

       cur = getCursor()   #fetch the details of this specific flight
       sql = ("""SELECT DISTINCT f.FlightID, r.FlightNum, f.FlightDate, a.Airportname AS DepartAirport, 
                   f.deptime, aa.AirportName AS ArrivalAirpot, f.ArrTime,f.Aircraft, COUNT(p.PassengerID) as seatBooked, 
                   ac.Seating - COUNT(p.PassengerID) AS seatAvailable, f.FlightStatus
                   FROM flight AS f
                   LEFT JOIN route AS r
                   ON f.FlightNum = r.FlightNum
                   LEFT JOIN airport AS a
                   ON r.DepCode = a.AirportCode
                   LEFT JOIN airport AS aa
                    ON r.DepCode = aa.AirportCode
                   LEFT JOIN aircraft AS ac
                   ON f.Aircraft = ac.RegMark
                   LEFT JOIN passengerFlight AS pf
                   ON f.FlightID = pf.FlightID
                   LEFT JOIN passenger AS p
                   ON pf.PassengerID = p.PassengerID
                   left join STATUS AS S
                   on f.FlightStatus = s.FlightStatus
                   where f.flightid = %s
                   ;""")     
       parameter = (flightID,)   
       cur.execute(sql,parameter)
       dbOutput = cur.fetchall()
    
       cur2 = getCursor()  #fetch all the passenger under this flight
       sql2 = ("""SELECT * 
            from passenger as p
            join passengerflight as pf
            on pf.PassengerID = p.PassengerID
            join flight as f
            on f.flightid = pf.FlightID
            where f.flightid = %s
            order by p.lastname, p.firstname;""")
       parameter2 = (flightID,)
       cur2.execute(sql2,parameter2)
       dbOutput2 = cur2.fetchall()
    
       passengerID = dbOutput2[0][0]
    
       return render_template("adminFlightDetail.html",flightID=flightID,staffID=staffID,passengerID=passengerID,
        userSelect = dbOutput, passenger = dbOutput2,isManager=isManager,regMark=dbOutput3)


@app.route("/admin/flight/add/",methods = ['POST','GET'])#insert these values into database flight table 为什么没成功？？？？？？？？？???
def adminFlightAdd():
    if request.method == 'POST':
        newFlight = request.form
        print(newFlight)

        flightnum = newFlight['flightnum'] #fetch the value from the user
        weeknum = newFlight['weeknum']
        flightdate = newFlight['flightdate']
        deptime = newFlight['deptime']
        arrtime = newFlight['arrtime']
       # duration = arrtime -deptime
        depEstAct = newFlight['deptime']
        arrEstAct = newFlight['arrtime']
        flightstatus = "On time"
        aircraft = newFlight['aircraft']

        print(flightnum,weeknum,flightdate,deptime,arrtime,depEstAct,arrEstAct,flightstatus,aircraft)
        
        cur = getCursor()   #insert these values into database flight table
        dbsql = """insert into flight(flightnum,weeknum,flightdate,deptime,arrtime,duration,depEstAct,arrEstAct,flightstatus,aircraft)
                   values(%s,%s,%s,%s,%s,'30:00',%s,%s,%s,%s);"""
        parameters = (flightnum,weeknum,flightdate,deptime,arrtime,depEstAct,arrEstAct,flightstatus,aircraft)
        cur.execute(dbsql,parameters) 
        
        print(cur.statement)

        return render_template('home.html')
    else:

        cur = getCursor()
        cur.execute("""select regmark from aircraft;""")
        dbOutput=cur.fetchall()    

        print(dbOutput)
        
        cur2 = getCursor()
        cur.execute("""select distinct flightnum from flight;""")
        dbOutput2=cur2.fechall()

        print(dbOutput2)
       

        return render_template("adminFlightAdd.html",regMark=dbOutput,flightNum = dbOutput2)    

@app.route("/admin/flight/duplicate/")
def adminDuplicate():
    cur=getCursor()
    cur.execute("""INSERT INTO flight(FlightNum, WeekNum, FlightDate, DepTime, ArrTime, Duration, DepEstAct, ArrEstAct, FlightStatus, Aircraft)
            SELECT FlightNum, WeekNum+1, date_add(FlightDate, interval 7 day), DepTime, ArrTime, Duration, DepTime, ArrTime, 'On time', Aircraft
            FROM flight
            WHERE WeekNum = (SELECT MAX(WeekNum) FROM flight);""")
    
    return render_template("admin.html",duplicate="flights for new week had been duplicated from lastest week!")
#记得要在上传github时候有一个text记录所有pip installed







   

