#importing flask
from flask import *
#Importing_sql_database
import sqlite3
#Importing_libr
import hashlib
#importing_os
import os


app = Flask(__name__)
#providing_pathfor_folderupload
UPLOAD_FOLDER = 'static/uploads'
#Providing_randomstringfor_secretkey
app.secret_key = 'random string'
#imageformat_extensions
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'gif','jpeg'])
#Appconfigurationfor_folderupload
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



#Func_to_fetch_num_of_items_if_the_useris_already_loggedin
def detailed_login():
    #establising_connection_to_the_database
    with sqlite3.connect('database.db') as data_connect:
        #Connection_to_the_data_base
        data_cursor = data_connect.cursor()
        #If_emailid_not_in_session_the_value_returns_false_blank_zero
        if 'email_id' not in session:
            #Log_in_will_be_false
            login_check = False
            #First_name_returns_blank
            First_Name = ''
            #Item_quantiy_will_be_zero
            Item_quantity = 0
        else:
            login_check = True
            #Selecting_the_user_saved_under_session
            data_cursor.execute("SELECT userId, firstName FROM users WHERE email_id = ?", (session['email_id'], ))
            userId, First_Name = data_cursor.fetchone()
            #Fetching_the_count_of_Product_id_from_Kart
            data_cursor.execute("SELECT count(productId) FROM kart WHERE userId = ?", (userId, ))
            #Fetch_the_First_row_in_the_output
            Item_quantity = data_cursor.fetchone()[0]
            #Closing_the_connection
    data_connect.close()
    #Values_returned_for_above_function
    return (login_check, First_Name, Item_quantity)

@app.route("/")
def root():
    #Getting_the_values_from_detailed_login_and_assigning_it_to_these_below_mentioned_values
    login_check, First_Name, Item_quantity = detailed_login()
    with sqlite3.connect('database.db') as data_connect:
        data_cursor = data_connect.cursor()
        #Getting_prod_detail_from_the_table
        data_cursor.execute('SELECT productId, item_name, item_cost, item_spec, image, stock FROM products')
        itemData = data_cursor.fetchall()
        #Pulling_Cart_id_Item_name
        data_cursor.execute('SELECT Cat_Id, item_name FROM categories')
        categoryData = data_cursor.fetchall()
    itemData = parse(itemData)   
    return render_template('item_home.html', itemData=itemData, login_check=login_check, First_Name=First_Name, Item_quantity=Item_quantity, categoryData=categoryData)

@app.route("/add")
def ad_min():
    with sqlite3.connect('database.db') as data_connect:
        data_cursor = data_connect.cursor()
        #Gettting_caritems_from_the_table
        data_cursor.execute("SELECT Cat_Id, item_name FROM categories")
        categories = data_cursor.fetchall()
    data_connect.close()
    #Redirecting_to_the_item_add_html
    return render_template('item_add.html', categories=categories)

from werkzeug.utils import secure_filename

@app.route("/addItem", methods=["GET", "POST"])
def addItem():
    if request.method == "POST":
        #Getting_the_Item_name_and_assigning_it_to_variable
        name = request.form['item_name']
        #Pulling_the_product_cost_and_assigning_it_to_price
        price = float(request.form['item_cost'])
        #Pulling_itm_specification_and_assigning_it_to_description
        description = request.form['item_spec']
        #Pulling_the_integer_stoc
        stock = int(request.form['stock'])
        #Pulling_the_catogoryas_int
        categoryId = int(request.form['category'])

        #Uploading image procedure
        image = request.files['image']
        if image and allowed_file(image.filename):
            #Secur_the_file_name
            filename = secure_filename(image.filename)
            #Upload_path_For_the_image
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            #Assign_the_file_to_image
        imagename = filename
        with sqlite3.connect('database.db') as data_connect:
            try:
                data_cursor = data_connect.cursor()
                #Inserting_data_into_prod_tabel
                data_cursor.execute('''INSERT INTO products (item_name, item_cost, item_spec, image, stock, Cat_Id) VALUES (?, ?, ?, ?, ?, ?)''', (name, price, description, imagename, stock, categoryId))
                data_connect.commit()
                msg="Successfully Added"
            except:
                msg="Error - Try Again!"
                data_connect.rollback()
        data_connect.close()
        #Printing_success_or_error_message
        print(msg)
        #Redirect_to_the_root
        return redirect(url_for('root'))

