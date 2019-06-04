from flask import Flask, render_template, request, redirect, url_for, session
from flask_bootstrap import Bootstrap
from flask_mysqldb import MySQL
from forms import *
from models import User
from tables import *
import sys
from datetime import *

app = Flask(__name__)
Bootstrap(app)

app.config['MYSQL_USER'] = 'cs4400_team_23'
app.config['MYSQL_PASSWORD'] = '3NM9S3YD'
app.config['MYSQL_DB'] = 'cs4400_team_23'
app.config['MYSQL_HOST'] = 'academic-mysql.cc.gatech.edu'

mysql = MySQL(app)

cur = None;

with app.app_context():
    conn = mysql.connect
    cur = conn.cursor()


app.secret_key = "development-key"

curUser = None

propertyNameExists = 'A property with that name already exists.'

#This global variable is for making sure new owners don't have the cancel button on the add
#property page
newOwner = False

#Global varaibles for keeping track of visitor previous searches and sorts
visitorPropertyCurrentSort = "Name"
visitorPropertySearchType = "Name"
visitorPropertySearchText = ""
visitedPropertyCurrentSort = "Name"
visitedPropertySearchType = "Name"
visitedPropertySearchText = ""

#Global variables for keeping track of owner previous searches and sorts
ownerPropertyCurrentSort = "Name"
ownerPropertySearchType = "Name"
ownerPropertySearchText = ""
ownerOtherPropertyCurrentSort = "Name"
ownerOtherPropertySearchType = "Name"
ownerOtherPropertySearchText = ""

#Global variables for the admin visitor list functionality
adminVisitorCurrentSort = "Username"
adminVisitorSearchType = "Username"
adminVisitorSearchText = ""

#Global variables for the admin owner list functionality
adminOwnerCurrentSort = "Username"
adminOwnerSearchType = "Username"
adminOwnerSearchText = ""

#Global variables for the admin unconfirmed properties list functionality
adminUnconfirmedCurrentSort = "Name"
adminUnconfirmedSearchType = "Name"
adminUnconfirmedSearchText = ""

#Global variables for the admin confirmed properties list functionality
adminConfirmedCurrentSort = "Name"
adminConfirmedSearchType = "Name"
adminConfirmedSearchText = ""

#Global variables for the admin approved organisms list functionality
adminApprovedCurrentSort = "Name"
adminApprovedSearchType = "Name"
adminApprovedSearchText = ""

#Global variables for the admin pending organisms list functionality
adminPendingCurrentSort= "Name"
adminPendingSearchType = "Name"
adminPendingSearchText = ""

#Global variables for admin manage property functionality
addedOrganismsConfirmedProperty = []
deletedOrganismsConfirmedProperty = []
addedOrganismsUnconfirmedProperty = []
deletedOrganismsUnconfirmedProperty = []

@app.route('/', methods=['GET', 'POST'])
def index():
    global curUser
    register_form = RegisterForm()
    login_form = LoginForm()

    #curUser = User("billybob", "billy@gatech.edu", "123", "VISITOR")
    #return redirect(url_for('visitor'))

    #curUser = User("admin1", "admin@gatech.edu", "123", "ADMIN")
    #return redirect(url_for('admin'))

    #curUser = User("farmowner", "farmer@gatech.edu", "123", "OWNER")
    #return redirect(url_for('owner'))

    if request.method == 'POST':
        form_name = request.form['form-name']
        if form_name == 'login_form':
            if login_form.validate_on_submit():
                email = login_form.email.data
                password = login_form.password.data
                cur.execute('SELECT Username, UserType, Password, Email '
                            'FROM User '
                            'WHERE Email=%s', [email])
                try:
                    username, usertype, password_hash, email = cur.fetchone()
                except Exception:
                    return render_template('index.html', login_form=login_form, register_form=register_form, data="Email Not Registered")
                try:
                    curUser = User(username, email, password, usertype)
                    if password_hash == str(curUser.password_hash):
                        curUser = User(username, email, password, usertype)
                        print('login successful', file=sys.stderr)
                        print(curUser.username, file=sys.stderr)
                        if curUser.usertype == 'VISITOR':
                            session['logged_in'] = True
                            return redirect(url_for('visitor'))
                        elif curUser.usertype == "OWNER":
                            session['logged_in'] = True
                            return redirect(url_for('owner'))
                        elif curUser.usertype == "ADMIN":
                            session['logged_in'] = True
                            return render_template('AdminHome.html', username=curUser.username)
                    else:
                        print('login failed', file=sys.stderr)
                        curUser = None
                        return render_template('index.html', login_form=login_form, register_form=register_form,
                                               data="Wrong Email/Password Combination")
                except Exception:
                    print('exception logging in', file=sys.stderr)
                    return render_template('index.html', login_form=login_form, register_form=register_form,
                                           data="Error Logging In")
            else:
                return render_template('index.html', login_form=login_form, register_form=register_form,
                                       data="Error With Login Information")
        elif form_name == 'register_form':
            if register_form.validate_on_submit():
                username = register_form.user.data
                email = register_form.email.data
                password = register_form.password.data
                confirmPassword = register_form.confirmPassword.data
                usertype = register_form.type.data
                newuser = User(username, email, password, usertype)
                cur.execute('SELECT Username '
                            'FROM User '
                            'WHERE username=%s', [username])
                matchingUsername = cur.fetchone()
                cur.execute('SELECT Email '
                            'FROM User '
                            'WHERE email=%s', [email])
                matchingEmail = cur.fetchone()
                if (matchingUsername is not None):
                    return render_template('index.html', login_form=login_form, register_form=register_form,
                                           data="Username Already Registered")
                if (matchingEmail is not None):
                    return render_template('index.html', login_form=login_form, register_form=register_form,
                                           data="Email Already Registered")
                try:
                    curUser = User(username, email, password, usertype)
                    if newuser.usertype == 'VISITOR':
                        cur.execute('INSERT INTO User (Username, Email, Password, UserType) '
                                    'VALUES (%s, %s, %s, %s)',
                                    (newuser.username, newuser.email, newuser.password_hash, newuser.usertype))
                        conn.commit()
                        return redirect(url_for('visitor'))
                    if newuser.usertype == 'OWNER':
                        global newOwner
                        newOwner = True
                        return redirect(url_for('addProperty'))
                except Exception:
                    return render_template('index.html', login_form=login_form, register_form=register_form,
                                           data="Error with Registration")
            else:
                return render_template('index.html', login_form=login_form, register_form=register_form,
                                       data="Error with Registration Information")
        else:
            return render_template('index.html', login_form=login_form, register_form=register_form)
    elif not session.get('logged_in'):
        return render_template('index.html', login_form=login_form, register_form=register_form)
    else:
        return render_template('index.html', login_form=login_form, register_form=register_form)


@app.route('/visitor/')
def visitor():
    cur.execute('SELECT ID, Name, Size, IsCommercial, IsPublic, Street, City, Zip, PropertyType, COUNT(V.PropertyID), AVG(V.Rating) FROM Property P JOIN Visit V ON P.ID = V.PropertyID AND P.ApprovedBy IS NOT NULL GROUP BY V.PropertyID')
    data = list(cur.fetchall())
    return render_template('VisitorHome.html', data=data, name=curUser.username)


@app.route('/visitorVisited/')
def visitorVisited():
    global curUser
    cur.execute('SELECT Name, VisitDate, Rating, ID '
                'FROM (SELECT * FROM Property WHERE ApprovedBy IS NOT NULL) AS Property JOIN (SELECT PropertyID, VisitDate, Rating '
                'FROM Visit WHERE Username = %s) AS Visit ON ID = PropertyID', [curUser.username])
    data = list(cur.fetchall())
    return render_template('VisitorVisitedList.html', data=data, name=curUser.username)


@app.route('/visitorViewPropertyDetails/', methods=['POST'])
def visitorViewPropertyDetails():
    global curUser
    propertyID = request.form.get("propertyID")
    cur.execute('SELECT ID, Name, Size, IsCommercial, IsPublic, Street, City, Zip, PropertyType, ApprovedBy, Visits, Rating, Owner, PropertyType '
        'FROM (SELECT ID, Name, Size, IsCommercial, IsPublic, Street, City, Zip, Owner, PropertyType, ApprovedBy, COUNT(V.PropertyID) AS Visits, AVG(V.Rating) AS Rating FROM Property P LEFT JOIN Visit V ON P.ID = V.PropertyID GROUP BY V.PropertyID) AS T '
        'WHERE ID = %s', [propertyID])
    propertyInfo = cur.fetchone()
    cur.execute('SELECT Email '
                'FROM User '
                'WHERE Username = %s', [propertyInfo[12]])
    ownerEmail = cur.fetchone()
    cur.execute('SELECT ItemName '
                'FROM Has '
                'WHERE PropertyID = %s', [propertyID])
    propertyOrganisms = cur.fetchall()
    cur.execute('SELECT Rating '
                'FROM Visit '
                'WHERE Username = %s AND PropertyID = %s', [curUser.username, propertyID])
    rating = cur.fetchone()
    alreadyVisited = True
    if rating is None:
        alreadyVisited = False
    return render_template('VisitorDetailProperty.html', propertyInfo=propertyInfo, ownerEmail=ownerEmail, organisms=propertyOrganisms, alreadyVisited=alreadyVisited)


@app.route('/logVisit/', methods=['POST'])
def logVisit():
    split = request.form.get("Rating").split("-")
    rating = split[0]
    propertyID = split[1]
    cur.execute('SELECT Name '
                'FROM Property '
                'WHERE ID = %s', [propertyID])
    propertyName = cur.fetchone()
    now = datetime.now()
    currentSecond = str(now.second)
    currentMinute = str(now.minute)
    currentHour = str(now.hour)
    currentDay = str(now.day)
    currentMonth = str(now.month)
    currentYear = str(now.year)
    currentDate = currentYear + "-" + currentMonth + "-" + currentDay + " " + currentHour + ":" + currentMinute + ":" + currentSecond
    cur.execute('INSERT INTO Visit '
                'VALUES(%s, %s, %s, %s)', [curUser.username, propertyID, currentDate, rating])
    conn.commit()
    return redirect(url_for('visitorVisited'))


@app.route('/visitorUnlogVisit/', methods=['POST'])
def visitorUnlogVisit():
    propertyID = request.form.get('propertyID')
    cur.execute('DELETE FROM Visit '
                'WHERE Username = %s AND PropertyID = %s', [curUser.username, propertyID])
    conn.commit()
    return redirect(url_for('visitorVisited'))


@app.route('/visitedSortByASC/<Param>')
def visitedSortByASC(Param):
    global visitedPropertyCurrentSort
    visitedPropertyCurrentSort = Param + " ASC"
    if visitedPropertySearchType == "Name":
        searchText = "%" + visitedPropertySearchText + "%"
        cur.execute('SELECT Name, VisitDate, Rating, ID '
                    'FROM (SELECT * FROM Property WHERE ApprovedBy IS NOT NULL) AS Property JOIN (SELECT PropertyID, VisitDate, Rating '
                    'FROM Visit WHERE Username = %s) AS Visit ON ID = PropertyID '
                    'WHERE ' + visitedPropertySearchType + ' LIKE %s '
                    'ORDER BY ' + visitedPropertyCurrentSort, [curUser.username, searchText])
    else:
        minVal = 0
        maxVal = 100000
        if visitedPropertySearchType == "VisitDate":
            split = visitedPropertySearchText.split(":")
            if len(split) > 1:
                minVal = split[0]
                maxVal = split[1]
            else:
                minVal = '0000-00-00'
                maxVal = '3000-12-31'
        else:
            split = visitedPropertySearchText.split("-")
            minVal = 0
            maxVal = 1000000
            if len(split) > 1:
                minVal = min(float(split[0]), float(split[1]))
                maxVal = max(float(split[0]), float(split[1]))
        cur.execute('SELECT Name, VisitDate, Rating, ID '
                    'FROM (SELECT * FROM Property WHERE ApprovedBy IS NOT NULL) AS Property JOIN (SELECT PropertyID, VisitDate, Rating '
                    'FROM Visit WHERE Username = %s) AS Visit ON ID = PropertyID '
                    'WHERE ' + visitedPropertySearchType + ' BETWEEN %s and %s '
                                                           'ORDER BY ' + visitedPropertyCurrentSort,
                    [curUser.username, minVal, maxVal])
    data = list(cur.fetchall())
    return render_template('VisitorVisitedList.html', data=data, name=curUser.username)


@app.route('/visitedSortByDESC/<Param>')
def visitedSortByDESC(Param):
    global visitedPropertyCurrentSort
    visitedPropertyCurrentSort = Param + " DESC"
    if visitedPropertySearchType == "Name":
        searchText = "%" + visitedPropertySearchText + "%"
        cur.execute('SELECT Name, VisitDate, Rating, ID '
                    'FROM (SELECT * FROM Property WHERE ApprovedBy IS NOT NULL) AS Property JOIN (SELECT PropertyID, VisitDate, Rating '
                    'FROM Visit WHERE Username = %s) AS Visit ON ID = PropertyID '
                    'WHERE ' + visitedPropertySearchType + ' LIKE %s '
                                                           'ORDER BY ' + visitedPropertyCurrentSort,
                    [curUser.username, searchText])
    else:
        minVal = 0
        maxVal = 100000
        if visitedPropertySearchType == "VisitDate":
            split = visitedPropertySearchText.split(":")
            if len(split) > 1:
                minVal = split[0]
                maxVal = split[1]
            else:
                minVal = '0000-00-00'
                maxVal = '3000-12-31'
        else:
            split = visitedPropertySearchText.split("-")
            minVal = 0
            maxVal = 1000000
            if len(split) > 1:
                minVal = min(float(split[0]), float(split[1]))
                maxVal = max(float(split[0]), float(split[1]))
        cur.execute('SELECT Name, VisitDate, Rating, ID '
                    'FROM (SELECT * FROM Property WHERE ApprovedBy IS NOT NULL) AS Property JOIN (SELECT PropertyID, VisitDate, Rating '
                    'FROM Visit WHERE Username = %s) AS Visit ON ID = PropertyID '
                    'WHERE ' + visitedPropertySearchType + ' BETWEEN %s and %s '
                                                           'ORDER BY ' + visitedPropertyCurrentSort,
                    [curUser.username, minVal, maxVal])
    data = list(cur.fetchall())
    return render_template('VisitorVisitedList.html', data=data, name=curUser.username)


@app.route('/searchVisitedPropertyList/', methods=['POST'])
def searchVisitedPropertyList():
    global visitedPropertySearchType
    global visitedPropertySearchText
    visitedPropertySearchType = request.form.get('searchBy')
    visitedPropertySearchText = request.form.get('searchText')
    if visitedPropertySearchType == "Name":
        searchText = "%" + visitedPropertySearchText + "%"
        cur.execute('SELECT Name, VisitDate, Rating, ID '
                    'FROM (SELECT * FROM Property WHERE ApprovedBy IS NOT NULL) AS Property JOIN (SELECT PropertyID, VisitDate, Rating '
                    'FROM Visit WHERE Username = %s) AS Visit ON ID = PropertyID '
                    'WHERE ' + visitedPropertySearchType + ' LIKE %s '
                    'ORDER BY ' + visitedPropertyCurrentSort, [curUser.username, searchText])
    else:
        minVal = 0
        maxVal = 100000
        if visitedPropertySearchType == "VisitDate":
            split = visitedPropertySearchText.split(":")
            if len(split) > 1:
                minVal = split[0]
                maxVal = split[1]
            else:
                minVal = '0000-00-00'
                maxVal = '3000-12-31'
        else:
            split = visitedPropertySearchText.split("-")
            minVal = 0
            maxVal = 1000000
            if len(split) > 1:
                minVal = min(float(split[0]), float(split[1]))
                maxVal = max(float(split[0]), float(split[1]))
        cur.execute('SELECT Name, VisitDate, Rating, ID '
                    'FROM (SELECT * FROM Property WHERE ApprovedBy IS NOT NULL) AS Property JOIN (SELECT PropertyID, VisitDate, Rating '
                    'FROM Visit WHERE Username = %s) AS Visit ON ID = PropertyID '
                    'WHERE ' + visitedPropertySearchType + ' BETWEEN %s and %s '
                    'ORDER BY ' + visitedPropertyCurrentSort, [curUser.username, minVal, maxVal])
    data = cur.fetchall()
    return render_template('VisitorVisitedList.html', data=data, name=curUser.username)

