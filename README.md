# assessment3
for the third assessment of 636

## 在本地写好code，如何上传到github网页？

- github destop中选择用VScode打开（respository)
- 修改此.md文档或其他文档中的code
- 保存ctrl+s
- 回到github destop，左下角选择commit to main(可加description)
- 选择push origin
- 此时打开github website，可以看到修改过后的文档状况

# Project title
Python and Database Assessment
# sub title
- name:Enci lyu 
- Student ID: 1153399
# Project Description
This assessment develops an airline flight management web application for Air Whakatū based out 
of Nelson, New Zealand. It manages customer bookings, flights, routes, airports and aircraft.

The website consists of two main parts: a public area for customers to look up flight details and 
book flights, and an administration area for staff to add and edit flight details, bookings and 
passenger information.
# How to Install and Run the Project
# Project details and design

- ## universal 
     - I have a app.py file coded with python(flask), which connected to my database 
     - In my templates folder, there are all the html file connected to my app.py file
     - My home.html file includes logo pictures which located in my static folder as well as the contacts info, and those will be inherit to all the other html files
    - My home.html has the link of bootstrap, and it will be inherit to other html files
- ##  public area for customers
    - ### @app.route("/") 
      it returns the home.html file,this is the first page the user will see, and there are two Links in the middle of the page, one links to /screen/ page and another links to /login/ page
    - ### @app.route("/screen/")
      it will load the screen.html file firstly,and user can select the airport in this page by filling a form\
      after they submit(if request.method == 'POST'), the airportcode will be passed to backend to fetch all the value and then pass that value to database to fetch the airport info
    - ### @app.route("/login/")
      in this page,it will load login.html firstly, and there is a input for user to fill their email(if they have one), and three buttons: 'submit', 'register' and 'logout'. \
      first,in backend, I will get all the emailaddress from database, then when user enter their email( if the user don't want to enter the email to login, they can also register or logout,I will talk later):
        - if the email is in my emaillist, the user will login succesfully, and it will show two table,one is the details of user, another is the booking detail of the user,and they can click the ID to edit their info(this links to /login/edit/)
        - if the email is not in my emailist, it will suggest to register
    - ### @app.route("/login/edit/")
       in this page ,it will load edit.html file, and there is a form for user to fill,\
       in backend,first of all ,I fetch the user details again and pass to value to the fronend to remind the user what's the value now when they try to change them.\
        once they submit the form(if request.method == 'POST'), it will insert their new details into the database, and display the /login/ page for user to re-login.
    - ### @app.route("/cancel/")
       this page is linked from the /login/ page (when user login successfully and then click the cancel button after one booking )\
       in this page, it will fetch the specific flightID and specific passengerID from the url, and , remove the passenger from the flight,and it will load the /login/ page.
    - ### @app.route("/add/")
      this page is linked from the /login/ page(when user login successfully and then click the button named 'add new booking!')\
      this page will load add.html file,and user can selects departure airport here. All flights from that airport are displayed for the selected date and 7 days after that date, A button named 'back' is available to take the customer back to the previous page which is the /login/ page. 
    - ### @app.route("/add/success/") 
    - ### @app.route("/register/"）
      this page is linked from the /login page,when user click the 'register' button,they will come to here\
      it will load the register.html file at first, and there is a form for user to fill, after they submit(if request.method == 'POST'), there is a sql query to fetch this values and send it into the database (passenger table), then we have a new passenger\
      after the user registered, it will load the /login/ page.
  
- ## administration area for staff
    - ### @app.route("/admin/")
      this page is the first page for staff to login.\
      it will load admin.html file,and staff can select their name here, and pass the value(staffID) back to backend as well as the URL.\
      after staff login (if request.method == 'POST'),they are welcomed and there are two buttons:'passenger infomation' links to /admin/passenger/ page and 'flight infomation' links to /admin/flight/ page.
    - ### @app.route("/admin/passenger/")
      this page will load adminPassenger.html file, it will display all the details of all passengers.And there is a search place for them to enter passenger's lastname.\
      if they choose to search, and the value they entered is in my value list(varieble called 'lastname_list') , and there is a sql query to fetch all the datails of passengers with that lastname, and pass all the info into html table to display.\
      if they entered an wrong/invalid value, then it will just load adminPassenger.html file, it will display all the details of all passengers.
      and there is a button:'add new passenger' links to /admin/passenger/register.\
      ALL the passenger id number in this page is a link which links to /admin/passenger/details/ page about the specific passenger.
    - ### @app.route("/admin/passenger/register/")
      this page will firstly load adminRegister.html file, very similar with register.html file, there is also a form for staff to fill, after they submit(if request.method == 'POST'), there is a sql query to fetch this values and send it into the database (passenger table), then we have a new passenger\
      after new user has been registered, it will load the adminLogin.html, here there are two buttons:'passenger infomation' links to /admin/passenger/ page and 'flight infomation' links to /admin/flight/ page.
    - ### @app.route("/admin/passenger/details/")
      this page will load adminDetails.html.\
      there will display two tables, one is the specific passenger details and the id number links to /admin/passenger/edit/ page.\
      another table displays all bookings under this passenger. there is a cancel button after every booking(if has), this button will links to /admin/passenger/cancel/ page
    - ### @app.route("/admin/passenger/edit/"）
      this page will load adminedit.html file firstly.It's very similar to edit.html file.\
      in backend,first of all ,It fetches the user details again and pass to value to the fronend to remind the staff what's the value now when they try to change them.\
      once they submit the form(if request.method == 'POST'), it will insert their new details into the database, and display the /admin/passenger/details/ page.
    - ### @app.route("/admin/passenger/cancel/")
      this page is linked from the /admin/passenger/details/ page ，if staff click the cancel button there, they will be here.\
       in this page, it will fetch the specific flightID and specific passengerID from the url, and , remove the passenger from the flight,and it will load the adminCancel.html file which remind the staff the booking had been cancel and they can back to /admin/ page with a link.
    - ### @app.route("/admin/flight/")
      this page linked from /admin/ page and will load adminFlight.html file. There is a table display flights info.
      The flightid number is a link, which links to /admin/flight/details.\
    - ### @app.route("/admin/flight/details/")
      this page will load adminFlightDetail.html file which shows the flight manifest.\
      In this page, there are two tables ,the first table shows the specific flight details, another table shows the passengers ids under this flight, if staff clicks the passenger ID number, it will link to /admin/passenger/details/ page which staff can change the passenger details just samse as above.
      

      