#Removing_the_prod_from_cart
@app.route("/remove")
def remove():
    with sqlite3.connect('database.db') as data_connect:
        data_cursor = data_connect.cursor()
        #Selecting_the_Product_details
        data_cursor.execute('SELECT productId, item_name, item_cost, item_spec, image, stock FROM products')
        data = data_cursor.fetchall()
    data_connect.close()
    #Rendering_to_product_remove_page
    return render_template('product_remove.html', data=data)

#Function_to_remove_item
@app.route("/removeItem")
def removeItem():
    #Getting_the_product_ID
    productId = request.args.get('productId')
    #Connection_to_database
    with sqlite3.connect('database.db') as data_connect:
        try:
            data_cursor = data_connect.cursor()
            #Deleting_the_fetched_prod_id
            data_cursor.execute('DELETE FROM products WHERE productID = ?', (productId, ))
            data_connect.commit()
            msg = "Successfully Deleted"
        except:
            #If_unsuccessfull_rolling_Back_to_the_previous_state
            data_connect.rollback()
            msg = "Error"
    data_connect.close()
    #Printing_success_or_error_message
    print(msg)
    #Redirect_to_the_root
    return redirect(url_for('root'))

#Function_for_display_category
@app.route("/displayCategory")
def displayCategory():
        #Getting_the_information_from_detailed_login_page
        login_check, First_Name, Item_quantity = detailed_login()
        #Requesting_the_id
        categoryId = request.args.get("Cat_Id")
        with sqlite3.connect('database.db') as data_connect:
            data_cursor = data_connect.cursor()
            #Selecting_the_prod_details_from_produ_ct_table
            data_cursor.execute("SELECT products.productId, products.item_name, products.item_cost, products.image, categories.item_name FROM products, categories WHERE products.Cat_Id = categories.Cat_Id AND categories.Cat_Id = ?", (categoryId, ))
            data = data_cursor.fetchall()
        data_connect.close()
        categoryName = data[0][4]
        #Parsing_the_data
        data = parse(data)
        #returning_the_values_taken_from_prod_table
        return render_template('item_display.html', data=data, login_check=login_check, First_Name=First_Name, Item_quantity=Item_quantity, categoryName=categoryName)

#Function_to_write_profile_home
@app.route("/account/profile")
def profileHome():
    #Checking_if_the_user_is_not_Logged_in
    if 'email_id' not in session:
        #If_not_logged_in_redirecting_to_the_root
        return redirect(url_for('root'))
    login_check, First_Name, Item_quantity = detailed_login()
    return render_template("Home_profile.html", login_check=login_check, First_Name=First_Name, Item_quantity=Item_quantity)

#Function_to_edit_profile
@app.route("/account/profile/edit")
def Profile_edit():
    #If_user_not_logged_in
    if 'email_id' not in session:
        return redirect(url_for('root'))
    login_check, First_Name, Item_quantity = detailed_login()
    with sqlite3.connect('database.db') as data_connect:
        data_cursor = data_connect.cursor()
        #Fetching_data_from_users_table
        data_cursor.execute("SELECT userId, email_id, firstName, lastName, address1, zipcode, city, country, phone FROM users WHERE email_id = ?", (session['email_id'], ))
        profileData = data_cursor.fetchone()
    data_connect.close()
    #Rendering_to_profile_edit_page
    return render_template("Profile edit.html", profileData=profileData, login_check=login_check, First_Name=First_Name, Item_quantity=Item_quantity)