@app.route('/searchVisitorPropertyList/', methods=['POST'])
def searchVisitorPropertyList():
    global visitorPropertySearchType
    global visitorPropertySearchText
    visitorPropertySearchType = request.form.get('searchBy')
    visitorPropertySearchText = request.form.get('searchText')
    if visitorPropertySearchType == "Name" or visitorPropertySearchType == "City" or visitorPropertySearchType == "PropertyType":
        searchText = "%" + visitorPropertySearchText + "%"
        cur.execute('SELECT ID, Name, Size, IsCommercial, IsPublic, Street, City, Zip, PropertyType, COALESCE(Visits, 0), COALESCE(Rating, 0) '
                    'FROM (SELECT * FROM Property WHERE ApprovedBy IS NOT NULL) AS P LEFT OUTER JOIN (SELECT PropertyID, Count(PropertyID) AS Visits, AVG(Rating) AS Rating FROM Visit GROUP BY PropertyID) AS V ON ID = PropertyID '
                    'WHERE ' + visitorPropertySearchType + ' LIKE %s '
                    'ORDER BY ' + visitorPropertyCurrentSort, [searchText])
    else:
        split = visitorPropertySearchText.split("-")
        minVal = 0
        maxVal = 1000000
        if len(split) > 1:
            minVal = min(float(split[0]), float(split[1]))
            maxVal = max(float(split[0]), float(split[1]))
        cur.execute('SELECT ID, Name, Size, IsCommercial, IsPublic, Street, City, Zip, PropertyType, COALESCE(Visits, 0), COALESCE(Rating, 0) '
                    'FROM (SELECT * FROM Property WHERE ApprovedBy IS NOT NULL) AS P LEFT OUTER JOIN (SELECT PropertyID, Count(PropertyID) AS Visits, AVG(Rating) AS Rating FROM Visit GROUP BY PropertyID) AS V ON ID = PropertyID '
                    'WHERE ' + visitorPropertySearchType + ' BETWEEN %s AND %s '
                    'ORDER BY ' + visitorPropertyCurrentSort, [minVal, maxVal])
    data = list(cur.fetchall())
    return render_template('VisitorHome.html', data=data, name=curUser.username)


@app.route('/visitorSortByASC/<Param>')
def visitorSortByASC(Param):
    global visitorPropertyCurrentSort
    visitorPropertyCurrentSort = Param + " ASC"
    if visitorPropertySearchType == "Name" or visitorPropertySearchType == "City" or visitorPropertySearchType == "PropertyType":
        searchText = "%" + visitorPropertySearchText + "%"
        cur.execute('SELECT ID, Name, Size, IsCommercial, IsPublic, Street, City, Zip, PropertyType, COALESCE(Visits, 0), COALESCE(Rating, 0) '
                    'FROM (SELECT * FROM Property WHERE ApprovedBy IS NOT NULL) AS P LEFT OUTER JOIN (SELECT PropertyID, Count(PropertyID) AS Visits, AVG(Rating) AS Rating FROM Visit GROUP BY PropertyID) AS V ON ID = PropertyID '
                    'WHERE ' + visitorPropertySearchType + ' LIKE %s '
                    'ORDER BY ' + visitorPropertyCurrentSort, [searchText])
    else:
        split = visitorPropertySearchText.split("-")
        minVal = 0
        maxVal = 1000000
        if len(split) > 1:
            minVal = min(float(split[0]), float(split[1]))
            maxVal = max(float(split[0]), float(split[1]))
        cur.execute('SELECT ID, Name, Size, IsCommercial, IsPublic, Street, City, Zip, PropertyType, COALESCE(Visits, 0), COALESCE(Rating, 0) '
                    'FROM (SELECT * FROM Property WHERE ApprovedBy IS NOT NULL) AS P LEFT OUTER JOIN (SELECT PropertyID, Count(PropertyID) AS Visits, AVG(Rating) AS Rating FROM Visit GROUP BY PropertyID) AS V ON ID = PropertyID '
                    'WHERE ' + visitorPropertySearchType + ' BETWEEN %s AND %s '
                    'ORDER BY ' + visitorPropertyCurrentSort, [minVal, maxVal])
    data = list(cur.fetchall())
    return render_template('VisitorHome.html', data=data, name=curUser.username)


@app.route('/visitorSortByDESC/<Param>')
def visitorSortByDESC(Param):
    global visitorPropertyCurrentSort
    visitorPropertyCurrentSort = Param + " DESC"
    if visitorPropertySearchType == "Name" or visitorPropertySearchType == "City" or visitorPropertySearchType == "PropertyType":
        searchText = "%" + visitorPropertySearchText + "%"
        cur.execute('SELECT ID, Name, Size, IsCommercial, IsPublic, Street, City, Zip, PropertyType, COALESCE(Visits, 0), COALESCE(Rating, 0) '
                    'FROM (SELECT * FROM Property WHERE ApprovedBy IS NOT NULL) AS P LEFT OUTER JOIN (SELECT PropertyID, Count(PropertyID) AS Visits, AVG(Rating) AS Rating FROM Visit GROUP BY PropertyID) AS V ON ID = PropertyID '
                    'WHERE ' + visitorPropertySearchType + ' LIKE %s '
                    'ORDER BY ' + visitorPropertyCurrentSort, [searchText])
    else:
        split = visitorPropertySearchText.split("-")
        minVal = 0
        maxVal = 1000000
        if len(split) > 1:
            minVal = min(float(split[0]), float(split[1]))
            maxVal = max(float(split[0]), float(split[1]))
        cur.execute('SELECT ID, Name, Size, IsCommercial, IsPublic, Street, City, Zip, PropertyType, COALESCE(Visits, 0), COALESCE(Rating, 0) '
                    'FROM (SELECT * FROM Property WHERE ApprovedBy IS NOT NULL) AS P LEFT OUTER JOIN (SELECT PropertyID, Count(PropertyID) AS Visits, AVG(Rating) AS Rating FROM Visit GROUP BY PropertyID) AS V ON ID = PropertyID '
                    'WHERE ' + visitorPropertySearchType + ' BETWEEN %s AND %s '
                    'ORDER BY ' + visitorPropertyCurrentSort, [minVal, maxVal])
    data = list(cur.fetchall())
    return render_template('VisitorHome.html', data=data, name=curUser.username)


@app.route('/owner/')
def owner():
    global newOwner
    newOwner = False
    global curUser
    cur.execute('SELECT ID, Name, Size, IsCommercial, IsPublic, Street, City, Zip, PropertyType, ApprovedBy, COALESCE (Visits, 0), COALESCE(Rating, 0) '
                'FROM (SELECT ID, Name, Size, IsCommercial, IsPublic, Street, City, Zip, Owner, PropertyType, ApprovedBy '
                'FROM Property) AS Props LEFT OUTER JOIN (SELECT PropertyID, COUNT(PropertyID) AS Visits, AVG(Rating) AS Rating FROM Visit GROUP BY PropertyID) AS Ratings ON ID = PropertyID '
                'WHERE Owner = %s '
                'ORDER BY Name', [curUser.username])
    data = list(cur.fetchall())
    return render_template('OwnerHome.html', data=data, username=curUser.username)


@app.route('/searchOwnerPropertyList/', methods=['POST'])
def searchOwnerPropertyList():
    global ownerPropertySearchType
    global ownerPropertySearchText
    ownerPropertySearchType = request.form.get('searchBy')
    ownerPropertySearchText = request.form.get('searchText')
    if ownerPropertySearchType == "Name" or ownerPropertySearchType == "City" or ownerPropertySearchType == "PropertyType":
        searchText = '%' + ownerPropertySearchText + '%'
        cur.execute('SELECT ID, Name, Size, IsCommercial, IsPublic, Street, City, Zip, PropertyType, ApprovedBy, COALESCE (Visits, 0), COALESCE(Rating, 0) '
                    'FROM (SELECT ID, Name, Size, IsCommercial, IsPublic, Street, City, Zip, Owner, PropertyType, ApprovedBy '
                    'FROM Property) AS Props LEFT OUTER JOIN (SELECT PropertyID, COUNT(PropertyID) AS Visits, AVG(Rating) AS Rating FROM Visit GROUP BY PropertyID) AS Ratings ON ID = PropertyID '
                    'WHERE Owner = %s AND ' + ownerPropertySearchType + ' LIKE %s '
                    'ORDER BY ' + ownerPropertyCurrentSort, [curUser.username, searchText])
    else:
        split = ownerPropertySearchText.split("-")
        minVal = 0
        maxVal = 1000000
        if len(split) > 1:
            minVal = min(float(split[0]), float(split[1]))
            maxVal = max(float(split[0]), float(split[1]))
        print(ownerPropertySearchType, minVal, maxVal)
        cur.execute('SELECT ID, Name, Size, IsCommercial, IsPublic, Street, City, Zip, PropertyType, ApprovedBy, COALESCE (Visits, 0), COALESCE(Rating, 0) '
                    'FROM (SELECT ID, Name, Size, IsCommercial, IsPublic, Street, City, Zip, Owner, PropertyType, ApprovedBy '
                    'FROM Property) AS Props LEFT OUTER JOIN (SELECT PropertyID, COUNT(PropertyID) AS Visits, AVG(Rating) AS Rating FROM Visit GROUP BY PropertyID) AS Ratings ON ID = PropertyID '
                    'WHERE Owner = %s AND ' + ownerPropertySearchType + ' BETWEEN %s AND %s '
                    'ORDER BY ' + ownerPropertyCurrentSort, [curUser.username, minVal, maxVal])
    data = list(cur.fetchall())
    return render_template('OwnerHome.html', data=data, username=curUser.username)


@app.route('/ownerSortByASC/<Param>')
def ownerSortByASC(Param):
    global ownerPropertyCurrentSort
    ownerPropertyCurrentSort = Param + " ASC"
    if ownerPropertySearchType == "Name" or ownerPropertySearchType == "City" or ownerPropertySearchType == "PropertyType":
        searchText = '%' + ownerPropertySearchText + '%'
        cur.execute('SELECT ID, Name, Size, IsCommercial, IsPublic, Street, City, Zip, PropertyType, ApprovedBy, COALESCE (Visits, 0), COALESCE(Rating, 0) '
                    'FROM (SELECT ID, Name, Size, IsCommercial, IsPublic, Street, City, Zip, Owner, PropertyType, ApprovedBy '
                    'FROM Property) AS Props LEFT OUTER JOIN (SELECT PropertyID, COUNT(PropertyID) AS Visits, AVG(Rating) AS Rating FROM Visit GROUP BY PropertyID) AS Ratings ON ID = PropertyID '
                    'WHERE Owner = %s AND ' + ownerPropertySearchType + ' LIKE %s '
                    'ORDER BY ' + ownerPropertyCurrentSort, [curUser.username, searchText])
    else:
        split = ownerPropertySearchText.split("-")
        minVal = 0
        maxVal = 1000000
        if len(split) > 1:
            minVal = min(float(split[0]), float(split[1]))
            maxVal = max(float(split[0]), float(split[1]))
        cur.execute('SELECT ID, Name, Size, IsCommercial, IsPublic, Street, City, Zip, PropertyType, ApprovedBy, COALESCE (Visits, 0), COALESCE(Rating, 0) '
                    'FROM (SELECT ID, Name, Size, IsCommercial, IsPublic, Street, City, Zip, Owner, PropertyType, ApprovedBy '
                    'FROM Property) AS Props LEFT OUTER JOIN (SELECT PropertyID, COUNT(PropertyID) AS Visits, AVG(Rating) AS Rating FROM Visit GROUP BY PropertyID) AS Ratings ON ID = PropertyID '
                    'WHERE Owner = %s AND ' + ownerPropertySearchType + ' BETWEEN %s AND %s '
                    'ORDER BY ' + ownerPropertyCurrentSort, [curUser.username, minVal, maxVal])
    data = list(cur.fetchall())
    return render_template('OwnerHome.html', data=data, username=curUser.username)


@app.route('/ownerSortByDESC/<Param>')
def ownerSortByDESC(Param):
    global ownerPropertyCurrentSort
    ownerPropertyCurrentSort = Param + " DESC"
    if ownerPropertySearchType == "Name" or ownerPropertySearchType == "City" or ownerPropertySearchType == "PropertyType":
        searchText = '%' + ownerPropertySearchText + '%'
        cur.execute('SELECT ID, Name, Size, IsCommercial, IsPublic, Street, City, Zip, PropertyType, ApprovedBy, COALESCE (Visits, 0), COALESCE(Rating, 0) '
                    'FROM (SELECT ID, Name, Size, IsCommercial, IsPublic, Street, City, Zip, Owner, PropertyType, ApprovedBy '
                    'FROM Property) AS Props LEFT OUTER JOIN (SELECT PropertyID, COUNT(PropertyID) AS Visits, AVG(Rating) AS Rating FROM Visit GROUP BY PropertyID) AS Ratings ON ID = PropertyID '
                    'WHERE Owner = %s AND ' + ownerPropertySearchType + ' LIKE %s '
                    'ORDER BY ' + ownerPropertyCurrentSort, [curUser.username, searchText])
    else:
        split = ownerPropertySearchText.split("-")
        minVal = 0
        maxVal = 1000000
        if len(split) > 1:
            minVal = min(float(split[0]), float(split[1]))
            maxVal = max(float(split[0]), float(split[1]))
        cur.execute('SELECT ID, Name, Size, IsCommercial, IsPublic, Street, City, Zip, PropertyType, ApprovedBy, COALESCE (Visits, 0), COALESCE(Rating, 0) '
                    'FROM (SELECT ID, Name, Size, IsCommercial, IsPublic, Street, City, Zip, Owner, PropertyType, ApprovedBy '
                    'FROM Property) AS Props LEFT OUTER JOIN (SELECT PropertyID, COUNT(PropertyID) AS Visits, AVG(Rating) AS Rating FROM Visit GROUP BY PropertyID) AS Ratings ON ID = PropertyID '
                    'WHERE Owner = %s AND ' + ownerPropertySearchType + ' BETWEEN %s AND %s '
                    'ORDER BY ' + ownerPropertyCurrentSort, [curUser.username, minVal, maxVal])
    data = list(cur.fetchall())
    return render_template('OwnerHome.html', data=data, username=curUser.username)


