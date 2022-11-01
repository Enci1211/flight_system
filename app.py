# Name:  Enci Lyu
# Student ID: 1153399
####################################################




import mysql.connector
from mysql.connector import FieldType
import datetime
from datetime import timedelta
import connect_airline
from flask import Flask,render_template,request,redirect
from flask import url_for



app = Flask(__name__)

timeNow = datetime.datetime(2022,10,28,17,0,0)
dateNow = datetime.date(2022,10,28)
timeNow_hms = datetime.time(17,0,0)



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


 # Public system for customers
       
@app.route("/")
def home():
    return render_template("home.html")


@app.route("/screen/" , methods = ['POST','GET'])#select an airport, display info dep/arr at this airport
def screen():
    date_before = dateNow - timedelta(days=2) #create a date 2days before "current day"
    date_after = dateNow + timedelta(days=5)  #create a date 5days after "current day"
    
    if request.method == 'POST':
        userSelect = request.form['select']
                          
        cur = getCursor() #Shows appropriate arrivals and departures information for a selected airport
        dbsql = ("""SELECT r.FlightNum, f.FlightDate, r.DepCode, a.AirportName as depairport, f.DepTime, r.ArrCode, aa.AirportName as arrairport,f.ArrTime
                   from route as r
                   join airport as a
                   on r.DepCode = a.AirportCode
                   join airport as aa
                   on r.ArrCode = aa.AirportCode
                   join flight as f
                   on f.FlightNum = r.FlightNum
                   where (f.FlightDate >= %s and f.FlightDate <= %s AND
                         a.AirportCode = %s) or 
                         (f.FlightDate >= %s and f.FlightDate <= %s AND 
                         aa.AirportCode = %s)
                   order by f.FlightDate;""")
        parameters = (date_before,date_after,userSelect, date_before,date_after,userSelect)
        cur.execute(dbsql,parameters) 
        dbOutput = cur.fetchall()
        return render_template("screen.html",userSelect = dbOutput)
        
    return render_template("screen.html")