#Function_to_change_pass_word
@app.route("/account/profile/changePassword", methods=["GET", "POST"])
def changePassword():
    #Checking_if_the_user_is_still_Logged_in
    if 'email_id' not in session:
        return redirect(url_for('loginForm'))
        #Posting_the_method
    if request.method == "POST":
        #Fetching_the_old_pass_wrd
        oldPassword = request.form['oldpassword']
        #Encoding_the_pass_wrd
        oldPassword = hashlib.md5(oldPassword.encode()).hexdigest()
        #Fetching_new_pass_wrd
        newPassword = request.form['newpassword']
        #Encoding_the_new_pass_wrd
        newPassword = hashlib.md5(newPassword.encode()).hexdigest()
        #Establishing_connection_to_the_Db
        with sqlite3.connect('database.db') as data_connect:
            data_cursor = data_connect.cursor()
            #Pulling_userdata_of_logged_in_user
            data_cursor.execute("SELECT userId, password FROM users WHERE email_id = ?", (session['email_id'], ))
            userId, password = data_cursor.fetchone()
            #If_it_is_a_change_the_value_gets_updated
            if (password == oldPassword):
                try:
                    #queryfor_appending_the_Pass_wrd
                    data_cursor.execute("UPDATE users SET password = ? WHERE userId = ?", (newPassword, userId))
                    data_connect.commit()
                    #commit_confimation_string
                    msg="Success"
                except:
                    data_connect.rollback()
                    #Commit_failure_string
                    msg = "Request Failed"
                    #Redirecting_to_pass_wrd_change_html
                return render_template("Password_change.html", msg=msg)
            else:
                msg = "password entered wrong"
        data_connect.close()
        #Redirecting_to_pass_wrd_change_html
        return render_template("Password_change.html", msg=msg)
    else:
        #Redirecting_to_pass_wrd_change_html
        return render_template("Password_change.html")

#Function_to_update_user_account
@app.route("/updateProfile", methods=["GET", "POST"])
def updateProfile():
    #If_the_request_is_post
    if request.method == 'POST':
        #Fectchng_the_email
        email_id = request.form['email_id']
        #Fectchng_the_frst_name
        First_Name = request.form['firstName']
        #Fectchng_the_last_nam
        lastName = request.form['lastName']
        #Fectchng_the_redince_loaction
        address1 = request.form['address1']
        #Fectchng_the_redince_postal_code
        zipcode = request.form['zipcode']
        #Fectchng_the_town
        city = request.form['city']
        #Fectchng_the_redince_nation
        country = request.form['country']
        #Fectchng_the_redince_telephone
        phone = request.form['phone']
        with sqlite3.connect('database.db') as data_connect:
                try:
                    data_cursor = data_connect.cursor()
                    #Query_to_update_the_profile_tabel
                    data_cursor.execute('UPDATE users SET firstName = ?, lastName = ?, address1 = ?, zipcode = ?, city = ?, country = ?, phone = ? WHERE email_id = ?', (First_Name, lastName, address1, zipcode, city, country, phone, email_id))
                    data_connect.commit()
                    #Printing_Message
                    msg = "Successful"
                except:
                    #Rolling_back_the_function
                    data_connect.rollback()
                    msg = "Error - Try Again!"
        data_connect.close()
        #Redirecting_to_profile_edit
        return redirect(url_for('Profile_edit'))

#Function_to_login_navigation_page
@app.route("/loginForm")
def loginForm():
    #if_the_user_still_logged_in
    if 'email_id' in session:
        #nagivate_to_the_root
        return redirect(url_for('root'))
    else:
        #Navigate_to_the_log_in_page
        return render_template('log_in.html', error='')

#Function_to_check_the_user_credentials
@app.route("/login", methods = ['POST', 'GET'])
def login():
    #If_the_Request_method_is_post
    if request.method == 'POST':
        #Getting_the_email_id_and_pass_wrd_from_front_end
        email_id = request.form['email_id']
        #Getting_the_pass_wrd
        password = request.form['password']
        #If_the_validation_is_correct
        if is_valid(email_id, password):
            #Assigning_the_email_id_to_the_session
            session['email_id'] = email_id
            #Navigating_to_the_root
            return redirect(url_for('root'))
        else:
            #Printing_error_message
            error = 'Invalid Credentials! Try Again!'
            #Navigation_to_the_login_page_again
            return render_template('log_in.html', error=error)