@app.route('/ownerManageProperties/', methods=['GET', 'POST'])
def ownerManageProperties():
    owner = curUser.username
    cur.execute('SELECT Name, Street, City, Zip, Size, PropertyType,'
                'IsPublic, IsCommercial, ID, ApprovedBy FROM Property WHERE Owner=%s', [owner])
    properties = cur.fetchall()
    dicts = []
    print(properties, file=sys.stderr)
    for row in properties:
        dict = {}
        dict['Name'] = row[0]
        dict['Street'] = row[1]
        dict['City'] = row[2]
        dict['Zip'] = row[3]
        dict['Size'] = row[4]
        dict['PropertyType'] = row[5]
        dict['IsPublic'] = 'Yes' if row[6] == 1 else 'No'
        dict['IsCommercial'] = 'Yes' if row[7] == 1 else 'No'
        dict['ID'] = row[8]
        dict['ApprovedBy'] = 'Yes' if row[9] is not None else 'No'
        dicts.append(dict)
    table = PropertyTable(dicts)
    return render_template('OwnerManageProperties.html', table=table, owner='Your')

# owner manage property
@app.route('/manageproperty/<id>', methods=['GET', 'POST'])
def manageProperty(id):
    form = ManagePropertyForm()
    errors = []
    modified = 0

    # current Property and Has to check if property has been modified at the end
    cur.execute('SELECT Name, Size, IsCommercial, IsPublic, Street, City, Zip, PropertyType FROM Property WHERE ID=%s', [id])
    currProperty = cur.fetchall()
    cur.execute('SELECT * FROM Has WHERE PropertyID=%s', [id])
    currHas = cur.fetchall()

    # current items
    cur.execute('SELECT ItemName FROM Has WHERE PropertyID=%s', [id])
    raw = cur.fetchall()
    currItems = []
    for row in raw:
        currItems.append(row[0])

    # current attributes
    cur.execute('SELECT Name, Street, City, Zip, Size, PropertyType,'
                'IsPublic, IsCommercial, ID, ApprovedBy FROM Property WHERE ID=%s', [id])
    data = cur.fetchall()[0]
    propertyName = data[0]
    propertyType = data[5]
    streetAddress = data[1]
    city = data[2]
    zip = data[3]
    acres = data[4]
    public = data[6]
    commercial = data[7]

    # pre-populate form fields
    form.propertyName.description = propertyName
    form.streetAddress.description = streetAddress
    form.city.description = city
    form.zip.description = zip
    form.acres.description = acres
    form.public.description = 'YES' if public == 1 else 'NO'
    form.commercial.description = 'YES' if commercial == 1 else 'NO'

    # retrieve items not already owned by the property
    cur.execute('SELECT Name FROM FarmItem WHERE Type=%s AND IsApproved=1 '
                'AND Name NOT IN (SELECT ItemName FROM Has WHERE PropertyID=%s)', ['ANIMAL', id])
    animals = cur.fetchall()
    cur.execute('SELECT Name FROM FarmItem WHERE Type=%s AND IsApproved=1 '
                'AND Name NOT IN (SELECT ItemName FROM Has WHERE PropertyID=%s)', ['FRUIT', id])
    fruits = cur.fetchall()
    cur.execute('SELECT Name FROM FarmItem WHERE Type=%s AND IsApproved=1 '
                'AND Name NOT IN (SELECT ItemName FROM Has WHERE PropertyID=%s)', ['VEGETABLE', id])
    vegetables = cur.fetchall()
    cur.execute('SELECT Name FROM FarmItem WHERE Type=%s AND IsApproved=1 '
                'AND Name NOT IN (SELECT ItemName FROM Has WHERE PropertyID=%s)', ['NUT', id])
    nuts = cur.fetchall()
    cur.execute('SELECT Name FROM FarmItem WHERE Type=%s AND IsApproved=1 '
                'AND Name NOT IN (SELECT ItemName FROM Has WHERE PropertyID=%s)', ['FLOWER', id])
    flowers = cur.fetchall()
    crops = fruits + vegetables + nuts + flowers

    # populate add item SelectFields
    form.animal.choices = [('-', '-')] + [(row[0], row[0]) for row in animals]
    form.crop.choices = [('-', '-')] + [(row[0], row[0]) for row in crops]
    form.vegetable.choices = [('-', '-')] + [(row[0], row[0]) for row in vegetables]
    form.flower.choices = [('-', '-')] + [(row[0], row[0]) for row in flowers]
    form.fruit.choices = [('-', '-')] + [(row[0], row[0]) for row in fruits]
    form.nut.choices = [('-', '-')] + [(row[0], row[0]) for row in nuts]

    # populate request type SelectField
    requestTypes = [('-', '-')]
    if propertyType == 'FARM':
        requestTypes.extend([('ANIMAL', 'Animal'), ('FLOWER', 'Flower'),
                             ('VEGETABLE', 'Vegetable'), ('FRUIT', 'Fruit'), ('NUT', 'Nut')])
    elif propertyType == 'GARDEN':
        requestTypes.extend([('FLOWER', 'Flower'), ('VEGETABLE', 'Vegetable')])
    else:
        requestTypes.extend([('FRUIT', 'Fruit'), ('NUT', 'Nut')])
    form.requestType.choices = requestTypes

    # populate delete item SelectField
    deleteNames = [('-', '-')]
    types = {}
    if (propertyType == 'FARM'):
        types['ANIMAL'] = []
        types['CROP'] = []
        for item in currItems:
            cur.execute('SELECT Type FROM FarmItem WHERE Name=%s', [item])
            type = cur.fetchall()[0][0]
            if type == 'ANIMAL':
                types['ANIMAL'].append(item)
            else:
                types['CROP'].append(item)
    else:
        for item in currItems:
            cur.execute('SELECT Type FROM FarmItem WHERE Name=%s', [item])
            type = cur.fetchall()[0][0]
            if type not in types:
                types[type] = []
            types[type].append(item)
    for type in types:
        if len(types[type]) > 1:
            for item in types[type]:
                deleteNames.append((item, item))
    form.deleteName.choices = deleteNames

    if form.validate_on_submit():
        # retrieve edit attributes form data
        propertyName = form.propertyName.data if form.propertyName.data != '' else propertyName
        streetAddress = form.streetAddress.data if form.streetAddress.data != '' else streetAddress
        city = form.city.data if form.city.data != '' else city
        zip = form.zip.data if form.zip.data != '' else zip
        acres = form.acres.data if form.acres.data != '' else acres
        if form.public.data == 'YES':
            public = 1
        elif form.public.data == 'NO':
            public = 0
        if form.commercial.data == 'YES':
            commercial = 1
        elif form.commercial.data == 'NO':
            commercial = 0

        # obtain add item SelectField values based on property type
        if propertyType == 'FARM':
            item1 = form.animal.data
            item2 = form.crop.data
        elif propertyType == 'GARDEN':
            item1 = form.flower.data
            item2 = form.vegetable.data
        else:
            item1 = form.fruit.data
            item2 = form.nut.data

        # retrieve request approval form data
        requestName = form.requestName.data
        requestType = form.requestType.data

        # retrieve delete item form data
        deleteName = form.deleteName.data

        # retrieve delete property form data
        deletePropery = form.deleteProperty.data

        # check new name does not already exist
        if propertyName != '' and propertyName != data[0]:
            cur.execute('SELECT Name FROM Property')
            raw = cur.fetchall()
            for row in raw:
                if row[0].lower() == propertyName.lower():
                    errors.append(propertyNameExists)
            if propertyNameExists not in errors:
                try:
                    # update property name
                    cur.execute(
                        'UPDATE Property SET Name=%s WHERE ID=%s', [propertyName, id])
                    conn.commit()
                    print('edit property name success', file=sys.stderr)
                except Exception as e:
                    print('edit property name failure', file=sys.stderr)
                    print(e, file=sys.stderr)

        # update other attributes
        try:
            cur.execute(
                'UPDATE Property SET Size=%s, IsCommercial=%s,'
                'IsPublic=%s, Street=%s, City=%s, Zip=%s WHERE ID=%s',
                [acres, commercial, public, streetAddress, city, zip, id])
            conn.commit()
            print('edit other attributes success', file=sys.stderr)
        except Exception as e:
            print('edit other attributes failure', file=sys.stderr)
            print(e, file=sys.stderr)

        # update Has table
        if item1 != '-':
            try:
                cur.execute('INSERT INTO Has(PropertyID, ItemName) VALUES(%s, %s)', (id, item1))
                conn.commit()
                print('item1 add to Has success', file=sys.stderr)
            except Exception as e:
                print('item1 add to Has failure', file=sys.stderr)
                print(e, file=sys.stderr)
        if item2 != '-':
            try:
                cur.execute('INSERT INTO Has(PropertyID, ItemName) VALUES(%s, %s)', (id, item2))
                conn.commit()
                print('item2 add to Has success', file=sys.stderr)
            except Exception as e:
                print('item2 add to Has failure', file=sys.stderr)
                print(e, file=sys.stderr)

        # request approval
        if requestName != '' and requestType != '-':
            try:
                cur.execute('INSERT INTO FarmItem(Name, Type) VALUES(%s, %s)', (requestName, requestType))
                conn.commit()
                print('request approval success', file=sys.stderr)
            except Exception as e:
                print('request approval failure', file=sys.stderr)
                print(e, file=sys.stderr)

        # delete item
        if deleteName != '-':
            try:
                cur.execute('DELETE FROM Has WHERE PropertyID=%s AND ItemName=%s', [id, deleteName])
                conn.commit()
                print('delete item success', file=sys.stderr)
            except Exception as e:
                print('delete item failure', file=sys.stderr)
                print(e, file=sys.stderr)

        # visits = 0 and approvedBy = NULL if property is modified
        cur.execute('SELECT Name, Size, IsCommercial, IsPublic, Street, City, Zip, PropertyType FROM Property WHERE ID=%s', [id])
        newProperty = cur.fetchall()
        cur.execute('SELECT * FROM Has WHERE PropertyID=%s', [id])
        newHas = cur.fetchall()
        print(currProperty, file=sys.stderr)
        print(newProperty, file=sys.stderr)
        if newProperty != currProperty or newHas != currHas:
            try:
                cur.execute('DELETE FROM Visit WHERE PropertyID = %s', [id])
                cur.execute('UPDATE Property SET ApprovedBy=NULL WHERE ID=%s', [id])
                conn.commit()
                print('reset visits success', file=sys.stderr)
                print('reset approvedby success', file=sys.stderr)
            except Exception as e:
                print('reset visits failure', file=sys.stderr)
                print('reset approvedby failure', file=sys.stderr)
                print(e, file=sys.stderr)

        # delete property
        if deletePropery == 'YES':
            try:
                cur.execute('DELETE FROM Property WHERE ID=%s', [id])
                conn.commit()
                print('delete property success', file=sys.stderr)
                return redirect(url_for('ownerManageProperties'))
            except Exception as e:
                print('delete property failure', file=sys.stderr)
                print(e, file=sys.stderr)

        print('manage property total success', file=sys.stderr)
        return redirect(url_for('manageProperty', id=id))
    else:
          print('form not submitted', file=sys.stderr)
    if form.errors:
        print(form.errors, file=sys.stderr)
    return render_template('ManageProperty.html', form=form, propertyType=propertyType, currItems=currItems, id=id)

