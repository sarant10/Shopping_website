#Importing_flask_package
from flask import *
#Importing_sqllite3
import sqlite3
#Importing_hashlib
import hashlib
#Importing_OS
import os
#Importing_Secure_File
from werkzeug.utils import secure_filename

app = Flask(__name__)
#Random_String_for_App_securekey
app.secret_key = 'random string'
#setting_up_Path_For_Upload_Folder
UPLOAD_FOLDER = 'static/uploads'
#Allowing_Extension_For_image_file
ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#Function_for_login_carrying_Values
def Login_Detail():
    #Connecting_the_db_file
    with sqlite3.connect('storage.db') as Connections_cursor:
        #Commiting_the_connection
        cursorstring = Connections_cursor.cursor()
        #If_email_Id_is_not_in_session
        if 'email' not in session:
            loggedIn = False
            firstName = ''
            Number_of_Item = 0
            #The_Above_Vavlues_Will_be_Returned_false,null_and_zero
        else:
            #This_function_returns_the_numberofproductid,userid_and_FirstName_if_loggedin_is_true
            loggedIn = True
            cursorstring.execute("SELECT userId, firstName FROM users WHERE email = ?", (session['email'], ))
            userId, firstName = cursorstring.fetchone()
            #Fectching_the_count_of_the_productid
            cursorstring.execute("SELECT count(productId) FROM kart WHERE userId = ?", (userId, ))
            #Fetching_the_First_Rowofcount
            Number_of_Item = cursorstring.fetchone()[0]
    #Closing_the_Db_connection
    Connections_cursor.close()
    return (loggedIn, firstName, Number_of_Item)

#Index_routing_to_the_main_page
@app.route('/')
def index():
    return render_template("index.html")

#@app.route("/signedIn")
# def root():
#    loggedIn, firstName, Number_of_Item = Login_Detail()
#    with sqlite3.connect('storage.db') as Connections_cursor:
#        cursorstring = Connections_cursor.cursor()
#        cursorstring.execute('SELECT productId, name, price, description, image, stock FROM products')
#        itemData = cursorstring.fetchall()
#        cursorstring.execute('SELECT categoryId, name FROM categories')
#        categoryData = cursorstring.fetchall()
#    itemData = parse(itemData)   
#    return render_template('Product_home.html', itemData=itemData, loggedIn=loggedIn, firstName=firstName, Number_of_Item=Number_of_Item, #categoryData=categoryData)

#Adding_the_product
@app.route("/add")
def admin():
    with sqlite3.connect('storage.db') as Connections_cursor:
        cursorstring = Connections_cursor.cursor()
        #Fetching_the_data_from_Categories_Table
        cursorstring.execute("SELECT categoryId, name FROM categories")
        categories = cursorstring.fetchall()
    Connections_cursor.close()
    return render_template('Product_add.html', categories=categories)

#Adding_Items_to_the_cart
@app.route("/addItem", methods=["GET", "POST"])
def addItem():
    if request.method == "POST":
        pro_name = request.form['name']
        prod_price = float(request.form['price'])
        Prod_Descrip = request.form['description']
        Stoc_left = int(request.form['stock'])
        cat_Id = int(request.form['category'])

        #Uploading image procedure
        image = request.files['image']
        if image and allowed_file(image.file):
            #Secure_image_format
            file = secure_filename(image.file)
            #Defining_the_image_folder
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], file))
        imagename = file
        with sqlite3.connect('storage.db') as Connections_cursor:
            try:
                cursorstring = Connections_cursor.cursor()
                #Adding_the_Items_back_to_the_table
                cursorstring.execute('''INSERT INTO products (name, price, description, image, stock, categoryId) VALUES (?, ?, ?, ?, ?, ?)''', (pro_name, prod_price, Prod_Descrip, imagename, Stoc_left, cat_Id))
                Connections_cursor.commit()
                Message_Status="Added-successfull"
            except:
                Message_Status="Failed"
                Connections_cursor.rollback()
        Connections_cursor.close()
        print(Message_Status)
        return redirect(url_for('root'))

@app.route("/remove")
def remove():
    with sqlite3.connect('storage.db') as Connections_cursor:
        cursorstring = Connections_cursor.cursor()
        cursorstring.execute('SELECT productId, name, price, description, image, stock FROM products')
        Value = cursorstring.fetchall()
    Connections_cursor.close()
    return render_template('Product_remove.html', Value=Value)