#Function_for_product_description
@app.route("/productDescription")
def productDescription():
    #Fetching_the_detailed_login_values
    login_check, First_Name, Item_quantity = detailed_login()
    #Getting_the_product_number
    productId = request.args.get('productId')
    with sqlite3.connect('database.db') as data_connect:
        data_cursor = data_connect.cursor()
        #Selecting_prod_from_stock_table
        data_cursor.execute('SELECT productId, item_name, item_cost, item_spec, image, stock FROM products WHERE productId = ?', (productId, ))
        productData = data_cursor.fetchone()
    data_connect.close()
    #Redirecting_to_the_prd_des_page.
    return render_template("prd_Des.html", data=productData, login_check = login_check, First_Name = First_Name, Item_quantity = Item_quantity)

#Adding_cart_items
@app.route("/addToCart")
#function_to_add_cart
def addToCart():
    #If_user_not_logged_in
    if 'email_id' not in session:
        #Redirect_the_page_to_loginform
        return redirect(url_for('loginForm'))
    else:
        #fetching_the_productid_data
        productId = int(request.args.get('productId'))
        #Establising_connection_to_the_database.
        with sqlite3.connect('database.db') as data_connect:
            data_cursor = data_connect.cursor()
            #Selecting_user_data_with_the_help_of_session_id
            data_cursor.execute("SELECT userId FROM users WHERE email_id = ?", (session['email_id'], ))
            #Getting_the_first_row
            userId = data_cursor.fetchone()[0]
            try:
                #inserting_values_to_the_cart
                data_cursor.execute("INSERT INTO kart (userId, productId) VALUES (?, ?)", (userId, productId))
                data_connect.commit()
                #Satatus_message
                msg = "Successfull"
            except:
                #function_to_rol_l
                data_connect.rollback()
                #Status_message
                msg = "Error"
        #closing_the_connection
        data_connect.close()
        #Redirecting_to_the_root
        return redirect(url_for('root'))

#Function_For_Cart
@app.route("/cart")
def cart():
    #if_the_user_not_logged_in
    if 'email_id' not in session:
        #redurect_to_lgoin_page
        return redirect(url_for('loginForm'))
        #Getting_data_from_detailed_login
    login_check, First_Name, Item_quantity = detailed_login()
    #assigning_the_email_id_to_session
    email_id = session['email_id']
    #establishing_connection_to_the_Db
    with sqlite3.connect('database.db') as data_connect:
        data_cursor = data_connect.cursor()
        #Selecting_data_from_customer_table_passing_session_value
        data_cursor.execute("SELECT userId FROM users WHERE email_id = ?", (email_id, ))
        #Feching_first_row
        userId = data_cursor.fetchone()[0]
        #Selecting_values_from_products_table
        data_cursor.execute("SELECT products.productId, products.item_name, products.item_cost, products.image FROM products, kart WHERE products.productId = kart.productId AND kart.userId = ?", (userId, ))
        products = data_cursor.fetchall()
        #Declaring_total_price_to_zero
    totalPrice = 0
    for row in products:
        #pushing_the_value_to_row_two
        totalPrice += row[2]
        #redirecting_to_the_item_cart_page
    return render_template("item_cart.html", products = products, totalPrice=totalPrice, login_check=login_check, First_Name=First_Name, Item_quantity=Item_quantity)

'''
@app.route('/payment_gateway')
def index():
    return render_template('payment.html', key=stripe_keys['publishable_key'])

@app.route('/charge', methods=['POST'])
totalPrice = cart()
def charge():
    # Amount in cents
    amount = totalPrice
    customer = stripe.Customer.create(
        email='customer@example.com',
        source=request.form['stripeToken']
    )
    charge = stripe.Charge.create(
        customer=customer.id,
        amount=amount,
        currency='pounds',
        description='Shopping Payment'
    )
    return render_template('payment_base.html', amount=amount)
'''