# owner add property
@app.route('/addproperty/', methods=['GET', 'POST'])
def addProperty():
    global newOwner
    owner = curUser.username
    print(owner)
    form = AddPropertyForm()
    errors = []

    # new owners shouldn't be able to cancel from the add new property screen
    haveCancelButton = True
    if newOwner:
        haveCancelButton = False

    # retrieve all items
    cur.execute('SELECT Name FROM FarmItem WHERE Type=%s AND IsApproved=1', ['ANIMAL'])
    animals = cur.fetchall()
    cur.execute('SELECT Name FROM FarmItem WHERE Type=%s AND IsApproved=1', ['FRUIT'])
    fruits = cur.fetchall()
    cur.execute('SELECT Name FROM FarmItem WHERE Type=%s AND IsApproved=1', ['VEGETABLE'])
    vegetables = cur.fetchall()
    cur.execute('SELECT Name FROM FarmItem WHERE Type=%s AND IsApproved=1', ['NUT'])
    nuts = cur.fetchall()
    cur.execute('SELECT Name FROM FarmItem WHERE Type=%s AND IsApproved=1', ['FLOWER'])
    flowers = cur.fetchall()
    crops = fruits + vegetables + nuts + flowers

    # populate SelectFields
    form.animal.choices = [(row[0], row[0]) for row in animals]
    form.crop.choices = [(row[0], row[0]) for row in crops]
    form.vegetable.choices = [('-', '-')] + [(row[0], row[0]) for row in vegetables]
    form.flower.choices = [('-', '-')] + [(row[0], row[0]) for row in flowers]
    form.fruit.choices = [('-', '-')] + [(row[0], row[0]) for row in fruits]
    form.nut.choices = [('-', '-')] + [(row[0], row[0]) for row in nuts]

    if form.validate_on_submit():
        # retrieve form data
        print('form valid', file=sys.stderr)
        propertyName = form.propertyName.data
        streetAddress = form.streetAddress.data
        city = form.city.data
        zip = form.zip.data
        acres = form.acres.data
        public = 1 if form.public.data == 'YES' else 0
        commercial = 1 if form.commercial.data == 'YES' else 0
        propertyType = form.propertyType.data

        # obtain SelectField values based on property type
        if propertyType == 'FARM':
            item1 = form.animal.data
            item2 = form.crop.data
        elif propertyType == 'GARDEN':
            item1 = form.flower.data
            item2 = form.vegetable.data
            if item1 == '-' and item2 == '-':
                errors.append('Must add at least 1 item')
        else:
            item1 = form.fruit.data
            item2 = form.nut.data
            if item1 == '-' and item2 == '-':
                errors.append('Must add at least 1 item')

        # generate id
        cur.execute('SELECT MAX(ID) FROM Property')
        id = cur.fetchall()[0][0]
        id += 1

        # check name does not already exist
        cur.execute('SELECT Name FROM Property')
        raw = cur.fetchall()
        for row in raw:
            if row[0].lower() == propertyName.lower():
                errors.append(propertyNameExists)
        if not errors:
            # add property
            try:
                if newOwner:
                    cur.execute('INSERT INTO User (Username, Email, Password, UserType) '
                                'VALUES (%s, %s, %s, %s)',
                                (curUser.username, curUser.email, curUser.password_hash, curUser.usertype))
                    conn.commit()
                cur.execute(
                    'INSERT INTO Property(ID, Name, Size, IsCommercial, IsPublic, Street, City, Zip, PropertyType, Owner)'
                    'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                    (id, propertyName, acres, commercial, public, streetAddress, city, zip, propertyType, owner))
                conn.commit()
                newOwner = False
                print('add property success', file=sys.stderr)
            except Exception as e:
                print('add property failure', file=sys.stderr)
                print(e, file=sys.stderr)
                errors.append('Database error')
                return render_template('AddProperty.html', form=form, errors=errors, cancelButton=haveCancelButton)
            # insert into Has table
            try:
                if item1 != '-':
                    cur.execute('INSERT INTO Has(PropertyID, ItemName) VALUES(%s, %s)', (id, item1))
                if item2 != '-':
                    cur.execute('INSERT INTO Has(PropertyID, ItemName) VALUES(%s, %s)', (id, item2))
                conn.commit()
                print('add to Has success', file=sys.stderr)
            except Exception as e:
                print('add to Has failure', file=sys.stderr)
                print(e, file=sys.stderr)
                errors.append('Database error')
                return render_template('AddProperty.html', form=form, errors=errors, cancelButton=haveCancelButton)
            print('add property total success', file=sys.stderr)
            return redirect(url_for('ownerManageProperties'))
        else:
            return render_template('AddProperty.html', form=form, errors=errors, cancelButton=haveCancelButton)
    else:
        errors.append("All fields must be filled out")
        print('form not submitted', file=sys.stderr)
        return render_template('AddProperty.html', form=form, errors=errors, cancelButton=haveCancelButton)
    if form.errors:
        print(form.errors, file=sys.stderr)
    return render_template('AddProperty.html', form=form, cancelButton=haveCancelButton)


@app.route('/ownerOther')
def ownerOther():
    global curUser
    cur.execute('SELECT ID, Name, Size, IsCommercial, IsPublic, Street, City, Zip, PropertyType, ApprovedBy, COALESCE(Visits, 0), COALESCE(Rating, 0) '
                'FROM (SELECT ID, Name, Size, IsCommercial, IsPublic, Street, City, Zip, Owner, PropertyType, ApprovedBy, COUNT(V.PropertyID) AS Visits, AVG(V.Rating) AS Rating FROM Property P LEFT JOIN Visit V ON P.ID = V.PropertyID GROUP BY V.PropertyID) AS T '
                'WHERE Owner != %s AND ApprovedBy IS NOT NULL '
                'ORDER BY Name', [curUser.username])
    data = list(cur.fetchall())
    return render_template('OwnerOtherProperties.html', data=data)

@app.route('/ownerOtherSortByASC/<Param>')
def ownerOtherSortByASC(Param):
    global ownerOtherPropertyCurrentSort
    global ownerOtherPropertySearchText
    ownerOtherPropertyCurrentSort = Param + " ASC"
    if ownerOtherPropertySearchType == "Name" or ownerOtherPropertySearchType == "City" or ownerOtherPropertySearchType == "IsPublic":
        if ownerOtherPropertySearchType == "IsPublic":
            if ownerOtherPropertySearchText.lower() == "false":
                ownerOtherPropertySearchText = "0"
            else:
                ownerOtherPropertySearchText = "1"
        searchText = "%" + ownerOtherPropertySearchText + "%"
        cur.execute('SELECT ID, Name, Size, IsCommercial, IsPublic, Street, City, Zip, PropertyType, ApprovedBy, COALESCE(Visits, 0), COALESCE(Rating, 0) '
                    'FROM (SELECT ID, Name, Size, IsCommercial, IsPublic, Street, City, Zip, Owner, PropertyType, ApprovedBy, COUNT(V.PropertyID) AS Visits, AVG(V.Rating) AS Rating FROM Property P LEFT JOIN Visit V ON P.ID = V.PropertyID GROUP BY V.PropertyID) AS T '
                    'WHERE Owner != %s AND ApprovedBy IS NOT NULL AND ' + ownerOtherPropertySearchType + ' LIKE %s '
                    'ORDER BY ' + ownerOtherPropertyCurrentSort, [curUser.username, searchText])
    else:
        split = ownerOtherPropertySearchText.split("-")
        minVal = 0
        maxVal = 1000000
        if len(split) > 1:
            minVal = min(float(split[0]), float(split[1]))
            maxVal = max(float(split[0]), float(split[1]))
        cur.execute(
            'SELECT ID, Name, Size, IsCommercial, IsPublic, Street, City, Zip, PropertyType, ApprovedBy, COALESCE(Visits, 0), COALESCE(Rating, 0) '
            'FROM (SELECT ID, Name, Size, IsCommercial, IsPublic, Street, City, Zip, Owner, PropertyType, ApprovedBy, COUNT(V.PropertyID) AS Visits, AVG(V.Rating) AS Rating FROM Property P LEFT JOIN Visit V ON P.ID = V.PropertyID GROUP BY V.PropertyID) AS T '
            'WHERE Owner != %s AND ApprovedBy IS NOT NULL AND ' + ownerOtherPropertySearchType + ' BETWEEN %s AND %s '
            'ORDER BY ' + ownerOtherPropertyCurrentSort, [curUser.username, minVal, maxVal])
    data = list(cur.fetchall())
    return render_template('OwnerOtherProperties.html', data=data)

@app.route('/ownerOtherSortByDESC/<Param>')
def ownerOtherSortByDESC(Param):
    global ownerOtherPropertyCurrentSort
    global ownerOtherPropertySearchText
    ownerOtherPropertyCurrentSort = Param + " DESC"
    if ownerOtherPropertySearchType == "Name" or ownerOtherPropertySearchType == "City" or ownerOtherPropertySearchType == "IsPublic":
        if ownerOtherPropertySearchType == "IsPublic":
            if ownerOtherPropertySearchText.lower() == "false":
                ownerOtherPropertySearchText = "0"
            else:
                ownerOtherPropertySearchText = "1"
        searchText = "%" + ownerOtherPropertySearchText + "%"
        cur.execute('SELECT ID, Name, Size, IsCommercial, IsPublic, Street, City, Zip, PropertyType, ApprovedBy, COALESCE(Visits, 0), COALESCE(Rating, 0) '
                    'FROM (SELECT ID, Name, Size, IsCommercial, IsPublic, Street, City, Zip, Owner, PropertyType, ApprovedBy, COUNT(V.PropertyID) AS Visits, AVG(V.Rating) AS Rating FROM Property P LEFT JOIN Visit V ON P.ID = V.PropertyID GROUP BY V.PropertyID) AS T '
                    'WHERE Owner != %s AND ApprovedBy IS NOT NULL AND ' + ownerOtherPropertySearchType + ' LIKE %s '
                    'ORDER BY ' + ownerOtherPropertyCurrentSort, [curUser.username, searchText])
    else:
        split = ownerOtherPropertySearchText.split("-")
        minVal = 0
        maxVal = 1000000
        if len(split) > 1:
            minVal = min(float(split[0]), float(split[1]))
            maxVal = max(float(split[0]), float(split[1]))
        cur.execute(
            'SELECT ID, Name, Size, IsCommercial, IsPublic, Street, City, Zip, PropertyType, ApprovedBy, COALESCE(Visits, 0), COALESCE(Rating, 0) '
            'FROM (SELECT ID, Name, Size, IsCommercial, IsPublic, Street, City, Zip, Owner, PropertyType, ApprovedBy, COUNT(V.PropertyID) AS Visits, AVG(V.Rating) AS Rating FROM Property P LEFT JOIN Visit V ON P.ID = V.PropertyID GROUP BY V.PropertyID) AS T '
            'WHERE Owner != %s AND ApprovedBy IS NOT NULL AND ' + ownerOtherPropertySearchType + ' BETWEEN %s AND %s '
            'ORDER BY ' + ownerOtherPropertyCurrentSort, [curUser.username, minVal, maxVal])
    data = list(cur.fetchall())
    return render_template('OwnerOtherProperties.html', data=data)

@app.route('/searchOwnerOtherPropertyList/', methods=['POST'])
def searchOwnerOtherPropertyList():
    global ownerOtherPropertySearchType
    global ownerOtherPropertySearchText
    ownerOtherPropertySearchType = request.form.get('searchBy')
    ownerOtherPropertySearchText = request.form.get('searchText')
    if ownerOtherPropertySearchType == "Name" or ownerOtherPropertySearchType == "City" or ownerOtherPropertySearchType == "IsPublic":
        if ownerOtherPropertySearchType == "IsPublic":
            if ownerOtherPropertySearchText.lower() == "false":
                ownerOtherPropertySearchText = "0"
            else:
                ownerOtherPropertySearchText = "1"
        searchText = "%" + ownerOtherPropertySearchText + "%"
        cur.execute('SELECT ID, Name, Size, IsCommercial, IsPublic, Street, City, Zip, PropertyType, ApprovedBy, COALESCE(Visits, 0), COALESCE(Rating, 0) '
                    'FROM (SELECT ID, Name, Size, IsCommercial, IsPublic, Street, City, Zip, Owner, PropertyType, ApprovedBy, COUNT(V.PropertyID) AS Visits, AVG(V.Rating) AS Rating FROM Property P LEFT JOIN Visit V ON P.ID = V.PropertyID GROUP BY V.PropertyID) AS T '
                    'WHERE Owner != %s AND ApprovedBy IS NOT NULL AND ' + ownerOtherPropertySearchType + ' LIKE %s '
                    'ORDER BY ' + ownerOtherPropertyCurrentSort, [curUser.username, searchText])
    else:
        split = ownerOtherPropertySearchText.split("-")
        minVal = 0
        maxVal = 1000000
        if len(split) > 1:
            minVal = min(float(split[0]), float(split[1]))
            maxVal = max(float(split[0]), float(split[1]))
        cur.execute(
            'SELECT ID, Name, Size, IsCommercial, IsPublic, Street, City, Zip, PropertyType, ApprovedBy, COALESCE(Visits, 0), COALESCE(Rating, 0) '
            'FROM (SELECT ID, Name, Size, IsCommercial, IsPublic, Street, City, Zip, Owner, PropertyType, ApprovedBy, COUNT(V.PropertyID) AS Visits, AVG(V.Rating) AS Rating FROM Property P LEFT JOIN Visit V ON P.ID = V.PropertyID GROUP BY V.PropertyID) AS T '
            'WHERE Owner != %s AND ApprovedBy IS NOT NULL AND ' + ownerOtherPropertySearchType + ' BETWEEN %s AND %s '
            'ORDER BY ' + ownerOtherPropertyCurrentSort, [curUser.username, minVal, maxVal])
    data = list(cur.fetchall())
    return render_template('OwnerOtherProperties.html', data=data)


@app.route('/detailedViewOtherProperty/', methods=['POST'])
def detailedViewOtherProperty():
    propertyID = request.form.get("otherPropertyID")
    cur.execute('SELECT ID, Name, Size, IsCommercial, IsPublic, Street, City, Zip, PropertyType, ApprovedBy, Visits, Rating, Owner, PropertyType '
        'FROM (SELECT ID, Name, Size, IsCommercial, IsPublic, Street, City, Zip, Owner, PropertyType, ApprovedBy, COUNT(V.PropertyID) AS Visits, AVG(V.Rating) AS Rating FROM Property P LEFT JOIN Visit V ON P.ID = V.PropertyID GROUP BY V.PropertyID) AS T '
        'WHERE ID = %s', [propertyID])
    propertyInfo = cur.fetchone()
    cur.execute('SELECT Email '
                'FROM User '
                'WHERE Username = %s', [propertyInfo[12]])
    ownerEmail = cur.fetchone()
    cur.execute('SELECT ItemName '
                'FROM Has '
                'WHERE PropertyID = %s', [propertyID])
    propertyOrganisms = cur.fetchall()
    return render_template('OwnerOtherDetailedView.html', propertyInfo=propertyInfo, organisms=propertyOrganisms, ownerEmail=ownerEmail)


@app.route('/ownerDeleteOwnProperty/', methods=['POST'])
def ownerDeleteOwnProperty():
    propertyID = request.form.get('property_to_delete')
    cur.execute('DELETE FROM Property '
                'WHERE ID = %s', [propertyID])
    conn.commit()
    return redirect(url_for('owner'))


@app.route('/admin/')
def admin():
    return render_template('AdminHome.html')


@app.route('/adminVisitorList/')
def adminVisitorsList():
    cur.execute('SELECT Username, Email, COALESCE(Visits, 0) AS "Logged Visits" '
                'FROM (SELECT Username, Email FROM User WHERE UserType = "VISITOR") '
                    'AS Visitors LEFT OUTER JOIN (SELECT Username AS U2, COUNT(Username) AS Visits '
                    'FROM Visit '
                    'GROUP BY Username) AS Visits ON Username = U2 '
                'ORDER BY Username ASC')
    allVisitors = cur.fetchall();
    return render_template('AdminVisitorsList.html', data=allVisitors)


@app.route('/adminSortVisitorsASC/<Param>')
def adminSortVisitorsASC(Param):
    global adminVisitorCurrentSort
    adminVisitorCurrentSort = Param + " ASC"
    if adminVisitorSearchType == "Username" or adminVisitorSearchType == "Email":
        searchText = "%" + adminVisitorSearchText + "%"
        cur.execute('SELECT Username, Email, COALESCE(Visits, 0) AS "Logged Visits" '
                    'FROM (SELECT Username, Email FROM User WHERE UserType = "VISITOR") '
                    'AS Visitors LEFT OUTER JOIN (SELECT Username AS U2, COUNT(Username) AS Visits FROM Visit '
                    'GROUP BY Username) AS Visits ON Username = U2 '
                    'WHERE ' + adminVisitorSearchType + ' LIKE %s '
                    'ORDER BY ' + adminVisitorCurrentSort, [searchText])
    else:
        searchText = adminVisitorSearchText.split("-")
        if searchText[0] == "":
            searchText = [0, 1000000]
        minVisits = min(float(searchText[0]), float(searchText[1]))
        maxVisits = max(float(searchText[0]), float(searchText[1]))
        cur.execute('SELECT Username, Email, COALESCE(Visits, 0) AS "Logged Visits" '
                    'FROM ((SELECT Username, Email FROM User WHERE UserType = "VISITOR") '
                    'AS Visitors LEFT OUTER JOIN (SELECT Username AS U2, COUNT(Username) AS Visits FROM Visit '
                    'GROUP BY Username) AS Visits ON Username = U2) '
                    'WHERE COALESCE(Visits, 0) BETWEEN %s AND %s '
                    'ORDER BY ' + adminVisitorCurrentSort, [minVisits, maxVisits])
    allVisitors = cur.fetchall()
    return render_template('AdminVisitorsList.html', data=allVisitors)


@app.route('/adminSortVisitorsDESC/<Param>')
def adminSortVisitorsDESC(Param):
    global adminVisitorCurrentSort
    adminVisitorCurrentSort = Param + " DESC"
    if adminVisitorSearchType == "Username" or adminVisitorSearchType == "Email":
        searchText = "%" + adminVisitorSearchText + "%"
        cur.execute('SELECT Username, Email, COALESCE(Visits, 0) AS "Logged Visits" '
                    'FROM (SELECT Username, Email FROM User WHERE UserType = "VISITOR") '
                    'AS Visitors LEFT OUTER JOIN (SELECT Username AS U2, COUNT(Username) AS Visits FROM Visit '
                    'GROUP BY Username) AS Visits ON Username = U2 '
                    'WHERE ' + adminVisitorSearchType + ' LIKE %s '
                    'ORDER BY ' + adminVisitorCurrentSort, [searchText])
    else:
        searchText = adminVisitorSearchText.split("-")
        if searchText[0] == "":
            searchText = [0, 1000000]
        minVisits = min(float(searchText[0]), float(searchText[1]))
        maxVisits = max(float(searchText[0]), float(searchText[1]))
        cur.execute('SELECT Username, Email, COALESCE(Visits, 0) AS "Logged Visits" '
                    'FROM ((SELECT Username, Email FROM User WHERE UserType = "VISITOR") '
                    'AS Visitors LEFT OUTER JOIN (SELECT Username AS U2, COUNT(Username) AS Visits FROM Visit '
                    'GROUP BY Username) AS Visits ON Username = U2) '
                    'WHERE COALESCE(Visits, 0) BETWEEN %s AND %s '
                    'ORDER BY ' + adminVisitorCurrentSort, [minVisits, maxVisits])
    allVisitors = cur.fetchall()
    return render_template('AdminVisitorsList.html', data=allVisitors)


@app.route('/searchVisitorsAdminVisitorList/', methods=['POST'])
def searchVisitorsAdminVisitorList():
    global adminVisitorSearchType
    global adminVisitorSearchText
    adminVisitorSearchType = request.form.get('search_by')
    adminVisitorSearchText = request.form.get('search_text')
    if adminVisitorSearchType == "Username" or adminVisitorSearchType == "Email":
        searchText = "%" + adminVisitorSearchText + "%"
        cur.execute('SELECT Username, Email, COALESCE(Visits, 0) AS "Logged Visits" '
                    'FROM (SELECT Username, Email FROM User WHERE UserType = "VISITOR") '
                        'AS Visitors LEFT OUTER JOIN (SELECT Username AS U2, COUNT(Username) AS Visits FROM Visit '
                        'GROUP BY Username) AS Visits ON Username = U2 '
                    'WHERE ' + adminVisitorSearchType + ' LIKE %s '
                    'ORDER BY ' + adminVisitorCurrentSort, [searchText])
    else:
        searchText = adminVisitorSearchText.split("-")
        if searchText[0] == "":
            searchText = [0, 1000000]
        minVisits = min(float(searchText[0]), float(searchText[1]))
        maxVisits = max(float(searchText[0]), float(searchText[1]))
        cur.execute('SELECT Username, Email, COALESCE(Visits, 0) AS "Logged Visits" '
                    'FROM ((SELECT Username, Email FROM User WHERE UserType = "VISITOR") '
                        'AS Visitors LEFT OUTER JOIN (SELECT Username AS U2, COUNT(Username) AS Visits FROM Visit '
                        'GROUP BY Username) AS Visits ON Username = U2) '
                    'WHERE COALESCE(Visits, 0) >= %s AND COALESCE(Visits, 0) <= %s '
                    'ORDER BY ' + adminVisitorCurrentSort, [minVisits, maxVisits])
    filteredVisitors = cur.fetchall()
    return render_template('AdminVisitorsList.html', data=filteredVisitors)


@app.route('/deleteVisitor/', methods=['POST'])
def deleteVisitor():
    visitorUsername = request.form.get('visitor_to_delete')
    cur.execute('DELETE FROM User WHERE Username = %s', [visitorUsername])
    conn.commit()
    cur.execute('DELETE FROM Visit WHERE Username = %s', [visitorUsername])  #Shouldn't need this but included anyway
    conn.commit()
    cur.execute('SELECT Username, Email, COALESCE(Visits, 0) AS "Logged Visits" '
                'FROM (SELECT Username, Email FROM User WHERE UserType = "VISITOR") '
                    'AS Visitors LEFT OUTER JOIN (SELECT Username AS U2, COUNT(Username) AS Visits FROM Visit '
                    'GROUP BY Username) AS Visits ON Username = U2 '
                'ORDER BY ' + adminVisitorCurrentSort)
    newVisitorList = cur.fetchall()
    return render_template('AdminVisitorsList.html', data=newVisitorList)


@app.route('/deleteVisitorVisits/', methods=['POST'])
def deleteVisitorVisits():
    visitorUsername = request.form.get('visitor_visits_to_delete')
    cur.execute('DELETE FROM Visit WHERE Username = %s', [visitorUsername])
    conn.commit()
    cur.execute(
        'SELECT Username, Email, COALESCE(Visits, 0) AS "Logged Visits" '
        'FROM (SELECT Username, Email FROM User WHERE UserType = "VISITOR") '
            'AS Visitors LEFT OUTER JOIN (SELECT Username AS U2, COUNT(Username) AS Visits FROM Visit '
            'GROUP BY Username) AS Visits ON Username = U2 '
        'ORDER BY ' + adminVisitorCurrentSort)
    newVisitorInfo = cur.fetchall()
    return render_template('AdminVisitorsList.html', data=newVisitorInfo)


@app.route('/adminOwnersList/')
def adminOwnersList():
    cur.execute('SELECT Username, Email, COALESCE(Properties, 0) AS "Number of Properties" '
                'FROM (SELECT Username, Email FROM User WHERE UserType = "OWNER") '
                    'AS Owners LEFT OUTER JOIN (SELECT p.Owner AS U2, COUNT(Owner) AS Properties FROM Property p '
                    'GROUP BY p.Owner) AS TotalProperties ON Username = U2 '
                'ORDER BY Username')
    allOwners = cur.fetchall();
    return render_template('AdminOwnersList.html', data=allOwners)


@app.route('/adminSortOwnersASC/<Param>')
def adminSortOwnersASC(Param):
    global adminOwnerCurrentSort
    adminOwnerCurrentSort = Param + " ASC"
    if adminOwnerSearchType == "Username" or adminOwnerSearchType == "Email":
        searchText = "%" + adminOwnerSearchText + "%"
        cur.execute('SELECT Username, Email, COALESCE(Properties, 0) AS "Number of Properties" '
                    'FROM (SELECT Username, Email FROM User WHERE UserType = "OWNER") '
                    'AS Owners LEFT OUTER JOIN (SELECT p.Owner AS U2, COUNT(Owner) AS Properties FROM Property p '
                    'GROUP BY p.Owner) AS TotalProperties ON Username = U2 '
                    'WHERE ' + adminOwnerSearchType + ' LIKE %s '
                    'ORDER BY ' + adminOwnerCurrentSort, [searchText])
    else:
        searchText = adminOwnerSearchText.split("-")
        if searchText[0] == "":
            searchText = [0, 1000000]
        minProperties = min(float(searchText[0]), float(searchText[1]))
        maxProperties = max(float(searchText[0]), float(searchText[1]))
        cur.execute('SELECT Username, Email, COALESCE(Properties, 0) AS "Number of Properties" '
                    'FROM ((SELECT Username, Email FROM User WHERE UserType = "OWNER") '
                    'AS Owners LEFT OUTER JOIN (SELECT p.Owner AS U2, COUNT(Owner) AS Properties FROM Property p '
                    'GROUP BY p.Owner) AS TotalProperties ON Username = U2) '
                    'WHERE COALESCE(Properties, 0) BETWEEN %s AND %s '
                    'ORDER BY ' + adminOwnerCurrentSort, [minProperties, maxProperties])
    allOwners = cur.fetchall()
    return render_template('AdminOwnersList.html', data=allOwners)


@app.route('/adminSortOwnersDESC/<Param>')
def adminSortOwnersDESC(Param):
    global adminOwnerCurrentSort
    adminOwnerCurrentSort = Param + " DESC"
    if adminOwnerSearchType == "Username" or adminOwnerSearchType == "Email":
        searchText = "%" + adminOwnerSearchText + "%"
        cur.execute('SELECT Username, Email, COALESCE(Properties, 0) AS "Number of Properties" '
                    'FROM (SELECT Username, Email FROM User WHERE UserType = "OWNER") '
                    'AS Owners LEFT OUTER JOIN (SELECT p.Owner AS U2, COUNT(Owner) AS Properties FROM Property p '
                    'GROUP BY p.Owner) AS TotalProperties ON Username = U2 '
                    'WHERE ' + adminOwnerSearchType + ' LIKE %s '
                    'ORDER BY ' + adminOwnerCurrentSort, [searchText])
    else:
        searchText = adminOwnerSearchText.split("-")
        if searchText[0] == "":
            searchText = [0, 1000000]
        minProperties = min(float(searchText[0]), float(searchText[1]))
        maxProperties = max(float(searchText[0]), float(searchText[1]))
        cur.execute('SELECT Username, Email, COALESCE(Properties, 0) AS "Number of Properties" '
                    'FROM ((SELECT Username, Email FROM User WHERE UserType = "OWNER") '
                    'AS Owners LEFT OUTER JOIN (SELECT p.Owner AS U2, COUNT(Owner) AS Properties FROM Property p '
                    'GROUP BY p.Owner) AS TotalProperties ON Username = U2) '
                    'WHERE COALESCE(Properties, 0) BETWEEN %s AND %s '
                    'ORDER BY ' + adminOwnerCurrentSort, [minProperties, maxProperties])
    allOwners = cur.fetchall()
    return render_template('AdminOwnersList.html', data=allOwners)


@app.route('/searchOwnersAdminOwnerList/', methods=['POST'])
def searchOwnersAdminOwnerList():
    global adminOwnerSearchType
    global adminOwnerSearchText
    adminOwnerSearchType = request.form.get('search_by')
    adminOwnerSearchText = request.form.get('search_text')
    if adminOwnerSearchType == "Username" or adminOwnerSearchType == "Email":
        searchText = "%" + adminOwnerSearchText + "%"
        cur.execute('SELECT Username, Email, COALESCE(Properties, 0) AS "Number of Properties" '
                    'FROM (SELECT Username, Email FROM User WHERE UserType = "OWNER") '
                    'AS Owners LEFT OUTER JOIN (SELECT p.Owner AS U2, COUNT(Owner) AS Properties FROM Property p '
                    'GROUP BY p.Owner) AS TotalProperties ON Username = U2 '
                    'WHERE ' + adminOwnerSearchType + ' LIKE %s '
                    'ORDER BY ' + adminOwnerCurrentSort, [searchText])
    else:
        searchText = adminOwnerSearchText.split("-")
        if searchText[0] == "":
            searchText = [0, 1000000]
        minProperties = min(float(searchText[0]), float(searchText[1]))
        maxProperties = max(float(searchText[0]), float(searchText[1]))
        cur.execute('SELECT Username, Email, COALESCE(Properties, 0) AS "Number of Properties" '
                    'FROM ((SELECT Username, Email FROM User WHERE UserType = "OWNER") '
                    'AS Owners LEFT OUTER JOIN (SELECT p.Owner AS U2, COUNT(Owner) AS Properties FROM Property p '
                    'GROUP BY p.Owner) AS TotalProperties ON Username = U2) '
                    'WHERE COALESCE(Properties, 0) BETWEEN %s AND %s '
                    'ORDER BY ' + adminOwnerCurrentSort, [minProperties, maxProperties])
    filteredProperties = cur.fetchall()
    return render_template('AdminOwnersList.html', data=filteredProperties)


@app.route('/deleteOwner/', methods=['POST'])
def deleteOwner():
    ownerUsername = request.form.get('owner_to_delete')
    cur.execute('DELETE FROM User WHERE Username = %s', [ownerUsername])
    conn.commit()
    cur.execute('DELETE FROM Property WHERE Owner = %s', [ownerUsername])  #Shouldn't need this but included anyway
    conn.commit()
    cur.execute('SELECT Username, Email, COALESCE(Properties, 0) AS "Number of Properties" '
                'FROM (SELECT Username, Email FROM User WHERE UserType = "OWNER") '
                'AS Owners LEFT OUTER JOIN (SELECT p.Owner AS U2, COUNT(Owner) AS Properties FROM Property p '
                'GROUP BY p.Owner) AS TotalProperties ON Username = U2 '
                'ORDER BY ' + adminOwnerCurrentSort)
    allVisitors = cur.fetchall();
    return render_template('AdminOwnersList.html', data=allVisitors)


@app.route('/adminUnconfirmedPropertiesList')
def adminUnconfirmedPropertiesList():
    clearAddedAndDeletedOrganisms(0)
    cur.execute('SELECT Name, Street, City, Zip, Size, PropertyType, IsPublic, IsCommercial, ID, Owner '
                'FROM Property '
                'WHERE ApprovedBy IS NULL '
                'ORDER BY Name')
    unconfirmedProperties = cur.fetchall()
    return render_template('AdminUnconfirmedList.html', data=unconfirmedProperties)


@app.route('/adminSortUnconfirmedASC/<Param>')
def adminSortUnconfirmedASC(Param):
    global adminUnconfirmedCurrentSort
    adminUnconfirmedCurrentSort = Param + " ASC"
    if adminUnconfirmedSearchType == "Name" or adminUnconfirmedSearchType == "Owner":
        searchText = "%" + adminUnconfirmedSearchText + "%"
        cur.execute('SELECT Name, Street, City, Zip, Size, PropertyType, IsPublic, IsCommercial, ID, Owner '
                    'FROM Property '
                    'WHERE ApprovedBy IS NULL AND ' + adminUnconfirmedSearchType + ' LIKE %s '
                    'ORDER BY ' + adminUnconfirmedCurrentSort, [searchText])
    else:
        sizes = adminUnconfirmedSearchText.split("-")
        if sizes[0] == "":
            sizes = [0, 1000000]
        minSize = min(float(sizes[0]), float(sizes[1]))
        maxSize = max(float(sizes[0]), float(sizes[1]))
        cur.execute('SELECT Name, Street, City, Zip, Size, PropertyType, IsPublic, IsCommercial, ID, Owner '
                    'FROM Property '
                    'WHERE ApprovedBy IS NULL AND Size BETWEEN %s AND %s '
                    'ORDER BY ' + adminUnconfirmedCurrentSort, [minSize, maxSize])
    sortedProperties = cur.fetchall()
    return render_template('AdminUnconfirmedList.html', data=sortedProperties)


@app.route('/adminSortUnconfirmedDESC/<Param>')
def adminSortUnconfirmedDESC(Param):
    global adminUnconfirmedCurrentSort
    adminUnconfirmedCurrentSort = Param + " DESC"
    if adminUnconfirmedSearchType == "Name" or adminUnconfirmedSearchType == "Owner":
        searchText = "%" + adminUnconfirmedSearchText + "%"
        cur.execute('SELECT Name, Street, City, Zip, Size, PropertyType, IsPublic, IsCommercial, ID, Owner '
                    'FROM Property '
                    'WHERE ApprovedBy IS NULL AND ' + adminUnconfirmedSearchType + ' LIKE %s '
                    'ORDER By ' + adminUnconfirmedCurrentSort, [searchText])
    else:
        sizes = adminUnconfirmedSearchText.split("-")
        if sizes[0] == "":
            sizes = [0, 1000000]
        minSize = min(float(sizes[0]), float(sizes[1]))
        maxSize = max(float(sizes[0]), float(sizes[1]))
        cur.execute('SELECT Name, Street, City, Zip, Size, PropertyType, IsPublic, IsCommercial, ID, Owner '
                    'FROM Property '
                    'WHERE ApprovedBy IS NULL AND Size BETWEEN %s AND %s '
                    'ORDER BY ' + adminUnconfirmedCurrentSort, [minSize, maxSize])
    sortedProperties = cur.fetchall()
    return render_template('AdminUnconfirmedList.html', data=sortedProperties)


@app.route('/searchPropertiesAdminUnconfirmedPropertyList/', methods=['POST'])
def searchPropertiesAdminUnconfirmedPropertyList():
    global adminUnconfirmedSearchType
    global adminUnconfirmedSearchText
    adminUnconfirmedSearchType = request.form.get('search_by')
    adminUnconfirmedSearchText = request.form.get('search_text')
    if adminUnconfirmedSearchType == "Name" or adminUnconfirmedSearchType == "Owner":
        searchText = "%" + adminUnconfirmedSearchText + "%"
        cur.execute('SELECT Name, Street, City, Zip, Size, PropertyType, IsPublic, IsCommercial, ID, Owner '
                    'FROM Property '
                    'WHERE ' + adminUnconfirmedSearchType + ' LIKE %s AND ApprovedBy IS NULL '
                    'ORDER BY ' + adminUnconfirmedCurrentSort, [searchText])
    else:
        sizes = adminUnconfirmedSearchText.split("-")
        if sizes[0] == "":
            sizes = [0, 1000000]
        minSize = min(float(sizes[0]), float(sizes[1]))
        maxSize = max(float(sizes[0]), float(sizes[1]))
        cur.execute('SELECT Name, Street, City, Zip, Size, PropertyType, IsPublic, IsCommercial, ID, Owner '
                    'FROM Property '
                    'WHERE Size >= %s AND Size <= %s AND ApprovedBy IS NULL '
                    'ORDER BY ' + adminUnconfirmedCurrentSort, [minSize, maxSize])
    filteredProperties = cur.fetchall()
    return render_template('AdminUnconfirmedList.html', data=filteredProperties)


@app.route('/deleteUnconfirmedProperty/', methods=['POST'])
def deleteUnconfirmedProperty():
    propertyInfo = request.form.get('unconfirmed_property_to_delete')
    cur.execute('DELETE FROM Property '
                'WHERE Name = %s OR ID = %s', [propertyInfo, propertyInfo])
    conn.commit()
    cur.execute('SELECT Name, Street, City, Zip, Size, PropertyType, IsPublic, IsCommercial, ID, Owner '
                'FROM Property '
                'WHERE ApprovedBy IS NULL '
                'ORDER BY ' + adminUnconfirmedCurrentSort)
    unconfirmedProperties = cur.fetchall()
    clearAddedAndDeletedOrganisms(0)
    return render_template('AdminUnconfirmedList.html', data=unconfirmedProperties)


@app.route('/adminManageUnconfirmedProperty/', methods=['GET','POST'])
def adminManageUnconfirmedProperty():
    propertyID = request.form.get('property_to_manage')
    cur.execute('SELECT * '
                'FROM Property '
                'WHERE ID = %s AND ApprovedBy IS NULL', [propertyID])
    propertyInfo = cur.fetchone()
    cur.execute('SELECT ItemName '
                'FROM Has '
                'WHERE PropertyID = %s', [propertyID])
    propertyItems = cur.fetchall()
    propertyItems = [element for item in propertyItems for element in item]
    cur.execute('SELECT Name, Type '
                'FROM FarmItem '
                'WHERE IsApproved = 1 AND Name NOT IN (SELECT ItemName '
                                                        'FROM Has '
                                                        'WHERE PropertyID = %s)', [propertyID])
    approvedItems = cur.fetchall()
    approvedItems = [list(x) for x in approvedItems]
    filteredItems = []
    if propertyInfo[8] == "ORCHARD":
        for item in approvedItems:
            if item[1] == "FRUIT" or item[1] == "NUT":
                filteredItems.append(item)
        approvedItems = filteredItems
    elif propertyInfo[8] == "GARDEN":
        for item in approvedItems:
            if item[1] == "VEGETABLE" or item[1] == "FLOWER":
                filteredItems.append(item)
        approvedItems = filteredItems
    return render_template('AdminManageUnconfirmedProperty.html', data=propertyInfo, name=propertyInfo[1], items=propertyItems,
                           approvedItems=approvedItems)


@app.route('/adminAddItemToUnconfirmedProperty/', methods=['POST'])
def adminAddItemToUnconfirmedProperty():
    global addedOrganismsConfirmedProperty
    organism = request.form.get('AddItem')
    organism = organism.split("-")
    propertyID = organism[0]
    #If the selected organism is not the empty string then update, greater than 1 because
    #the PID is also part of value
    if len(organism) > 1:
        cur.execute('INSERT INTO Has () '
                    'VALUES (%s, %s)', [propertyID, organism[1]])
        conn.commit()
        addedOrganismsUnconfirmedProperty.append([propertyID, organism[1]])
    #Pulling all the info about the property again in order to reload the manage property
    #page with the update organisms list
    cur.execute('SELECT * '
                'FROM Property '
                'WHERE ID = %s AND ApprovedBy IS NULL', [propertyID])
    propertyInfo = cur.fetchone()
    cur.execute('SELECT ItemName '
                'FROM Has '
                'WHERE PropertyID = %s', [propertyID])
    propertyItems = cur.fetchall()
    propertyItems = [element for item in propertyItems for element in item]
    cur.execute('SELECT Name, Type '
                'FROM FarmItem '
                'WHERE IsApproved = 1 AND Name NOT IN (SELECT ItemName '
                'FROM Has '
                'WHERE PropertyID = %s)', [propertyID])
    approvedItems = cur.fetchall()
    approvedItems = [list(x) for x in approvedItems]
    filteredItems = []
    if propertyInfo[8] == "ORCHARD":
        for item in approvedItems:
            if item[1] == "FRUIT" or item[1] == "NUT":
                filteredItems.append(item)
        approvedItems = filteredItems
    elif propertyInfo[8] == "GARDEN":
        for item in approvedItems:
            if item[1] == "VEGETABLE" or item[1] == "FLOWER":
                filteredItems.append(item)
        approvedItems = filteredItems
    return render_template('AdminManageUnconfirmedProperty.html', data=propertyInfo, name=propertyInfo[1], items=propertyItems,
                           approvedItems=approvedItems)


@app.route('/adminDeleteItemFromUnconfirmedProperty/', methods=['POST'])
def adminDeleteItemFromUnconfirmedProperty():
    global deletedOrganismsUnconfirmedProperty
    organism = request.form.get('DeleteItem')
    organism = organism.split("-")
    propertyID = organism[0]
    # If the selected organism is not the empty string then check for deletion, greater than 1 because
    # the PID is also part of value
    errorMessage = ""
    if len(organism) > 1:
        itemName = organism[1]
        #Get all items a property currently has
        cur.execute('SELECT ItemName '
                    'FROM Has '
                    'WHERE PropertyID = %s', [propertyID])
        currentItems = cur.fetchall()
        currentItems = [element for item in currentItems for element in item]
        currentTypes = []
        #Get the types of all the items a property currently has
        for i in currentItems:
            cur.execute('SELECT Type '
                        'FROM FarmItem '
                        'WHERE Name LIKE %s', [i])
            temp = cur.fetchall()
            temp = [element for item in temp for element in item]
            currentTypes.append(temp)
        currentTypes = sum(currentTypes, []) #2d to 1d list
        animalCount = currentTypes.count("ANIMAL")
        fruitCount = currentTypes.count("FRUIT")
        flowerCount = currentTypes.count("FLOWER")
        vegetableCount = currentTypes.count("VEGETABLE")
        nutCount = currentTypes.count("NUT")
        cur.execute('SELECT Type '
                    'FROM FarmItem '
                    'WHERE Name LIKE %s', [itemName])
        currentItemType = cur.fetchone()
        currentItemType = currentItemType[0]  #Get String from returned tuple
        cur.execute('SELECT PropertyType '
                    'FROM Property '
                    'WHERE ID=%s ', [propertyID])
        currentPropertyType = cur.fetchone()
        currentPropertyType = currentPropertyType[0]
        errorMessage = "Cannot Delete That Organism Because It Is the Last One Required For the Property Type"
        if currentPropertyType == "FARM":
            if currentItemType == "FRUIT" or currentItemType == "FLOWER" or currentItemType == "VEGETABLE" or currentItemType == "NUT":
                cropCount = fruitCount + flowerCount + vegetableCount + nutCount
                if cropCount > 1:
                    errorMessage = ""
                    cur.execute('DELETE FROM Has '
                                'WHERE PropertyID=%s AND ItemName LIKE %s', [propertyID, itemName])
                    conn.commit()
                    deletedOrganismsUnconfirmedProperty.append([propertyID, organism[1]])
            elif currentItemType == "ANIMAL":
                if animalCount > 1:
                    errorMessage = ""
                    cur.execute('DELETE FROM Has '
                                'WHERE PropertyID=%s AND ItemName LIKE %s', [propertyID, itemName])
                    conn.commit()
                    deletedOrganismsUnconfirmedProperty.append([propertyID, organism[1]])
        elif currentPropertyType == "ORCHARD":
            if fruitCount + nutCount > 1:
                errorMessage = ""
                cur.execute('DELETE FROM Has '
                            'WHERE PropertyID=%s AND ItemName LIKE %s', [propertyID, itemName])
                conn.commit()
                deletedOrganismsUnconfirmedProperty.append([propertyID, organism[1]])
        elif currentPropertyType == "GARDEN":
                if vegetableCount + flowerCount > 1:
                    errorMessage = ""
                    cur.execute('DELETE FROM Has '
                                'WHERE PropertyID=%s AND ItemName LIKE %s', [propertyID, itemName])
                    conn.commit()
                deletedOrganismsUnconfirmedProperty.append([propertyID, organism[1]])
    # Pulling all the info about the property again in order to reload the manage property
    # page with the update organisms list
    cur.execute('SELECT * '
                'FROM Property '
                'WHERE ID = %s AND ApprovedBy IS NULL', [propertyID])
    propertyInfo = cur.fetchone()
    cur.execute('SELECT ItemName '
                'FROM Has '
                'WHERE PropertyID = %s', [propertyID])
    propertyItems = cur.fetchall()
    propertyItems = [element for item in propertyItems for element in item]
    cur.execute('SELECT Name, Type '
                'FROM FarmItem '
                'WHERE IsApproved = 1 AND Name NOT IN (SELECT ItemName '
                'FROM Has '
                'WHERE PropertyID = %s)', [propertyID])
    approvedItems = cur.fetchall()
    approvedItems = [list(x) for x in approvedItems]
    filteredItems = []
    if propertyInfo[8] == "ORCHARD":
        for item in approvedItems:
            if item[1] == "FRUIT" or item[1] == "NUT":
                filteredItems.append(item)
        approvedItems = filteredItems
    elif propertyInfo[8] == "GARDEN":
        for item in approvedItems:
            if item[1] == "VEGETABLE" or item[1] == "FLOWER":
                filteredItems.append(item)
        approvedItems = filteredItems
    return render_template('AdminManageUnconfirmedProperty.html', data=propertyInfo, name=propertyInfo[1], items=propertyItems,
                           approvedItems=approvedItems, errorMessage=errorMessage)


@app.route('/saveUnconfirmedPropertyInfoAdmin/', methods=['POST'])
def saveUnconfirmedPropertyInfoAdmin():
    name = request.form.get("Name")
    id = request.form.get("ID")
    cur.execute('SELECT Name '
                'FROM Property '
                'WHERE ID != %s', [id])
    allPropertyNames = cur.fetchall()
    allPropertyNames = [element for item in allPropertyNames for element in item]
    for name2 in allPropertyNames:
        #If admin changes the property name to a name that already exists, go back to the
        #unconfirmed property page and show and error message
        if name.lower() == name2.lower():
            cur.execute('SELECT Name, Street, City, Zip, Size, PropertyType, IsPublic, IsCommercial, ID, Owner '
                        'FROM Property '
                        'WHERE ApprovedBy IS NULL '
                        'ORDER BY Name')
            unconfirmedProperties = cur.fetchall()
            return render_template('AdminUnconfirmedList.html', data=unconfirmedProperties,
                                   error="A Property with that name already exists")
    street = request.form.get("Street")
    city = request.form.get("City")
    zip = request.form.get("Zip")
    size = request.form.get("Size")
    #If any property attribute is empty, reject the updates
    if not name or not street or not city or not zip or not size:
        cur.execute('SELECT Name, Street, City, Zip, Size, PropertyType, IsPublic, IsCommercial, ID, Owner '
                    'FROM Property '
                    'WHERE ApprovedBy IS NULL '
                    'ORDER BY Name')
        unconfirmedProperties = cur.fetchall()
        return render_template('AdminUnconfirmedList.html', data=unconfirmedProperties,
                               error="The property must have values for all of its attributes")
    try:
        size = abs(float(size))
        zip = abs(int(zip))
    except:
        cur.execute('SELECT Name, Street, City, Zip, Size, PropertyType, IsPublic, IsCommercial, ID, Owner '
                    'FROM Property '
                    'WHERE ApprovedBy IS NULL '
                    'ORDER BY Name')
        unconfirmedProperties = cur.fetchall()
        return render_template('AdminUnconfirmedList.html', data=unconfirmedProperties,
                               error="Size must be a number and zip must be an integer")
    isPublic = request.form.get("Public")
    isCommercial = request.form.get("Commercial")
    cur.execute('UPDATE Property '
                'SET Name=%s, Size=%s, IsCommercial=%s, IsPublic=%s, Street=%s, City=%s, '
                    'Zip=%s, ApprovedBy=%s '
                'WHERE ID=%s', [name, size, isCommercial, isPublic, street, city, zip, curUser.username, id])
    conn.commit()
    clearAddedAndDeletedOrganisms(0)
    return(redirect(url_for('adminUnconfirmedPropertiesList')))


@app.route('/adminDontSaveChangesUnconfirmedProperty/')
def adminDontSaveChangesUnconfirmedProperty():
    for pair in addedOrganismsUnconfirmedProperty:
        cur.execute('DELETE FROM Has '
                    'WHERE PropertyID = %s AND ItemName = %s', [pair[0], pair[1]])
        conn.commit()
    for pair in deletedOrganismsUnconfirmedProperty:
        cur.execute('INSERT INTO Has '
                    'VALUES(%s, %s)', [pair[0], pair[1]])
        conn.commit()
    clearAddedAndDeletedOrganisms(0)
    return redirect(url_for('adminUnconfirmedPropertiesList'))


@app.route('/adminConfirmedPropertiesList')
def adminConfirmedPropertiesList():
    clearAddedAndDeletedOrganisms(1)
    cur.execute('SELECT Name, Street, City, Zip, Size, PropertyType, IsPublic, IsCommercial, ID, ApprovedBy, COALESCE(Average, 0) '
                'FROM ((SELECT * FROM Property WHERE ApprovedBy IS NOT NULL) AS P LEFT OUTER JOIN (SELECT PropertyID, AVG(Rating) AS Average FROM Visit GROUP BY PropertyID) AS A ON ID=PropertyID) '
                'WHERE ApprovedBy IS NOT NULL '
                'ORDER BY Name')
    confirmedProperties = cur.fetchall()
    return render_template('AdminConfirmedList.html', data=confirmedProperties)


@app.route('/adminSortConfirmedASC/<Param>')
def adminSortConfirmedASC(Param):
    global adminConfirmedCurrentSort
    adminConfirmedCurrentSort = Param + " ASC"
    if adminConfirmedSearchType == "Name" or adminConfirmedSearchType == "PropertyType" or adminConfirmedSearchType == "ApprovedBy":
        searchText = "%" + adminConfirmedSearchText + "%"
        cur.execute('SELECT Name, Street, City, Zip, Size, PropertyType, IsPublic, IsCommercial, ID, ApprovedBy, COALESCE(Average, 0) '
                    'FROM ((SELECT * FROM Property WHERE ApprovedBy IS NOT NULL) AS P LEFT OUTER JOIN (SELECT PropertyID, AVG(Rating) AS Average FROM Visit GROUP BY PropertyID) AS A ON ID=PropertyID) '
                    'WHERE ApprovedBy IS NOT NULL AND ' + adminConfirmedSearchType + ' LIKE %s '
                    'ORDER BY ' + adminConfirmedCurrentSort, [searchText])
    elif adminConfirmedSearchType == "Zip":
        cur.execute('SELECT Name, Street, City, Zip, Size, PropertyType, IsPublic, IsCommercial, ID, ApprovedBy, COALESCE(Average, 0) '
                    'FROM ((SELECT * FROM Property WHERE ApprovedBy IS NOT NULL) AS P LEFT OUTER JOIN (SELECT PropertyID, AVG(Rating) AS Average FROM Visit GROUP BY PropertyID) AS A ON ID=PropertyID) '
                    'WHERE ApprovedBy IS NOT NULL AND Zip=%s '
                    'ORDER BY ' + adminConfirmedCurrentSort, [adminConfirmedSearchText])
    else :
        rating = adminConfirmedSearchText.split("-")
        if rating[0] == "":
            rating = [0, 1000000]
        minRating = min(float(rating[0]), float(rating[1]))
        maxRating = max(float(rating[0]), float(rating[1]))
        cur.execute('SELECT Name, Street, City, Zip, Size, PropertyType, IsPublic, IsCommercial, ID, ApprovedBy, COALESCE(Average, 0) '
                    'FROM ((SELECT * FROM Property WHERE ApprovedBy IS NOT NULL) AS P LEFT OUTER JOIN (SELECT PropertyID, AVG(Rating) AS Average FROM Visit GROUP BY PropertyID) AS A ON ID=PropertyID) '
                    'WHERE ApprovedBy IS NOT NULL AND Average Between %s AND %s '
                    'ORDER BY ' + adminConfirmedCurrentSort, [minRating, maxRating])
    sortedProperties = cur.fetchall()
    return render_template('AdminConfirmedList.html', data=sortedProperties)


@app.route('/adminSortConfirmedDESC/<Param>')
def adminSortConfirmedDESC(Param):
    global adminConfirmedCurrentSort
    adminConfirmedCurrentSort = Param + " DESC"
    if adminConfirmedSearchType == "Name" or adminConfirmedSearchType == "PropertyType" or adminConfirmedSearchType == "ApprovedBy":
        searchText = "%" + adminConfirmedSearchText + "%"
        cur.execute('SELECT Name, Street, City, Zip, Size, PropertyType, IsPublic, IsCommercial, ID, ApprovedBy, COALESCE(Average, 0) '
                    'FROM ((SELECT * FROM Property WHERE ApprovedBy IS NOT NULL) AS P LEFT OUTER JOIN (SELECT PropertyID, AVG(Rating) AS Average FROM Visit GROUP BY PropertyID) AS A ON ID=PropertyID) '
                    'WHERE ApprovedBy IS NOT NULL AND ' + adminConfirmedSearchType + ' LIKE %s '
                    'ORDER BY ' + adminConfirmedCurrentSort, [searchText])
    elif adminConfirmedSearchType == "Zip":
        cur.execute('SELECT Name, Street, City, Zip, Size, PropertyType, IsPublic, IsCommercial, ID, ApprovedBy, COALESCE(Average, 0) '
                    'FROM ((SELECT * FROM Property WHERE ApprovedBy IS NOT NULL) AS P LEFT OUTER JOIN (SELECT PropertyID, AVG(Rating) AS Average FROM Visit GROUP BY PropertyID) AS A ON ID=PropertyID) '
                    'WHERE ApprovedBy IS NOT NULL AND Zip=%s '
                    'ORDER BY ' + adminConfirmedCurrentSort, [adminConfirmedSearchText])
    else :
        rating = adminConfirmedSearchText.split("-")
        if rating[0] == "":
            rating = [0, 1000000]
        minRating = min(float(rating[0]), float(rating[1]))
        maxRating = max(float(rating[0]), float(rating[1]))
        cur.execute('SELECT Name, Street, City, Zip, Size, PropertyType, IsPublic, IsCommercial, ID, ApprovedBy, COALESCE(Average, 0) '
                    'FROM ((SELECT * FROM Property WHERE ApprovedBy IS NOT NULL) AS P LEFT OUTER JOIN (SELECT PropertyID, AVG(Rating) AS Average FROM Visit GROUP BY PropertyID) AS A ON ID=PropertyID) '
                    'WHERE ApprovedBy IS NOT NULL AND Average Between %s AND %s '
                    'ORDER BY ' + adminConfirmedCurrentSort, [minRating, maxRating])
    sortedProperties = cur.fetchall()
    return render_template('AdminConfirmedList.html', data=sortedProperties)


@app.route('/searchPropertiesAdminConfirmedPropertyList/', methods=['POST'])
def searchPropertiesAdminConfirmedPropertyList():
    global adminConfirmedSearchType
    global adminConfirmedSearchText
    adminConfirmedSearchType = request.form.get('search_by')
    adminConfirmedSearchText = request.form.get('search_text')
    if adminConfirmedSearchType == "Name" or adminConfirmedSearchType == "PropertyType" or adminConfirmedSearchType == "ApprovedBy":
        searchText = "%" + adminConfirmedSearchText + "%"
        cur.execute('SELECT Name, Street, City, Zip, Size, PropertyType, IsPublic, IsCommercial, ID, ApprovedBy, COALESCE(Average, 0) '
                    'FROM ((SELECT * FROM Property WHERE ApprovedBy IS NOT NULL) AS P LEFT OUTER JOIN (SELECT PropertyID, AVG(Rating) AS Average FROM Visit GROUP BY PropertyID) AS A ON ID=PropertyID) '
                    'WHERE ApprovedBy IS NOT NULL AND ' + adminConfirmedSearchType + ' LIKE %s '
                    'ORDER BY ' + adminConfirmedCurrentSort, [searchText])
    elif adminConfirmedSearchType == "Zip":
        cur.execute('SELECT Name, Street, City, Zip, Size, PropertyType, IsPublic, IsCommercial, ID, ApprovedBy, COALESCE(Average, 0) '
                    'FROM ((SELECT * FROM Property WHERE ApprovedBy IS NOT NULL) AS P LEFT OUTER JOIN (SELECT PropertyID, AVG(Rating) AS Average FROM Visit GROUP BY PropertyID) AS A ON ID=PropertyID) '
                    'WHERE ApprovedBy IS NOT NULL AND Zip=%s '
                    'ORDER BY ' + adminConfirmedCurrentSort, [adminConfirmedSearchText])
    else:
        rating = adminConfirmedSearchText.split("-")
        if rating[0] == "":
            rating = [0, 1000000]
        minRating = min(float(rating[0]), float(rating[1]))
        maxRating = max(float(rating[0]), float(rating[1]))
        cur.execute('SELECT Name, Street, City, Zip, Size, PropertyType, IsPublic, IsCommercial, ID, ApprovedBy, COALESCE(Average, 0) '
                    'FROM ((SELECT * FROM Property WHERE ApprovedBy IS NOT NULL) AS P LEFT OUTER JOIN (SELECT PropertyID, AVG(Rating) AS Average FROM Visit GROUP BY PropertyID) AS A ON ID=PropertyID) '
                    'WHERE ApprovedBy IS NOT NULL AND COALESCE(Average, 0) >= %s AND COALESCE(Average, 0) <= %s '
                    'ORDER BY ' + adminConfirmedCurrentSort, [minRating, maxRating])
    filteredProperties = cur.fetchall()
    return render_template('AdminConfirmedList.html', data=filteredProperties)


@app.route('/deleteConfirmedProperty/', methods=['POST'])
def deleteConfirmedProperty():
    clearAddedAndDeletedOrganisms(1)
    propertyInfo = request.form.get('confirmed_property_to_delete')
    cur.execute('DELETE FROM Property '
                'WHERE Name = %s OR ID = %s', [propertyInfo, propertyInfo])
    conn.commit()
    cur.execute('SELECT Name, Street, City, Zip, Size, PropertyType, IsPublic, IsCommercial, ID, ApprovedBy, COALESCE(Average, 0) '
                'FROM ((SELECT * FROM Property WHERE ApprovedBy IS NOT NULL) AS P LEFT OUTER JOIN (SELECT PropertyID, AVG(Rating) AS Average FROM Visit GROUP BY PropertyID) AS A ON ID=PropertyID) '
                'WHERE ApprovedBy IS NOT NULL '
                'ORDER BY ' + adminConfirmedCurrentSort)
    confirmedProperties = cur.fetchall()
    return render_template('AdminConfirmedList.html', data=confirmedProperties)


@app.route('/adminManageConfirmedProperty/', methods=['POST'])
def adminManageConfirmedProperty():
    propertyID = request.form.get('property_to_manage')
    cur.execute('SELECT Name, Street, City, Zip, Size, PropertyType, IsPublic, IsCommercial, ID, ApprovedBy, COALESCE (Average, 0) '
                'FROM ((SELECT * FROM Property WHERE ApprovedBy IS NOT NULL) AS P LEFT OUTER JOIN (SELECT PropertyID, AVG(Rating) AS Average FROM Visit GROUP BY PropertyID) AS A ON ID=PropertyID) '
                'WHERE ID = %s ', [propertyID])
    propertyInfo = cur.fetchone()
    cur.execute('SELECT ItemName '
                'FROM Has '
                'WHERE PropertyID = %s', [propertyID])
    propertyItems = cur.fetchall()
    propertyItems = [element for item in propertyItems for element in item]
    approvedItems = []
    if propertyInfo[5] == "FARM":
        cur.execute('SELECT Name, Type '
                    'FROM FarmItem '
                    'WHERE IsApproved = 1 AND Name NOT IN (SELECT ItemName '
                                                            'FROM Has '
                                                            'WHERE PropertyID = %s)', [propertyID])
        approvedItems = cur.fetchall()
    elif propertyInfo[5] == "GARDEN":
        cur.execute('SELECT Name, Type '
                    'FROM FarmItem '
                    'WHERE IsApproved = 1 AND Name NOT IN (SELECT ItemName '
                    'FROM Has '
                    'WHERE PropertyID = %s) AND (Type="FLOWER" OR Type="VEGETABLE")', [propertyID])
        approvedItems = cur.fetchall()
    else:
        cur.execute('SELECT Name, Type '
                    'FROM FarmItem '
                    'WHERE IsApproved = 1 AND Name NOT IN (SELECT ItemName '
                    'FROM Has '
                    'WHERE PropertyID = %s) AND (Type="FRUIT" OR Type="NUT")', [propertyID])
        approvedItems = cur.fetchall()
    return render_template('AdminManageConfirmedProperty.html', data=propertyInfo, name=propertyInfo[0], items=propertyItems,
                           approvedItems=approvedItems)


@app.route('/adminAddItemToConfirmedProperty/', methods=['POST'])
def adminAddItemToConfirmedProperty():
    global addedOrganismsConfirmedProperty
    organism = request.form.get('AddItem')
    organism = organism.split("-")
    propertyID = organism[0]
    # If the selected organism is not the empty string then update, greater than 1 because
    # the PID is also part of value
    if len(organism) > 1:
        cur.execute('INSERT INTO Has () '
                    'VALUES (%s, %s)', [propertyID, organism[1]])
        conn.commit()
        addedOrganismsConfirmedProperty.append([propertyID, organism[1]])
    # Pulling all the info about the property again in order to reload the manage property
    # page with the update organisms list
    cur.execute('SELECT Name, Street, City, Zip, Size, PropertyType, IsPublic, IsCommercial, ID, ApprovedBy, COALESCE (Average, 0) '
                'FROM ((SELECT * FROM Property WHERE ApprovedBy IS NOT NULL) AS P LEFT OUTER JOIN (SELECT PropertyID, AVG(Rating) AS Average FROM Visit GROUP BY PropertyID) AS A ON ID=PropertyID) '
                'WHERE ID = %s ', [propertyID])
    propertyInfo = cur.fetchone()
    cur.execute('SELECT ItemName '
                'FROM Has '
                'WHERE PropertyID = %s', [propertyID])
    propertyItems = cur.fetchall()
    propertyItems = [element for item in propertyItems for element in item]
    approvedItems = []
    if propertyInfo[5] == "FARM":
        cur.execute('SELECT Name, Type '
                    'FROM FarmItem '
                    'WHERE IsApproved = 1 AND Name NOT IN (SELECT ItemName '
                    'FROM Has '
                    'WHERE PropertyID = %s)', [propertyID])
        approvedItems = cur.fetchall()
    elif propertyInfo[5] == "GARDEN":
        cur.execute('SELECT Name, Type '
                    'FROM FarmItem '
                    'WHERE IsApproved = 1 AND Name NOT IN (SELECT ItemName '
                    'FROM Has '
                    'WHERE PropertyID = %s) AND (Type="FLOWER" OR Type="VEGETABLE")', [propertyID])
        approvedItems = cur.fetchall()
    else:
        cur.execute('SELECT Name, Type '
                    'FROM FarmItem '
                    'WHERE IsApproved = 1 AND Name NOT IN (SELECT ItemName '
                    'FROM Has '
                    'WHERE PropertyID = %s) AND (Type="FRUIT" OR Type="NUT")', [propertyID])
        approvedItems = cur.fetchall()
    return render_template('AdminManageConfirmedProperty.html', data=propertyInfo, name=propertyInfo[0],
                           items=propertyItems, approvedItems=approvedItems)

@app.route('/adminDeleteItemFromConfirmedProperty/', methods=['POST'])
def adminDeleteItemFromConfirmedProperty():
    global deletedOrganismsConfirmedProperty
    organism = request.form.get('DeleteItem')
    organism = organism.split("-")
    propertyID = organism[0]
    # If the selected organism is not the empty string then check for deletion, greater than 1 because
    # the PID is also part of value
    errorMessage = ""
    if len(organism) > 1:
        itemName = organism[1]
        # Get all items a property currently has
        cur.execute('SELECT ItemName '
                    'FROM Has '
                    'WHERE PropertyID = %s', [propertyID])
        currentItems = cur.fetchall()
        currentItems = [element for item in currentItems for element in item]
        currentTypes = []
        # Get the types of all the items a property currently has
        for i in currentItems:
            cur.execute('SELECT Type '
                        'FROM FarmItem '
                        'WHERE Name LIKE %s', [i])
            temp = cur.fetchall()
            temp = [element for item in temp for element in item]
            currentTypes.append(temp)
        currentTypes = sum(currentTypes, [])  # 2d to 1d list
        animalCount = currentTypes.count("ANIMAL")
        fruitCount = currentTypes.count("FRUIT")
        flowerCount = currentTypes.count("FLOWER")
        vegetableCount = currentTypes.count("VEGETABLE")
        nutCount = currentTypes.count("NUT")
        cur.execute('SELECT Type '
                    'FROM FarmItem '
                    'WHERE Name LIKE %s', [itemName])
        currentItemType = cur.fetchone()
        currentItemType = currentItemType[0]  # Get String from returned tuple
        cur.execute('SELECT PropertyType '
                    'FROM Property '
                    'WHERE ID=%s ', [propertyID])
        currentPropertyType = cur.fetchone()
        currentPropertyType = currentPropertyType[0]
        errorMessage = "Cannot Delete That Organism Because It Is the Last One Required For the Property Type"
        if currentPropertyType == "FARM":
            if currentItemType == "FRUIT" or currentItemType == "FLOWER" or currentItemType == "VEGETABLE" or currentItemType == "NUT":
                cropCount = fruitCount + flowerCount + vegetableCount + nutCount
                if cropCount > 1:
                    errorMessage = ""
                    cur.execute('DELETE FROM Has '
                                'WHERE PropertyID=%s AND ItemName LIKE %s', [propertyID, itemName])
                    conn.commit()
                    deletedOrganismsConfirmedProperty.append([propertyID, organism[1]])
            elif currentItemType == "ANIMAL":
                if animalCount > 1:
                    errorMessage = ""
                    cur.execute('DELETE FROM Has '
                                'WHERE PropertyID=%s AND ItemName LIKE %s', [propertyID, itemName])
                    conn.commit()
                    deletedOrganismsConfirmedProperty.append([propertyID, organism[1]])
        elif currentPropertyType == "ORCHARD":
            if fruitCount + nutCount > 1:
                errorMessage = ""
                cur.execute('DELETE FROM Has '
                            'WHERE PropertyID=%s AND ItemName LIKE %s', [propertyID, itemName])
                conn.commit()
                deletedOrganismsConfirmedProperty.append([propertyID, organism[1]])
        elif currentPropertyType == "GARDEN":
            if vegetableCount + flowerCount > 1:
                errorMessage = ""
                cur.execute('DELETE FROM Has '
                            'WHERE PropertyID=%s AND ItemName LIKE %s', [propertyID, itemName])
                conn.commit()
                deletedOrganismsConfirmedProperty.append([propertyID, organism[1]])
    # Pulling all the info about the property again in order to reload the manage property
    # page with the updated organisms list
    cur.execute('SELECT Name, Street, City, Zip, Size, PropertyType, IsPublic, IsCommercial, ID, ApprovedBy, COALESCE (Average, 0) '
                'FROM ((SELECT * FROM Property WHERE ApprovedBy IS NOT NULL) AS P LEFT OUTER JOIN (SELECT PropertyID, AVG(Rating) AS Average FROM Visit GROUP BY PropertyID) AS A ON ID=PropertyID) '
                'WHERE ID = %s ', [propertyID])
    propertyInfo = cur.fetchone()
    cur.execute('SELECT ItemName '
                'FROM Has '
                'WHERE PropertyID = %s', [propertyID])
    propertyItems = cur.fetchall()
    propertyItems = [element for item in propertyItems for element in item]
    approvedItems = []
    if propertyInfo[5] == "FARM":
        cur.execute('SELECT Name, Type '
                    'FROM FarmItem '
                    'WHERE IsApproved = 1 AND Name NOT IN (SELECT ItemName '
                    'FROM Has '
                    'WHERE PropertyID = %s)', [propertyID])
        approvedItems = cur.fetchall()
    elif propertyInfo[5] == "GARDEN":
        cur.execute('SELECT Name, Type '
                    'FROM FarmItem '
                    'WHERE IsApproved = 1 AND Name NOT IN (SELECT ItemName '
                    'FROM Has '
                    'WHERE PropertyID = %s) AND (Type="FLOWER" OR Type="VEGETABLE")', [propertyID])
        approvedItems = cur.fetchall()
    else:
        cur.execute('SELECT Name, Type '
                    'FROM FarmItem '
                    'WHERE IsApproved = 1 AND Name NOT IN (SELECT ItemName '
                    'FROM Has '
                    'WHERE PropertyID = %s) AND (Type="FRUIT" OR Type="NUT")', [propertyID])
        approvedItems = cur.fetchall()
    return render_template('AdminManageConfirmedProperty.html', data=propertyInfo, name=propertyInfo[0],
                           items=propertyItems, approvedItems=approvedItems, errorMessage=errorMessage)


@app.route('/saveConfirmedPropertyInfoAdmin/', methods=['POST'])
def saveConfirmedPropertyInfoAdmin():
    name = request.form.get("Name")
    id = request.form.get("ID")
    cur.execute('SELECT Name '
                'FROM Property '
                'WHERE ID != %s', [id])
    allPropertyNames = cur.fetchall()
    allPropertyNames = [element for item in allPropertyNames for element in item]
    for name2 in allPropertyNames:
        #If admin changes the property name to a name that already exists, go back to the
        #unconfirmed property page and show and error message
        if name.lower() == name2.lower():
            cur.execute('SELECT Name, Street, City, Zip, Size, PropertyType, IsPublic, IsCommercial, ID, ApprovedBy, COALESCE (Average, 0) '
                        'FROM ((SELECT * FROM Property WHERE ApprovedBy IS NOT NULL) AS P LEFT OUTER JOIN (SELECT PropertyID, AVG(Rating) AS Average FROM Visit GROUP BY PropertyID) AS A ON ID=PropertyID) '
                        'WHERE ApprovedBy IS NOT NULL '
                        'ORDER BY Name ')
            confirmedProperties = cur.fetchall()
            return render_template('AdminConfirmedList.html', data=confirmedProperties,
                                   error="A Property with that name already exists")
    street = request.form.get("Street")
    city = request.form.get("City")
    zip = request.form.get("Zip")
    size = request.form.get("Size")
    # If any property attribute is empty, reject the updates
    if not name or not street or not city or not zip or not size:
        cur.execute('SELECT Name, Street, City, Zip, Size, PropertyType, IsPublic, IsCommercial, ID, ApprovedBy, COALESCE (Average, 0) '
                    'FROM ((SELECT * FROM Property WHERE ApprovedBy IS NOT NULL) AS P LEFT OUTER JOIN (SELECT PropertyID, AVG(Rating) AS Average FROM Visit GROUP BY PropertyID) AS A ON ID=PropertyID) '
                    'WHERE ApprovedBy IS NOT NULL '
                    'ORDER BY Name ')
        confirmedProperties = cur.fetchall()
        return render_template('AdminConfirmedList.html', data=confirmedProperties,
                               error="The property must have values for all of its attributes")
    try:
        size = abs(float(size))
        zip = abs(int(zip))
    except:
        cur.execute('SELECT Name, Street, City, Zip, Size, PropertyType, IsPublic, IsCommercial, ID, ApprovedBy, COALESCE (Average, 0) '
                    'FROM ((SELECT * FROM Property WHERE ApprovedBy IS NOT NULL) AS P LEFT OUTER JOIN (SELECT PropertyID, AVG(Rating) AS Average FROM Visit GROUP BY PropertyID) AS A ON ID=PropertyID) '
                    'WHERE ApprovedBy IS NOT NULL '
                    'ORDER BY Name ')
        confirmedProperties = cur.fetchall()
        return render_template('AdminConfirmedList.html', data=confirmedProperties,
                               error="Size must be a number and zip must be an integer")
    isPublic = request.form.get("Public")
    isCommercial = request.form.get("Commercial")
    cur.execute('SELECT Name, Street, City, Zip, Size, IsPublic, IsCommercial '
                'FROM Property '
                'WHERE ID = %s', [id])
    previousPropertyValues = cur.fetchone()
    cur.execute('UPDATE Property '
                'SET Name=%s, Size=%s, IsCommercial=%s, IsPublic=%s, Street=%s, City=%s, Zip=%s, ApprovedBy=%s '
                'WHERE ID=%s', [name, size, isCommercial, isPublic, street, city, zip, curUser.username, id])
    conn.commit()
    cur.execute('SELECT Name, Street, City, Zip, Size, IsPublic, IsCommercial '
                'FROM Property '
                'WHERE ID = %s', [id])
    currentPropertyValues = cur.fetchone()
    #Reset all of the visits to the modified confirmed property if admin made changes
    print(addedOrganismsConfirmedProperty, deletedOrganismsConfirmedProperty)
    if previousPropertyValues != currentPropertyValues or len(addedOrganismsConfirmedProperty) != 0 or len(deletedOrganismsConfirmedProperty) != 0:
        cur.execute('DELETE FROM Visit '
                    'WHERE PropertyID = %s', [id])
        conn.commit()
    clearAddedAndDeletedOrganisms(1)
    return redirect(url_for('adminConfirmedPropertiesList'))


#If admin presses back button, revert any added/deleted organisms from the property
@app.route('/adminDontSaveChangesConfirmedProperty/')
def adminDontSaveChangesConfirmedProperty():
    for pair in addedOrganismsConfirmedProperty:
        cur.execute('DELETE FROM Has '
                    'WHERE PropertyID = %s AND ItemName = %s', [pair[0], pair[1]])
        conn.commit()
    for pair in deletedOrganismsConfirmedProperty:
        cur.execute('INSERT INTO Has '
                    'VALUES(%s, %s)', [pair[0], pair[1]])
        conn.commit()
    clearAddedAndDeletedOrganisms(1)
    return redirect(url_for('adminConfirmedPropertiesList'))


@app.route('/adminApprovedOrganismsList')
def adminApprovedOrganismsList():
    cur.execute('SELECT Name, Type '
                'FROM FarmItem '
                'WHERE IsApproved = 1 '
                'ORDER BY Name ')
    approvedOrganisms = cur.fetchall()
    return render_template('AdminApprovedOrganisms.html', data=approvedOrganisms)


@app.route('/adminSortApprovedASC/<Param>')
def adminSortApprovedASC(Param):
    global adminApprovedCurrentSort
    adminApprovedCurrentSort = Param + " ASC"
    searchText = "%" + adminApprovedSearchText + "%"
    cur.execute('SELECT Name, Type '
                'FROM FarmItem '
                'WHERE IsApproved = 1 AND ' + adminApprovedSearchType + ' LIKE %s '
                'ORDER BY ' + adminApprovedCurrentSort, [searchText])
    sortedProperties = cur.fetchall()
    return render_template('AdminApprovedOrganisms.html', data=sortedProperties)


@app.route('/adminSortApprovedDESC/<Param>')
def adminSortApprovedDESC(Param):
    global adminApprovedCurrentSort
    adminApprovedCurrentSort = Param + " DESC"
    searchText = "%" + adminApprovedSearchText + "%"
    cur.execute('SELECT Name, Type '
                'FROM FarmItem '
                'WHERE IsApproved = 1 AND ' + adminApprovedSearchType + ' LIKE %s '
                'ORDER BY ' + adminApprovedCurrentSort, [searchText])
    sortedProperties = cur.fetchall()
    return render_template('AdminApprovedOrganisms.html', data=sortedProperties)


@app.route('/searchApprovedOrganismsAdmin/', methods=['POST'])
def searchApprovedOrganismsAdmin():
    global adminApprovedSearchType
    global adminApprovedSearchText
    adminApprovedSearchType = request.form.get('search_by')
    adminApprovedSearchText = request.form.get('search_text')
    searchText = "%" + adminApprovedSearchText + "%"
    cur.execute('SELECT Name, Type '
                'FROM FarmItem '
                'WHERE IsApproved = 1 AND ' + adminApprovedSearchType + ' LIKE %s '
                'ORDER BY ' + adminApprovedCurrentSort, [searchText])
    filteredProperties = cur.fetchall()
    return render_template('AdminApprovedOrganisms.html', data=filteredProperties)


@app.route('/addApprovedOrganismsAdmin/', methods=['POST'])
def addApprovedOrganismsAdmin():
    organismType = request.form.get('organism_type')
    organismName = request.form.get('organism_name')
    errorMessage = "Must Include Organism Name When Adding to Approved Animals/Crops"
    if organismName != "":
        cur.execute('SELECT Name FROM FarmItem '
                    'WHERE Name = %s', [organismName])
        sameName = cur.fetchone()
        if sameName is None:
            cur.execute('INSERT INTO FarmItem () '
                        'VALUES(%s, 1, %s)', [organismName, organismType])
            conn.commit()
            errorMessage = ""
        else:
            cur.execute('UPDATE FarmItem '
                        'SET IsApproved = 1 '
                        'WHERE Name = %s', [organismName])
            conn.commit()
            errorMessage = ""
    cur.execute('SELECT Name, Type '
                'FROM FarmItem '
                'WHERE IsApproved = 1 '
                'ORDER BY ' + adminApprovedCurrentSort)
    approvedOrganisms = cur.fetchall()
    return render_template('AdminApprovedOrganisms.html', data=approvedOrganisms, error=errorMessage)


@app.route('/deleteApprovedOrganismsAdmin/', methods=['POST'])
def deleteApprovedOrganismsAdmin():
    organismName = request.form.get('organism_name')
    errorMessage = "Must Specify Organism Name to Delete"
    if organismName != "":
        cur.execute('DELETE FROM FarmItem '
                    'WHERE Name = %s ', [organismName])
        conn.commit()
        errorMessage = ""
    cur.execute('SELECT Name, Type '
                'FROM FarmItem '
                'WHERE IsApproved = 1 '
                'ORDER BY ' + adminApprovedCurrentSort)
    approvedOrganisms = cur.fetchall()
    return render_template('AdminApprovedOrganisms.html', data=approvedOrganisms, error=errorMessage)


@app.route('/adminPendingOrganismsList')
def adminPendingOrganismsList():
    cur.execute('SELECT Name, Type '
                'FROM FarmItem '
                'WHERE IsApproved = 0 '
                'ORDER BY Name')
    pendingOrganisms = cur.fetchall()
    return render_template('AdminPendingOrganisms.html', data=pendingOrganisms)


@app.route('/adminSortPendingASC/<Param>')
def adminSortPendingASC(Param):
    global adminPendingCurrentSort
    adminPendingCurrentSort = Param + " ASC"
    searchText = "%" + adminPendingSearchText + "%"
    cur.execute('SELECT Name, Type '
                'FROM FarmItem '
                'WHERE IsApproved = 0 AND ' + adminPendingSearchType + ' LIKE %s '
                'ORDER BY ' + adminPendingCurrentSort, [searchText])
    sortedProperties = cur.fetchall()
    return render_template('AdminPendingOrganisms.html', data=sortedProperties)


@app.route('/adminSortPendingDESC/<Param>')
def adminSortPendingDESC(Param):
    global adminPendingCurrentSort
    adminPendingCurrentSort = Param + " DESC"
    searchText = "%" + adminPendingSearchText + "%"
    cur.execute('SELECT Name, Type '
                'FROM FarmItem '
                'WHERE IsApproved = 0 AND ' + adminPendingSearchType + ' LIKE %s '
                'ORDER BY ' + adminPendingCurrentSort, [searchText])
    sortedProperties = cur.fetchall()
    return render_template('AdminPendingOrganisms.html', data=sortedProperties)


@app.route('/searchPendingOrganismsAdmin/', methods=['POST'])
def searchPendingOrganismsAdmin():
    global adminPendingSearchType
    global adminPendingSearchText
    adminPendingSearchType = request.form.get('search_by')
    adminPendingSearchText = request.form.get('search_text')
    searchText = "%" + adminPendingSearchText + "%"
    cur.execute('SELECT Name, Type '
                'FROM FarmItem '
                'WHERE IsApproved = 0 AND ' + adminPendingSearchType + ' LIKE %s '
                'ORDER BY ' + adminPendingCurrentSort, [searchText])
    filteredProperties = cur.fetchall()
    return render_template('AdminPendingOrganisms.html', data=filteredProperties)


@app.route('/approvePendingOrganismAdmin/', methods=['POST'])
def approvePendingOrganismAdmin():
    organismName = request.form.get('organism_name')
    errorMessage = "Must Include Organism Name When Approving"
    if organismName != "":
        cur.execute('UPDATE FarmItem '
                    'SET IsApproved = 1 '
                    'WHERE Name = %s', [organismName])
        conn.commit()
        errorMessage = ""
    cur.execute('SELECT Name, Type '
                'FROM FarmItem '
                'WHERE IsApproved = 0 '
                'ORDER BY ' + adminPendingCurrentSort)
    pendingOrganisms = cur.fetchall()
    return render_template('AdminPendingOrganisms.html', data=pendingOrganisms)


@app.route('/deletePendingOrganismsAdmin/', methods=['POST'])
def deletePendingOrganismsAdmin():
    organismName = request.form.get('organism_name')
    errorMessage = "Must Include Organism Name When Deleting"
    if organismName != "":
        cur.execute('DELETE FROM FarmItem '
                    'WHERE Name = %s', [organismName])
        conn.commit()
        errorMessage = ""
    cur.execute('SELECT Name, Type '
                'FROM FarmItem '
                'WHERE IsApproved = 0 '
                'ORDER BY ' + adminPendingCurrentSort)
    pendingOrganisms = cur.fetchall()
    return render_template('AdminPendingOrganisms.html', data=pendingOrganisms)


#Function clears the global lists that keeps track of what organisms were added and deleted in
#the admin manage property page to revert changes in case the admin presses the back button
def clearAddedAndDeletedOrganisms(flag):
    if flag == 1:
        global addedOrganismsConfirmedProperty
        global deletedOrganismsConfirmedProperty
        addedOrganismsConfirmedProperty = []
        deletedOrganismsConfirmedProperty = []
    else:
        global addedOrganismsUnconfirmedProperty
        global deletedOrganismsUnconfirmedProperty
        addedOrganismsUnconfirmedProperty = []
        deletedOrganismsUnconfirmedProperty = []


@app.route('/logout')
def logout():
    session['logged_in'] = False
    curUser = None
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
