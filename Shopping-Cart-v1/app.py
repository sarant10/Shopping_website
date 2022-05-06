from flask import *
import sqlite3, hashlib, os
#from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'random string'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def detailed_login():
    with sqlite3.connect('database.db') as data_connect:
        data_cursor = data_connect.cursor()
        if 'email_id' not in session:
            login_check = False
            First_Name = ''
            Item_quantity = 0
        else:
            login_check = True
            data_cursor.execute("SELECT userId, firstName FROM users WHERE email_id = ?", (session['email_id'], ))
            userId, First_Name = data_cursor.fetchone()
            data_cursor.execute("SELECT count(productId) FROM kart WHERE userId = ?", (userId, ))
            Item_quantity = data_cursor.fetchone()[0]
    data_connect.close()
    return (login_check, First_Name, Item_quantity)

@app.route("/")
def root():
    login_check, First_Name, Item_quantity = detailed_login()
    with sqlite3.connect('database.db') as data_connect:
        data_cursor = data_connect.cursor()
        data_cursor.execute('SELECT productId, item_name, item_cost, item_spec, image, stock FROM products')
        itemData = data_cursor.fetchall()
        data_cursor.execute('SELECT Cat_Id, item_name FROM categories')
        categoryData = data_cursor.fetchall()
    itemData = parse(itemData)   
    return render_template('item_home.html', itemData=itemData, login_check=login_check, First_Name=First_Name, Item_quantity=Item_quantity, categoryData=categoryData)

@app.route("/add")
def ad_min():
    with sqlite3.connect('database.db') as data_connect:
        data_cursor = data_connect.cursor()
        data_cursor.execute("SELECT Cat_Id, item_name FROM categories")
        categories = data_cursor.fetchall()
    data_connect.close()
    return render_template('item_add.html', categories=categories)

@app.route("/addItem", methods=["GET", "POST"])
def addItem():
    if request.method == "POST":
        name = request.form['item_name']
        price = float(request.form['item_cost'])
        description = request.form['item_spec']
        stock = int(request.form['stock'])
        categoryId = int(request.form['category'])

        #Uploading image procedure
        image = request.files['image']
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        imagename = filename
        with sqlite3.connect('database.db') as data_connect:
            try:
                data_cursor = data_connect.cursor()
                data_cursor.execute('''INSERT INTO products (item_name, item_cost, item_spec, image, stock, Cat_Id) VALUES (?, ?, ?, ?, ?, ?)''', (name, price, description, imagename, stock, categoryId))
                data_connect.commit()
                msg="added successfully"
            except:
                msg="error occured"
                data_connect.rollback()
        data_connect.close()
        print(msg)
        return redirect(url_for('root'))

@app.route("/remove")
def remove():
    with sqlite3.connect('database.db') as data_connect:
        data_cursor = data_connect.cursor()
        data_cursor.execute('SELECT productId, item_name, item_cost, item_spec, image, stock FROM products')
        data = data_cursor.fetchall()
    data_connect.close()
    return render_template('product_remove.html', data=data)

@app.route("/removeItem")
def removeItem():
    productId = request.args.get('productId')
    with sqlite3.connect('database.db') as data_connect:
        try:
            data_cursor = data_connect.cursor()
            data_cursor.execute('DELETE FROM products WHERE productID = ?', (productId, ))
            data_connect.commit()
            msg = "Deleted successsfully"
        except:
            data_connect.rollback()
            msg = "Error occured"
    data_connect.close()
    print(msg)
    return redirect(url_for('root'))

@app.route("/displayCategory")
def displayCategory():
        login_check, First_Name, Item_quantity = detailed_login()
        categoryId = request.args.get("Cat_Id")
        with sqlite3.connect('database.db') as data_connect:
            data_cursor = data_connect.cursor()
            data_cursor.execute("SELECT products.productId, products.item_name, products.item_cost, products.image, categories.item_name FROM products, categories WHERE products.Cat_Id = categories.Cat_Id AND categories.Cat_Id = ?", (categoryId, ))
            data = data_cursor.fetchall()
        data_connect.close()
        categoryName = data[0][4]
        data = parse(data)
        return render_template('item_display.html', data=data, login_check=login_check, First_Name=First_Name, Item_quantity=Item_quantity, categoryName=categoryName)