@app.route("/login/", methods = ['POST','GET'])#enter id to login,if successfull, display all the booking under this user(email)
def login():
    cur = getCursor()
    cur.execute("""SELECT EmailAddress FROM passenger;""")#get all the id from database
    dbOutput = cur.fetchall()
    emailList = [item for t in dbOutput for item in t]
    
    if request.method == 'POST':
        userEmail = request.form['email'] #user fill in the form with the email

        if userEmail in emailList:    
            print(userEmail)
            cur = getCursor()  #fetch the user details
            dbsql = ("""select PassengerID, FirstName, LastName, EmailAddress
                        from passenger
                        where EmailAddress = %s""")
            parameter = (userEmail,) 
            cur.execute(dbsql,parameter)
            dbOutput = cur.fetchall()  
                 
            cur2 = getCursor()#fetch the details of all the bookings this user(with this email above) had made            
            dbsql2=("""SELECT p.PassengerID, f.FlightID, f.FlightNum, f.FlightDate,f.DepTime,a.AirportName as depairport
                            from passenger as p
                            join passengerFlight as pf
                            on pf.PassengerID = p.PassengerID
                            join flight as f
                            on f.FlightID = pf.FlightID 
                            join route as r
                            on f.FlightNum = r.FlightNum
                            join airport as a
                            on r.DepCode = a.AirportCode
                            where p.EmailAddress = %s
                            order by f.FlightDate,f.DepTime;""")
            parameter2 = (userEmail,)
            cur2.execute(dbsql2,parameter2)
            
            dbOutput2 = cur2.fetchall()
            
            cur3 = getCursor()  #fetch the passengerID
            dbsql3 = ("""select PassengerID from passenger
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
    sql = ("""DELETE FROM passengerFlight
              where FlightID = %s and PassengerID = %s;""")
    parameters=(flightID, passengerID)
    cur.execute(sql,parameters)
    connection.commit()

    print(cur.statement)
    
    return render_template('login.html',cancel= "this booking had been canceled, please login again to check!")

    
@app.route("/login/edit/",methods = ['POST','GET'])
def edit():    
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
    
        
        cur = getCursor()   #update the new details into the db 
        dbsql = """update passenger
                   set FirstName=%s,LastName=%s,EmailAddress=%s,PhoneNumber=%s,PassportNumber=%s,DateOfBirth=%s
                   where PassengerID = %s;"""
        parameters = (firstName,lastName,emailAddress,phoneNum,passportNum,dateBirth,passengerID)
        cur.execute(dbsql,parameters) 
        connection.commit()
        
        return redirect(url_for('login'))
    
    
    else: 
        passengerID = request.args.get("passengerID")
        print(passengerID)
        cur = getCursor() #fetch the details for this specific passenger
        dbsql = ("""select FirstName, LastName, EmailAddress, PhoneNumber, PassportNumber, DateOfBirth,PassengerID 
                from passenger
                where PassengerID = %s""")
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
                
@app.route("/add/",methods = ['POST','GET'])#add new booking 
def add():
    
    if request.method == 'POST':
        date_7after = timeNow + timedelta(days=7) 
        userSelect = request.form['select']
        passengerID = request.form['passengerID']
        print(userSelect)  
        print(passengerID) 


        cur = getCursor()   #User selects departure airport. All available flights(not been cancelled and still have seat) from that airport are displayed for the selected date and 7 days after that date
        dbsql = """SELECT DISTINCT f.FlightID, r.FlightNum, f.FlightDate, a.AirportName AS DepartAirport, 
                   f.DepTime, aa.AirportName AS ArrivalAirpot, f.ArrTime, ac.Seating - COUNT(pf.PassengerID) AS seatAvailable, f.FlightStatus, s.StatusDesc
                   FROM flight AS f
                   JOIN route AS r
                   ON f.FlightNum = r.FlightNum
                   JOIN airport AS a
                   ON r.DepCode = a.AirportCode  
                   JOIN airport as aa
                   on r.ArrCode = aa.AirportCode                 
                   JOIN aircraft AS ac
                   ON f.Aircraft = ac.RegMark
                   JOIN passengerFlight AS pf
                   ON f.FlightID = pf.FlightID                  
                   join status AS s
                   on f.FlightStatus = s.FlightStatus
                   where (r.DepCode = %s and f.FlightDate = %s and f.FlightDate <= %s and f.DepTime >= %s and f.FlightStatus != 'Cancelled' )
                         or (r.DepCode = %s and f.FlightDate > %s and f.FlightDate <= %s and f.FlightStatus != 'Cancelled')
                   GROUP BY f.FlightID, r.FlightNum, f.FlightDate, r.DepCode, f.Deptime, a.AirportName, f.ArrTime  
                   having seatavailable  > 0                                 
                   order by f.FlightDate;"""
        parameters = (userSelect, dateNow,date_7after,timeNow_hms,userSelect,dateNow,date_7after)
        cur.execute(dbsql,parameters) 
        dbOutput = cur.fetchall()
        print(dbOutput)

        cur2=getCursor() #if have, fetch the flight that have NO SEAT !and display
        dbsql2=("""SELECT DISTINCT f.FlightID, r.FlightNum, f.FlightDate, a.AirportName AS DepartAirport, 
                   f.DepTime, aa.AirportName AS ArrivalAirpot, f.ArrTime, ac.Seating - COUNT(pf.PassengerID) AS seatAvailable, f.FlightStatus, s.StatusDesc
                   FROM flight AS f
                   JOIN route AS r
                   ON f.FlightNum = r.FlightNum
                   JOIN airport AS a
                   ON r.DepCode = a.AirportCode  
                   JOIN airport as aa
                   on r.ArrCode = aa.AirportCode                 
                   JOIN aircraft AS ac
                   ON f.Aircraft = ac.RegMark
                   JOIN passengerFlight AS pf
                   ON f.FlightID = pf.FlightID                  
                   join status AS s
                   on f.FlightStatus = s.FlightStatus
                   where (r.DepCode = %s and f.FlightDate = %s and f.FlightDate <= %s and f.DepTime >= %s)
                         or (r.DepCode = %s and f.FlightDate > %s and f.FlightDate <= %s)
                   GROUP BY f.FlightID, r.FlightNum, f.FlightDate, r.DepCode, f.DepTime, a.AirportName, f.ArrTime  
                   having seatavailable  <= 0                                 
                   order by f.FlightDate; """)
        parameters2 = (userSelect, dateNow,date_7after,timeNow_hms,userSelect,dateNow,date_7after)
        cur2.execute(dbsql2,parameters2) 
        dbOutput2 = cur2.fetchall()
        print(dbOutput2)

        cur3=getCursor() #if have , fetch the flight that have been CANCELLED (although have seats)
        dbsql3=("""SELECT DISTINCT f.FlightID, r.FlightNum, f.FlightDate, a.AirportName AS DepartAirport, 
                   f.DepTime, aa.AirportName AS ArrivalAirpot, f.ArrTime, ac.Seating - COUNT(pf.PassengerID) AS seatAvailable, f.FlightStatus, s.StatusDesc
                   FROM flight AS f
                   JOIN route AS r
                   ON f.FlightNum = r.FlightNum
                   JOIN airport AS a
                   ON r.DepCode = a.AirportCode 
                   JOIN airport as aa
                   on r.ArrCode = aa.AirportCode                  
                   JOIN aircraft AS ac
                   ON f.Aircraft = ac.RegMark
                   JOIN passengerFlight AS pf
                   ON f.FlightID = pf.FlightID                  
                   join status AS s
                   on f.FlightStatus = s.FlightStatus
                   where (r.DepCode = %s and f.FlightDate = %s and f.FlightDate <= %s and f.DepTime >= %s and f.FlightStatus = 'Cancelled')
                         or (r.DepCode = %s and f.FlightDate > %s and f.FlightDate <= %s and f.FlightStatus = 'Cancelled')
                   GROUP BY f.FlightID, r.FlightNum, f.FlightDate, r.DepCode, f.Deptime, a.AirportName, f.ArrTime  
                   having seatavailable  > 0                                 
                   order by f.FlightDate;""")
        parameters3 = (userSelect, dateNow,date_7after,timeNow_hms,userSelect,dateNow,date_7after)
        cur3.execute(dbsql3,parameters3) 
        dbOutput3 = cur3.fetchall()
        print(dbOutput3)
        
   
        return render_template("add.html",available = dbOutput,noseats=dbOutput2,cancelled=dbOutput3,passengerID = passengerID) 
        
           
    else:
        passengerID = request.args.get("passengerID")
        print(passengerID)

        return render_template("add.html",passengerID=passengerID)  

@app.route("/add/success/") 
def addSuccess():
    passengerID = request.args.get("passengerID") 
    flightID = request.args.get("flightID") 

    cur = getCursor()
    dbsql = ("""select * from passengerFlight
                where FlightID = %s and PassengerID = %s;""")
    parameters=(flightID,passengerID)
    cur.execute(dbsql,parameters)
    dbOutput = cur.fetchall()
    print(dbOutput)

    if len(dbOutput) == 0:

       cur = getCursor()
       dbsql = """INSERT INTO passengerFlight(FlightID,PassengerID)
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

def CheckManager(staffID):#check if the staff is the manager or not
    cur = getCursor()
    sql = ("""SELECT IsManager from staff
                   WHERE staffID = %s;""")
    parameter = (staffID,)
    cur.execute(sql,parameter)
    dbOutput = cur.fetchall()
    isManagerNum = dbOutput[0][0]
    if isManagerNum == 1:
        return True
    else:
        return False
    

@app.route("/admin/", methods = ['POST','GET']) #staff login page
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
       cur.execute("""SELECT LastName FROM passenger;""")#get all the lastname from database
       dbOutput = cur.fetchall()
       lastname_list = [item for t in dbOutput for item in t]

       if lastname in lastname_list:

           cur = getCursor()
           sql = ("""select * from passenger where LastName = %s;""") #display the passenger details with the lastname staff entered
           parameter = (lastname,)
           cur.execute(sql,parameter)
           dbOutput = cur.fetchall()
           return render_template("adminPassenger.html", userSelect = dbOutput,staffID = staffID)
       else:
            staffID = request.args.get("staffID") #if staff entered a wrong/invalid value, just display all the passeger details
            cur = getCursor()
            cur.execute("""SELECT * FROM passenger
                     order by LastName, FirstName;""")        
            dbOutput = cur.fetchall()
            return render_template("adminPassenger.html", userSelect = dbOutput,staffID = staffID)

    else: 
       staffID = request.args.get("staffID") 
       cur = getCursor()  #display all the passeger details
       cur.execute("""SELECT * FROM passenger 
                     order by LastName, FirstName;""")        
       dbOutput = cur.fetchall()
       return render_template("adminPassenger.html", userSelect = dbOutput,staffID = staffID)


@app.route("/admin/passenger/register/", methods = ['POST','GET']) #add new customer
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
                    where passengerID = %s;""")    #fetch the specific passenger info
    parameter = (passengerID,)
    cur.execute(dbsql,parameter)
    dbOutput = cur.fetchall()
    
    cur2 = getCursor()
    dbsql2 = ("""SELECT p.PassengerID, p.FirstName, p.LastName, f.FlightID, f.FlightNum, f.FlightDate
                 FROM flight as f
                 join passengerFlight as pf
                 on f.FlightID = pf.FlightID
                 join passenger as p
                 on pf.PassengerID = p.PassengerID
                 where p.PassengerID = %s;""") #fetch all the booking under the specific passenger
    parameter2 = (passengerID,)
    cur2.execute(dbsql2,parameter2)
    dbOutput2 = cur2.fetchall()
    
    return render_template("adminDetails.html", passenger = dbOutput, passengerBooking = dbOutput2, staffID = staffID,passengerID= passengerID)
                          
@app.route("/admin/passenger/add/",methods = ['POST','GET']) #add new booking for specific customer
def adminAdd():
    
    if request.method == 'POST':
        date_7after = timeNow + timedelta(days=7) 
        userSelect = request.form['select']
        passengerID = request.form['passengerID']
        print(userSelect)  
        print(passengerID) 


        cur = getCursor()   #User selects departure airport. All available flights(not been cancelled and still have seat) from that airport are displayed for the selected date and 7 days after that date
        dbsql = """SELECT DISTINCT f.FlightID, r.FlightNum, f.FlightDate, a.AirportName AS DepartAirport, 
                   f.DepTime, aa.AirportName AS ArrivalAirpot, f.ArrTime, ac.Seating - COUNT(pf.PassengerID) AS seatAvailable, f.FlightStatus, s.StatusDesc
                   FROM flight AS f
                   JOIN route AS r
                   ON f.FlightNum = r.FlightNum
                   JOIN airport AS a
                   ON r.DepCode = a.AirportCode  
                   JOIN airport as aa
                   on r.ArrCode = aa.AirportCode                 
                   JOIN aircraft AS ac
                   ON f.Aircraft = ac.RegMark
                   JOIN passengerFlight AS pf
                   ON f.FlightID = pf.FlightID                  
                   join status AS s
                   on f.FlightStatus = s.FlightStatus
                   where (r.DepCode = %s and f.FlightDate = %s and f.FlightDate <= %s and f.DepTime >= %s and f.FlightStatus != 'Cancelled' )
                         or (r.DepCode = %s and f.FlightDate > %s and f.FlightDate <= %s and f.FlightStatus != 'Cancelled')
                   GROUP BY f.FlightID, r.FlightNum, f.FlightDate, r.DepCode, f.DepTime, a.AirportName, f.ArrTime  
                   having seatavailable  > 0                                 
                   order by f.FlightDate;"""
        parameters = (userSelect, dateNow,date_7after,timeNow_hms,userSelect,dateNow,date_7after)
        cur.execute(dbsql,parameters) 
        dbOutput = cur.fetchall()
        print(dbOutput)

        cur2=getCursor() #if have, fetch the flight that have NO SEAT !and display
        dbsql2=("""SELECT DISTINCT f.FlightID, r.FlightNum, f.FlightDate, a.AirportName AS DepartAirport, 
                   f.DepTime, aa.AirportName AS ArrivalAirpot, f.ArrTime, ac.Seating - COUNT(pf.PassengerID) AS seatAvailable, f.FlightStatus, s.StatusDesc
                   FROM flight AS f
                   JOIN route AS r
                   ON f.FlightNum = r.FlightNum
                   JOIN airport AS a
                   ON r.DepCode = a.AirportCode  
                   JOIN airport as aa
                   on r.ArrCode = aa.AirportCode                 
                   JOIN aircraft AS ac
                   ON f.Aircraft = ac.RegMark
                   JOIN passengerFlight AS pf
                   ON f.FlightID = pf.FlightID                  
                   join status AS s
                   on f.FlightStatus = s.FlightStatus
                   where (r.DepCode = %s and f.FlightDate = %s and f.FlightDate <= %s and f.DepTime >= %s)
                         or (r.DepCode = %s and f.FlightDate > %s and f.FlightDate <= %s)
                   GROUP BY f.FlightID, r.FlightNum, f.FlightDate, r.DepCode, f.DepTime, a.AirportName, f.ArrTime  
                   having seatavailable  <= 0                                 
                   order by f.FlightDate; """)
        parameters2 = (userSelect, dateNow,date_7after,timeNow_hms,userSelect,dateNow,date_7after)
        cur2.execute(dbsql2,parameters2) 
        dbOutput2 = cur2.fetchall()
        print(dbOutput2)

        cur3=getCursor() #if have , fetch the flight that have been CANCELLED (although have seats)
        dbsql3=("""SELECT DISTINCT f.FlightID, r.FlightNum, f.FlightDate, a.AirportName AS DepartAirport, 
                   f.DepTime, aa.AirportName AS ArrivalAirpot, f.ArrTime, ac.Seating - COUNT(pf.PassengerID) AS seatAvailable, f.FlightStatus, s.StatusDesc
                   FROM flight AS f
                   JOIN route AS r
                   ON f.FlightNum = r.FlightNum
                   JOIN airport AS a
                   ON r.DepCode = a.AirportCode 
                   JOIN airport as aa
                   on r.ArrCode = aa.AirportCode                  
                   JOIN aircraft AS ac
                   ON f.Aircraft = ac.RegMark
                   JOIN passengerFlight AS pf
                   ON f.FlightID = pf.FlightID                  
                   join status AS s
                   on f.FlightStatus = s.FlightStatus
                   where (r.DepCode = %s and f.FlightDate = %s and f.FlightDate <= %s and f.DepTime >= %s and f.FlightStatus = 'Cancelled')
                         or (r.DepCode = %s and f.FlightDate > %s and f.FlightDate <= %s and f.FlightStatus = 'Cancelled')
                   GROUP BY f.FlightID, r.FlightNum, f.FlightDate, r.DepCode, f.DepTime, a.AirportName, f.ArrTime  
                   having seatavailable  > 0                                 
                   order by f.FlightDate;""")
        parameters3 = (userSelect, dateNow,date_7after,timeNow_hms,userSelect,dateNow,date_7after)
        cur3.execute(dbsql3,parameters3) 
        dbOutput3 = cur3.fetchall()
        print(dbOutput3)
        return render_template("adminAdd.html",available = dbOutput,noseats=dbOutput2,cancelled=dbOutput3,passengerID = passengerID) 
    else:
        passengerID = request.args.get("passengerID")
        return render_template("adminAdd.html",passengerID=passengerID)  

@app.route("/admin/passenger/add/success/") 
def adminAddSuc():
    passengerID = request.args.get("passengerID") 
    flightID = request.args.get("flightID") 

    cur = getCursor()
    dbsql = ("""select * from passengerFlight
                where FlightID = %s and PassengerID = %s;""")
    parameters=(flightID,passengerID)
    cur.execute(dbsql,parameters)
    dbOutput = cur.fetchall()
    print(dbOutput)

    if len(dbOutput) == 0:

       cur = getCursor()
       dbsql = """INSERT INTO passengerFlight(FlightID,PassengerID)
                   VALUES(%s,%s);"""
       parameters = (flightID,passengerID)
       cur.execute(dbsql,parameters)

       return render_template("admin.html",success = "new booking have been added to the passenger!") 
    return render_template("admin.html",success = "the booking is exist!") 

@app.route("/admin/passenger/edit/",methods = ['POST','GET'])#edit the passenger details

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
        
        cur = getCursor()  
        dbsql = """update passenger
                   set FirstName=%s,LastName=%s,EmailAddress=%s,PhoneNumber=%s,PassportNumber=%s,DateOfBirth=%s
                   where PassengerID = %s;"""
        parameters = (firstName,lastName,emailAddress,phoneNum,passportNum,dateBirth,passengerID)
        cur.execute(dbsql,parameters) 
        connection.commit()
        return redirect(url_for('admin'))
    
    
    else: 
        passengerID = request.args.get("passengerID")
        staffID = request.args.get("staffID")
        cur = getCursor() #fetch the details for this specific passenger
        dbsql = ("""select FirstName, LastName, EmailAddress, PhoneNumber, PassportNumber, DateOfBirth, PassengerID
                from passenger
                where PassengerID = %s""")
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
                
                     
@app.route("/admin/passenger/cancel/")#cancel the booking from a specific passenger
def adminCancel():
    flightID = request.args.get("flightID")
    passengerID = request.args.get("passengerID")

    print(passengerID)
    print(flightID)
    
    cur = getCursor() 
    sql = ("""DELETE FROM passengerFlight
              where FlightID = %s and PassengerID = %s;""")
    paremeters =(flightID,passengerID)
    cur.execute(sql,paremeters)
    connection.commit()

    print(cur.statement)
    
    return render_template("admin.html",cancel = "the booking have been canceled")   
    
@app.route("/admin/flight/", methods = ['POST','GET']) #staff can get all the flights info in a talbe in this page,only manager can add flights in this page
def adminFlight():  
    if request.method == 'POST':
       staffID = request.form.get("staffID")
       print(staffID)
       isManager = CheckManager(staffID)

       search = request.form.get("search") 
       depcode=search.upper()
       print(depcode)

       cur = getCursor()
       cur.execute("""SELECT DepCode from route;""")#get all the dep-code from database
       dbOutput = cur.fetchall()
       depCode_list = [item for t in dbOutput for item in t]
       
       if depcode in depCode_list:  #The list can be filtered by departure airport-CODE
           staffID = request.form.get("staffID")
           isManager = CheckManager(staffID)
           print(isManager)

           date_7after = dateNow + timedelta(days=7) 
           cur = getCursor()
           sql = ("""SELECT DISTINCT f.FlightID, r.FlightNum, f.FlightDate, a.AirportName AS DepartAirport, 
                   f.DepTime, aa.AirportName AS ArrivalAirpot, f.ArrTime,f.Aircraft, COUNT(p.PassengerID) as seatBooked, ac.Seating - COUNT(p.PassengerID) AS seatAvailable, f.FlightStatus
                   FROM flight AS f
                   LEFT JOIN route AS r
                   ON f.FlightNum = r.FlightNum
                   LEFT JOIN airport AS a
                   ON r.DepCode = a.AirportCode
                   LEFT JOIN airport AS aa
                    ON r.ArrCode = aa.AirportCode
                   LEFT JOIN aircraft AS ac
                   ON f.Aircraft = ac.RegMark
                   LEFT JOIN passengerFlight AS pf
                   ON f.FlightID = pf.FlightID
                   LEFT JOIN passenger AS p
                   ON pf.PassengerID = p.PassengerID
                   left join status AS s
                   on f.FlightStatus = s.FlightStatus
                   where f.FlightDate >= %s and f.FlightDate <= %s and r.DepCode = %s
                   GROUP BY f.FlightID, r.FlightNum, f.FlightDate, a.AirportCode, f.DepEstAct, aa.AirportName, f.ArrTime, ac.Seating
                  order by f.FlightDate, f.DepTime,a.AirportName;""")        
           parameter = (dateNow,date_7after,depcode)
           cur.execute(sql,parameter)
           dbOutput = cur.fetchall()
           return render_template("adminFlight.html", userSelect = dbOutput,staffID = staffID, isManager=isManager)
       else:
           staffID = request.form.get("staffID")
           isManager = CheckManager(staffID)
           print(isManager)

           date_7after = dateNow + timedelta(days=7) 

           cur = getCursor()
           sql = ("""SELECT DISTINCT f.FlightID, r.FlightNum, f.FlightDate, a.AirportName AS DepartAirport, 
                   f.DepTime, aa.AirportName AS ArrivalAirpot, f.ArrTime,f.Aircraft, COUNT(p.PassengerID) as seatBooked, ac.Seating - COUNT(p.PassengerID) AS seatAvailable, f.FlightStatus
                   FROM flight AS f
                   LEFT JOIN route AS r
                   ON f.FlightNum = r.FlightNum
                   LEFT JOIN airport AS a
                   ON r.DepCode = a.AirportCode
                   LEFT JOIN airport AS aa
                    ON r.ArrCode = aa.AirportCode
                   LEFT JOIN aircraft AS ac
                   ON f.Aircraft = ac.RegMark
                   LEFT JOIN passengerFlight AS pf
                   ON f.FlightID = pf.FlightID
                   LEFT JOIN passenger AS p
                   ON pf.PassengerID = p.PassengerID
                   left join status AS s
                   on f.FlightStatus = s.FlightStatus
                   where f.FlightDate >= %s and f.FlightDate <= %s
                   GROUP BY f.FlightID, r.FlightNum, f.FlightDate, a.AirportCode, f.DepEstAct, aa.AirportName, f.ArrTime, ac.Seating
                  order by f.FlightDate, f.DepTime,a.AirportName;""")        
           parameter = (dateNow,date_7after)
           cur.execute(sql,parameter)
           dbOutput = cur.fetchall()
           return render_template("adminFlight.html", userSelect = dbOutput,staffID = staffID, isManager=isManager)
    else:
       staffID = request.args.get("staffID")
       isManager = CheckManager(staffID)
       print(isManager)

       date_7after = dateNow + timedelta(days=7) 

       cur = getCursor()
       sql = ("""SELECT DISTINCT f.FlightID, r.FlightNum, f.FlightDate, a.AirportName AS DepartAirport, 
                   f.DepTime, aa.AirportName AS ArrivalAirpot, f.ArrTime,f.Aircraft, COUNT(p.PassengerID) as seatBooked, ac.Seating - COUNT(p.PassengerID) AS seatAvailable, f.FlightStatus
                   FROM flight AS f
                   LEFT JOIN route AS r
                   ON f.FlightNum = r.FlightNum
                   LEFT JOIN airport AS a
                   ON r.DepCode = a.AirportCode
                   LEFT JOIN airport AS aa
                    ON r.ArrCode = aa.AirportCode
                   LEFT JOIN aircraft AS ac
                   ON f.Aircraft = ac.RegMark
                   LEFT JOIN passengerFlight AS pf
                   ON f.FlightID = pf.FlightID
                   LEFT JOIN passenger AS p
                   ON pf.PassengerID = p.PassengerID
                   left join status AS s
                   on f.FlightStatus = s.FlightStatus
                   where f.FlightDate >= %s and f.FlightDate <= %s
                   GROUP BY f.FlightID, r.FlightNum, f.FlightDate, a.AirportCode, f.DepEstAct, aa.AirportName, f.ArrTime, ac.Seating
                  order by f.FlightDate, f.DepTime,a.AirportName;""")        
       parameter = (dateNow,date_7after)
       cur.execute(sql,parameter)
       dbOutput = cur.fetchall()
       return render_template("adminFlight.html", userSelect = dbOutput, staffID = staffID, isManager=isManager)
     
@app.route("/admin/flight/details/", methods = ['POST','GET'])   #flight manifest, update the new details of specific flight
def flightDetail():
    if request.method == 'POST':  #if the staff changed the flight info
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
           duration = (datetime.datetime.strptime(arrtime,'%H:%M')) -(datetime.datetime.strptime(deptime,'%H:%M'))

           print(flightID)
           print(deptime)
           print(arrtime)
           print(regMark)
           print(status)
           
           if status == 'Cancelled': #if the status is 'Cancelled' , change the value of arrEstAct and depEstAct to NULL
              cur = getCursor() 
              dbsql = """update flight
                   set DepTime=%s,ArrTime=%s,Duration=%s,DepEstAct=%s, ArrEstAct=%s, Aircraft =%s,FlightStatus=%s
                   where FlightID = %s;"""
              parameters = (deptime,arrtime,duration,None,None,regMark,status,flightID)
              cur.execute(dbsql,parameters) 
              connection.commit()
           else:
              cur = getCursor() 
              dbsql = """update flight
                   set DepTime=%s,ArrTime=%s,Duration=%s,DepEstAct=%s, ArrEstAct=%s,Aircraft =%s,FlightStatus=%s
                   where FlightID = %s;"""
              parameters = (deptime,arrtime,duration,deptime,arrtime,regMark,status,flightID)
              cur.execute(dbsql,parameters) 
              connection.commit()

           return render_template("admin.html",edit_flight="flight details had been changed!")
        else:
            deptime = flightDetails['deptime']
            arrtime = flightDetails['arrtime']
            status = flightDetails['status']
            duration = (datetime.datetime.strptime(arrtime,'%H:%M')) -(datetime.datetime.strptime(deptime,'%H:%M'))

            if status == 'Cancelled':
                cur = getCursor()  
                dbsql = """update flight
                   set DepTime=%s,ArrTime=%s,Duration=%s,DepEstAct=%s, ArrEstAct=%s,FlightStatus=%s
                   where FlightID = %s;"""
                parameters = (deptime,arrtime,duration,None,None,status,flightID)
                cur.execute(dbsql,parameters) 
                connection.commit()
            else:
                cur = getCursor()  
                dbsql = """update flight
                   set DepTime=%s,ArrTime=%s,Duration=%s,DepEstAct=%s, ArrEstAct=%s,FlightStatus=%s
                   where FlightID = %s;"""
                parameters = (deptime,arrtime,duration,deptime,arrtime,status,flightID)
                cur.execute(dbsql,parameters) 
                connection.commit()
            
            return render_template("admin.html",edit_flight="flight details had been changed!")        
    else:
       staffID = request.args.get("staffID")
       flightID = request.args.get("flightID")
       isManager = CheckManager(staffID)      
       cur3 = getCursor()
       cur3.execute("""select RegMark from aircraft;""") #fetch all the regmark for manager to choose
       dbOutput3=cur3.fetchall()
       regMark = [item for t in dbOutput3 for item in t]

       cur = getCursor()   #fetch the details of this specific flight
       sql = ("""SELECT DISTINCT f.FlightID, r.FlightNum, f.FlightDate, a.AirportName AS DepartAirport, 
                   f.DepTime, aa.AirportName AS ArrivalAirpot, f.ArrTime,f.Aircraft, COUNT(p.PassengerID) as seatBooked, 
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
                   left join status AS s
                   on f.FlightStatus = s.FlightStatus
                   where f.FlightID = %s
                   ;""")     
       parameter = (flightID,)   
       cur.execute(sql,parameter)
       dbOutput = cur.fetchall()
    
       cur2 = getCursor()  #fetch all the passenger under this flight
       sql2 = ("""SELECT p.PassengerID, p.FirstName, p.LastName, p.EmailAddress, p.PhoneNumber, p.PassportNumber 
            from passenger as p
            join passengerFlight as pf
            on pf.PassengerID = p.PassengerID
            join flight as f
            on f.FlightID = pf.FlightID
            where f.FlightID = %s
            order by p.LastName, p.FirstName;""")
       parameter2 = (flightID,)
       cur2.execute(sql2,parameter2)
       dbOutput2 = cur2.fetchall()
    
       passengerID = dbOutput2[0][0]
    
       return render_template("adminFlightDetail.html",flightID=flightID,staffID=staffID,passengerID=passengerID,
        userSelect = dbOutput, passenger = dbOutput2,isManager=isManager,regMark=regMark)


@app.route("/admin/flight/add/",methods = ['POST','GET'])# make a new flight(only manager can do)
def adminFlightAdd():
    if request.method == 'POST':
        newFlight = request.form
        print(newFlight)

        flightnum = newFlight['flightnum'] #fetch the value from the user
        weeknum = newFlight['weeknum']
        flightdate = newFlight['flightdate']
        deptime = newFlight['deptime']
        arrtime = newFlight['arrtime']
        duration = (datetime.datetime.strptime(arrtime,'%H:%M')) -(datetime.datetime.strptime(deptime,'%H:%M'))
        depEstAct = newFlight['deptime']
        arrEstAct = newFlight['arrtime']
        flightstatus = "On time"
        aircraft = newFlight['aircraft']
        
        cur = getCursor()   #insert these values into database flight table
        dbsql = """insert into flight(FlightNum,WeekNum,FlightDate,DepTime,ArrTime,Duration,DepEstAct,ArrEstAct,FlightStatus,Aircraft)
                   values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"""
        parameters = (flightnum,weeknum,flightdate,deptime,arrtime,duration,depEstAct,arrEstAct,flightstatus,aircraft)
        cur.execute(dbsql,parameters) 
        
        print(cur.statement)

        return render_template('admin.html', add_flight="new flight had been added!!")
    else:

        cur = getCursor()
        cur.execute("""select RegMark from aircraft;""")#fetch all the regmark for user to choose
        dbOutput=cur.fetchall()   
        regMark = [item for t in dbOutput for item in t] 

        print(regMark)
        
        cur2 = getCursor()
        cur2.execute("""select distinct FlightNum from flight;""")#fetch all the flightnum for choosing
        dbOutput2=cur2.fetchall()
        flightnum = [item for t in dbOutput2 for item in t]

        print(flightnum)
       

        return render_template("adminFlightAdd.html",regMark=regMark,flightNum = flightnum)    

@app.route("/admin/flight/duplicate/")#duplicate new week from the lastest week
def adminDuplicate():
    cur=getCursor()
    cur.execute("""INSERT INTO flight(FlightNum, WeekNum, FlightDate, DepTime, ArrTime, Duration, DepEstAct, ArrEstAct, FlightStatus, Aircraft)
            SELECT FlightNum, WeekNum+1, date_add(FlightDate, interval 7 day), DepTime, ArrTime, Duration, DepTime, ArrTime, 'On time', Aircraft
            FROM flight
            WHERE WeekNum = (SELECT MAX(WeekNum) FROM flight);""")
    
    return render_template("admin.html",duplicate="flights for new week had been duplicated from lastest week!")








   