@app.route("/Item_remove")
def Item_remove():
    productId = request.args.get('productId')
    with sqlite3.connect('storage.db') as Connections_cursor:
        try:
            cursorstring = Connections_cursor.cursor()
            cursorstring.execute('DELETE FROM products WHERE productID = ?', (productId, ))
            Connections_cursor.commit()
            Message_Status = "Successful deletion"
        except:
            Connections_cursor.rollback()
            Message_Status = "Error"
    Connections_cursor.close()
    print(Message_Status)
    return redirect(url_for('root'))

@app.route("/displayCategory")
def displayCategory():
        loggedIn, firstName, Number_of_Item = Login_Detail()
        categ_Id = request.args.get("categoryId")
        with sqlite3.connect('storage.db') as Connections_cursor:
            cursorstring = Connections_cursor.cursor()
            cursorstring.execute("SELECT products.productId, products.name, products.price, products.image, categories.name FROM products, categories WHERE products.categoryId = categories.categoryId AND categories.categoryId = ?", (categ_Id, ))
            Value = cursorstring.fetchall()
        Connections_cursor.close()
        categoryName = Value[0][4]
        Value = parse(Value)
        return render_template('Product_displayCategory.html', Value=Value, loggedIn=loggedIn, firstName=firstName, Number_of_Item=Number_of_Item, categoryName=categoryName)

@app.route("/account/profile")
def profileHome():
    if 'email' not in session:
        return redirect(url_for('root'))
    loggedIn, firstName, Number_of_Item = Login_Detail()
    return render_template("Prod_Profil.html", loggedIn=loggedIn, firstName=firstName, Number_of_Item=Number_of_Item)

@app.route("/account/profile/edit")
def editProfile():
    if 'email' not in session:
        return redirect(url_for('root'))
    loggedIn, firstName, Number_of_Item = Login_Detail()
    with sqlite3.connect('storage.db') as Connections_cursor:
        cursorstring = Connections_cursor.cursor()
        cursorstring.execute("SELECT userId, email, firstName, lastName, address1, address2, zipcode, city, state, country, phone FROM users WHERE email = ?", (session['email'], ))
        profileData = cursorstring.fetchone()
    Connections_cursor.close()
    return render_template("Product_editProfile.html", profileData=profileData, loggedIn=loggedIn, firstName=firstName, Number_of_Item=Number_of_Item)

'''
@app.route("/login", methods = ['POST', 'GET'])
def login():
    if 'email' in session:
        return redirect(url_for('root'))
    elif 'email' not in session:
        return render_template('login.html', error='')
    elif request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
    elif is_valid(email, password):
        session['email'] = email
        return render_template('index.html')
    else:
        error = 'Invalid - credentials'
        return render_template('login.html', error=error)
'''


@app.route("/Login_page")
def Login_page():
    if 'email' in session:
        return redirect(url_for('root'))
    else:
        return render_template('login.html', error='')