@app.route("/account/profile")
def profileHome():
    if 'email_id' not in session:
        return redirect(url_for('root'))
    login_check, First_Name, Item_quantity = detailed_login()
    return render_template("Home_profile.html", login_check=login_check, First_Name=First_Name, Item_quantity=Item_quantity)

@app.route("/account/profile/edit")
def Profile_edit():
    if 'email_id' not in session:
        return redirect(url_for('root'))
    login_check, First_Name, Item_quantity = detailed_login()
    with sqlite3.connect('database.db') as data_connect:
        data_cursor = data_connect.cursor()
        data_cursor.execute("SELECT userId, email_id, firstName, lastName, address1, zipcode, city, country, phone FROM users WHERE email_id = ?", (session['email_id'], ))
        profileData = data_cursor.fetchone()
    data_connect.close()
    return render_template("Profile edit.html", profileData=profileData, login_check=login_check, First_Name=First_Name, Item_quantity=Item_quantity)

@app.route("/account/profile/changePassword", methods=["GET", "POST"])
def changePassword():
    if 'email_id' not in session:
        return redirect(url_for('loginForm'))
    if request.method == "POST":
        oldPassword = request.form['oldpassword']
        oldPassword = hashlib.md5(oldPassword.encode()).hexdigest()
        newPassword = request.form['newpassword']
        newPassword = hashlib.md5(newPassword.encode()).hexdigest()
        with sqlite3.connect('database.db') as data_connect:
            data_cursor = data_connect.cursor()
            data_cursor.execute("SELECT userId, password FROM users WHERE email_id = ?", (session['email_id'], ))
            userId, password = data_cursor.fetchone()
            if (password == oldPassword):
                try:
                    data_cursor.execute("UPDATE users SET password = ? WHERE userId = ?", (newPassword, userId))
                    data_connect.commit()
                    msg="Changed successfully"
                except:
                    data_connect.rollback()
                    msg = "Failed"
                return render_template("Password_change.html", msg=msg)
            else:
                msg = "Wrong password"
        data_connect.close()
        return render_template("Password_change.html", msg=msg)
    else:
        return render_template("Password_change.html")

@app.route("/updateProfile", methods=["GET", "POST"])
def updateProfile():
    if request.method == 'POST':
        email_id = request.form['email_id']
        First_Name = request.form['firstName']
        lastName = request.form['lastName']
        address1 = request.form['address1']
        zipcode = request.form['zipcode']
        city = request.form['city']
        country = request.form['country']
        phone = request.form['phone']
        with sqlite3.connect('database.db') as con:
                try:
                    data_cursor = con.cursor()
                    data_cursor.execute('UPDATE users SET firstName = ?, lastName = ?, address1 = ?, zipcode = ?, city = ?, country = ?, phone = ? WHERE email_id = ?', (First_Name, lastName, address1, zipcode, city, country, phone, email_id))

                    con.commit()
                    msg = "Saved Successfully"
                except:
                    con.rollback()
                    msg = "Error occured"
        con.close()
        return redirect(url_for('Profile_edit'))

@app.route("/loginForm")
def loginForm():
    if 'email_id' in session:
        return redirect(url_for('root'))
    else:
        return render_template('log_in.html', error='')