#Removing_the_product_function
@app.route("/removeFromCart")
def removeFromCart():
    #if_the_user_not_logged_in
    if 'email_id' not in session:
        #Redirect_to_log_in_page
        return redirect(url_for('loginForm'))
    #assigning_sesson_to_variable
    email_id = session['email_id']
    #Getting_product_number
    productId = int(request.args.get('productId'))
    #establishing_connection
    with sqlite3.connect('database.db') as data_connect:
        data_cursor = data_connect.cursor()
        #Selecting_values_from_profile_table
        data_cursor.execute("SELECT userId FROM users WHERE email_id = ?", (email_id, ))
        #Fetching_the_first_row
        userId = data_cursor.fetchone()[0]
        try:
            #Script_to_remove_the_prod_form_basket
            data_cursor.execute("DELETE FROM kart WHERE userId = ? AND productId = ?", (userId, productId))
            data_connect.commit()
            #Satatus_message
            msg = "Removed"
        except:
            #Function_to_roll_back
            data_connect.rollback()
            #Status_message
            msg = "Error - Try Again!"
    data_connect.close()
    #Redirecting_to_rot_page
    return redirect(url_for('root'))

#Function_to_log_out
@app.route("/logout")
def logout():
    #If_sesson_is_null
    session.pop('email_id', None)
    #Redirect_to_rot_page
    return redirect(url_for('root'))

#Function_to_validation_user_name_and_password
def is_valid(email_id, password):
    #Connection_to_the_Databse
    data_connect = sqlite3.connect('database.db')
    data_cursor = data_connect.cursor()
    #Getting_the_user_credentials_to_the_table
    data_cursor.execute('SELECT email_id, password FROM users')
    #Getting_all_the_record
    data = data_cursor.fetchall()
    #Checking_all_the_credentials_in_talbe
    for row in data:
        #If_the_credentials_are_correct_then_the_loop_returns_true
        if row[0] == email_id and row[1] == hashlib.md5(password.encode()).hexdigest():
            #value_returns_positive
            return True
    return False

#Function_to_regist_ter_the_user
@app.route("/register", methods = ['GET', 'POST'])
def register():
    #if_the_method_is_post
    if request.method == 'POST':
        #Getting_the_data_from_front_end_for_pass_word    
        password = request.form['password']
        #Getting_the_data_from_front_end_for_gmail
        email_id = request.form['email_id']
        #Getting_the_data_from_front_end_for_user_fore_name
        First_Name = request.form['firstName']
        #Getting_the_data_from_front_end_for_user_last_name
        lastName = request.form['lastName']
        #Getting_the_data_from_front_end_for_user_add
        address1 = request.form['address1']
        #Getting_the_data_from_front_end_for_user_postalcode
        zipcode = request.form['zipcode']
        #Getting_the_data_from_front_end_for_user_location
        city = request.form['city']
        #Getting_the_data_from_front_end_for_user_residence
        country = request.form['country']
        #Getting_the_data_from_front_end_for_user_contract
        phone = request.form['phone']
        #Establishing_connection_to_the_database
        with sqlite3.connect('database.db') as data_connect:
            try:
                data_cursor = data_connect.cursor()
                #Inserting_data_into_profile_table
                data_cursor.execute('INSERT INTO users (password, email_id, firstName, lastName, address1, zipcode, city, country, phone) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', (hashlib.md5(password.encode()).hexdigest(), email_id, First_Name, lastName, address1, zipcode, city, country, phone))
                #Commting_the_connection
                data_connect.commit()
                #status_message
                msg = "Registration_successfull"
            except:
                #Rolling_back_if_request
                data_connect.rollback()
                #status_message
                msg = "Unsuccessfull - Try Again!"
                #Closing_the_connection
        data_connect.close()
        #Redirecting_to_the_log_in_page
        return render_template("log_in.html", error=msg)

#Function_to_Register_form
@app.route("/registerationForm")
def registrationForm():
    #Rendering_to_profile_registration
    return render_template("profile_register.html")

#File_name_permission
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