@app.route("/login", methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if is_valid(email, password):
            session['email'] = email
            return render_template('index.html')
        else:
            error = 'Invalid userId / Password'
            return render_template('login.html', error=error)

@app.route("/productDescription")
def productDescription():
    loggedIn, firstName, Number_of_Item = Login_Detail()
    productId = request.args.get('productId')
    with sqlite3.connect('storage.db') as Connections_cursor:
        cursorstring = Connections_cursor.cursor()
        cursorstring.execute('SELECT productId, name, price, description, image, stock FROM products WHERE productId = ?', (productId, ))
        productData = cursorstring.fetchone()
    Connections_cursor.close()
    return render_template("Product_Description.html", Value=productData, loggedIn = loggedIn, firstName = firstName, Number_of_Item = Number_of_Item)

@app.route("/add_cart")
def add_cart():
    if 'email' not in session:
        return redirect(url_for('Login_page'))
    else:
        productId = int(request.args.get('productId'))
        with sqlite3.connect('storage.db') as Connections_cursor:
            cursorstring = Connections_cursor.cursor()
            cursorstring.execute("SELECT userId FROM users WHERE email = ?", (session['email'], ))
            userId = cursorstring.fetchone()[0]
            try:
                cursorstring.execute("INSERT INTO kart (userId, productId) VALUES (?, ?)", (userId, productId))
                Connections_cursor.commit()
                Message_Status = "Added successfully"
            except:
                Connections_cursor.rollback()
                Message_Status = "Error occured"
        Connections_cursor.close()
        return redirect(url_for('root'))

@app.route("/cart")
def cart():
    if 'email' not in session:
        return redirect(url_for('Login_page'))
    loggedIn, firstName, Number_of_Item = Login_Detail()
    email = session['email']
    with sqlite3.connect('storage.db') as Connections_cursor:
        cursorstring = Connections_cursor.cursor()
        cursorstring.execute("SELECT userId FROM users WHERE email = ?", (email, ))
        userId = cursorstring.fetchone()[0]
        cursorstring.execute("SELECT products.productId, products.name, products.price, products.image FROM products, kart WHERE products.productId = kart.productId AND kart.userId = ?", (userId, ))
        products = cursorstring.fetchall()
    totalPrice = 0
    for row in products:
        totalPrice += row[2]
    return render_template("Product_cart.html", products = products, totalPrice=totalPrice, loggedIn=loggedIn, firstName=firstName, Number_of_Item=Number_of_Item)

@app.route("/removeFromCart")
def removeFromCart():
    if 'email' not in session:
        return redirect(url_for('Login_page'))
    email = session['email']
    productId = int(request.args.get('productId'))
    with sqlite3.connect('storage.db') as Connections_cursor:
        cursorstring = Connections_cursor.cursor()
        cursorstring.execute("SELECT userId FROM users WHERE email = ?", (email, ))
        userId = cursorstring.fetchone()[0]
        try:
            cursorstring.execute("DELETE FROM kart WHERE userId = ? AND productId = ?", (userId, productId))
            Connections_cursor.commit()
            Message_Status = "removed successfully"
        except:
            Connections_cursor.rollback()
            Message_Status = "error occured"
    Connections_cursor.close()
    return redirect(url_for('root'))

@app.route("/logout")
def logout():
    session.pop('email', None)
    return redirect(url_for('root'))

def is_valid(email, password):
    Connections_cursor = sqlite3.connect('storage.db')
    cursorstring = Connections_cursor.cursor()
    cursorstring.execute('SELECT email, password FROM users')
    Value = cursorstring.fetchall()
    for row in Value:
        if row[0] == email and row[1] == hashlib.md5(password.encode()).hexdigest():
            return True
    return False

#function_to_get_and_post_registration_page
@app.route("/register", methods = ['GET', 'POST'])
def register():
    #IF_the_request_from_the_front_end_is_post
    if request.method == 'POST':
        #Parsing_the_form_data   
        # All the values are collected in string and passed to the database 
        Pass_wor = request.form['password']
        mail_id = request.form['email']
        First_nam = request.form['firstName']
        last_Nam = request.form['lastName']
        Add1 = request.form['address1']
        Add2 = request.form['address2']
        city = request.form['city']
        Postal_code = request.form['zipcode']
        Coun_try = request.form['country']
        state = request.form['state']
        Tele_phone = request.form['phone']

        with sqlite3.connect('storage.db') as Connections_cursor:
            try:
                cursorstring = Connections_cursor.cursor()
                cursorstring.execute('INSERT INTO users (password, email, firstName, lastName, address1, address2, zipcode, city, state, country, phone) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (hashlib.md5(Pass_wor.encode()).hexdigest(), mail_id, First_nam, last_Nam, Add1, Add2, Postal_code, city, state, Coun_try, Tele_phone))

                Connections_cursor.commit()

                Message_Status = "Registered"
            except:
                Connections_cursor.rollback()
                Message_Status = "Error"
        Connections_cursor.close()
        return render_template("Product_login.html", error=Message_Status)

@app.route("/registerationForm")
def registrationForm():
    return render_template("register.html")

def allowed_file(file):
    return '.' in file and \
            file.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def parse(Value):
    answer = []
    Valuei = 0
    while Valuei < len(Value):
        concurrent = []
        for j in range(7):
            if Valuei >= len(Value):
                break
            concurrent.append(Value[Valuei])
            Valuei += 1
        answer.append(concurrent)
    return answer

if __name__ == '__main__':
    app.run(debug=True)