@app.route("/login", methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        email_id = request.form['email_id']
        password = request.form['password']
        if is_valid(email_id, password):
            session['email_id'] = email_id
            return redirect(url_for('root'))
        else:
            error = 'Invalid UserId / Password'
            return render_template('log_in.html', error=error)

@app.route("/productDescription")
def productDescription():
    login_check, First_Name, Item_quantity = detailed_login()
    productId = request.args.get('productId')
    with sqlite3.connect('database.db') as data_connect:
        data_cursor = data_connect.cursor()
        data_cursor.execute('SELECT productId, item_name, item_cost, item_spec, image, stock FROM products WHERE productId = ?', (productId, ))
        productData = data_cursor.fetchone()
    data_connect.close()
    return render_template("prd_Des.html", data=productData, login_check = login_check, First_Name = First_Name, Item_quantity = Item_quantity)

@app.route("/addToCart")
def addToCart():
    if 'email_id' not in session:
        return redirect(url_for('loginForm'))
    else:
        productId = int(request.args.get('productId'))
        with sqlite3.connect('database.db') as data_connect:
            data_cursor = data_connect.cursor()
            data_cursor.execute("SELECT userId FROM users WHERE email_id = ?", (session['email_id'], ))
            userId = data_cursor.fetchone()[0]
            try:
                data_cursor.execute("INSERT INTO kart (userId, productId) VALUES (?, ?)", (userId, productId))
                data_connect.commit()
                msg = "Added successfully"
            except:
                data_connect.rollback()
                msg = "Error occured"
        data_connect.close()
        return redirect(url_for('root'))

@app.route("/cart")
def cart():
    if 'email_id' not in session:
        return redirect(url_for('loginForm'))
    login_check, First_Name, Item_quantity = detailed_login()
    email_id = session['email_id']
    with sqlite3.connect('database.db') as data_connect:
        data_cursor = data_connect.cursor()
        data_cursor.execute("SELECT userId FROM users WHERE email_id = ?", (email_id, ))
        userId = data_cursor.fetchone()[0]
        data_cursor.execute("SELECT products.productId, products.item_name, products.item_cost, products.image FROM products, kart WHERE products.productId = kart.productId AND kart.userId = ?", (userId, ))
        products = data_cursor.fetchall()
    totalPrice = 0
    for row in products:
        totalPrice += row[2]
    return render_template("item_cart.html", products = products, totalPrice=totalPrice, login_check=login_check, First_Name=First_Name, Item_quantity=Item_quantity)

@app.route("/removeFromCart")
def removeFromCart():
    if 'email_id' not in session:
        return redirect(url_for('loginForm'))
    email_id = session['email_id']
    productId = int(request.args.get('productId'))
    with sqlite3.connect('database.db') as data_connect:
        data_cursor = data_connect.cursor()
        data_cursor.execute("SELECT userId FROM users WHERE email_id = ?", (email_id, ))
        userId = data_cursor.fetchone()[0]
        try:
            data_cursor.execute("DELETE FROM kart WHERE userId = ? AND productId = ?", (userId, productId))
            data_connect.commit()
            msg = "removed successfully"
        except:
            data_connect.rollback()
            msg = "error occured"
    data_connect.close()
    return redirect(url_for('root'))

@app.route("/logout")
def logout():
    session.pop('email_id', None)
    return redirect(url_for('root'))

def is_valid(email_id, password):
    con = sqlite3.connect('database.db')
    data_cursor = con.cursor()
    data_cursor.execute('SELECT email_id, password FROM users')
    data = data_cursor.fetchall()
    for row in data:
        if row[0] == email_id and row[1] == hashlib.md5(password.encode()).hexdigest():
            return True
    return False

@app.route("/register", methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        #Parse form data    
        password = request.form['password']
        email_id = request.form['email_id']
        First_Name = request.form['firstName']
        lastName = request.form['lastName']
        address1 = request.form['address1']
        zipcode = request.form['zipcode']
        city = request.form['city']
        country = request.form['country']
        phone = request.form['phone']

        with sqlite3.connect('database.db') as con:
            try:
                data_cursor = con.cursor()
                data_cursor.execute('INSERT INTO users (password, email_id, firstName, lastName, address1, zipcode, city, country, phone) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (hashlib.md5(password.encode()).hexdigest(), email_id, First_Name, lastName, address1, zipcode, city, country, phone))

                con.commit()

                msg = "Registered Successfully"
            except:
                con.rollback()
                msg = "Error occured"
        con.close()
        return render_template("log_in.html", error=msg)

@app.route("/registerationForm")
def registrationForm():
    return render_template("profile_register.html")

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def parse(data):
    result = []
    x = 0
    while x < len(data):
        z = []
        for y in range(7):
            if x >= len(data):
                break
            z.append(data[x])
            x += 1
        result.append(z)
    return result

if __name__ == '__main__':
    app.run(debug=True)
