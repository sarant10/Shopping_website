#importing flask
#from crypt import methods
from locale import currency
from statistics import mode
from flask import *
from flask import Flask,redirect,request
#Importing_sql_database
import sqlite3
#Importing_libr
import hashlib
#importing_os
import os

import stripe


app = Flask(__name__)
#providing_pathfor_folderupload
UPLOAD_FOLDER = 'static/uploads'
#Add database
#Providing_randomstringfor_secretkey
app.secret_key = 'random string'
#Initialise The Database
#imageformat_extensions
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'gif','jpeg'])
#Appconfigurationfor_folderupload
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

stripe.api_key = "sk_test_51Kx7rxGE3jTiQV8u5oCrQ6C8g9b22Q9EGX4dhD7fb2TiSqGx32hnCSAiPXAunx6TXh1wguznKH5RWvO1jsoGI0ME00Er1efnGV"

YOUR_DOMAIN = "http://localhost:5000"

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    mail = session['mail']
    #establishing_connection_to_the_Db
    with sqlite3.connect('customerdb.db') as data_connect:
        connect_data = data_connect.cursor()
        #Selecting_data_from_customer_table_passing_session_value
        connect_data.execute("SELECT profile_Id FROM profile WHERE mail = ?", (mail, ))
        #Feching_first_row
        profile_Id = connect_data.fetchone()[0]
        #Selecting_values_from_products_table
        connect_data.execute("SELECT catalog_prod.prod_number, catalog_prod.item_name, catalog_prod.item_cost, catalog_prod.image FROM catalog_prod, product_basket WHERE catalog_prod.prod_number = product_basket.prod_number AND product_basket.profile_Id = ?", (profile_Id, ))
        catalog_prod = connect_data.fetchall()
        #Declaring_total_price_to_zero
    totalPrice = 0
    for row in catalog_prod:
        #pushing_the_value_to_row_two
        totalPrice += row[2]
        #redirecting_to_the_item_cart_page
    totalPrice = totalPrice * 100
    Price = int(totalPrice)
    checkout_session = stripe.checkout.Session.create(
        success_url=YOUR_DOMAIN + '/success',
        cancel_url=YOUR_DOMAIN + '/cancel',
        submit_type='pay',
        payment_method_types=["card"],
        #mode="payment",
        
        line_items = [{
            'amount': Price,
            'name': 'Purchase Items',
            'currency': 'gbp',
            'quantity': 1,
        }]
    )
    return redirect(checkout_session.url, code=303)    
#Func_to_fetch_num_of_items_if_the_useris_already_loggedin
def detailed_login():
    #establising_connection_to_the_database
    with sqlite3.connect('customerdb.db') as data_connect:
        #Connection_to_the_data_base
        connect_data = data_connect.cursor()
        #If_emailid_not_in_session_the_value_returns_false_blank_zero
        if 'mail' not in session:
            #Log_in_will_be_false
            login_check = False
            #First_name_returns_blank
            First_Name = ''
            #Item_quantiy_will_be_zero
            Item_quantity = 0
        else:
            login_check = True
            #Selecting_the_user_saved_under_session
            connect_data.execute("SELECT profile_Id, firstName FROM profile WHERE mail = ?", (session['mail'], ))
            profile_Id, First_Name = connect_data.fetchone()
            #Fetching_the_count_of_Product_id_from_Kart
            connect_data.execute("SELECT count(prod_number) FROM product_basket WHERE profile_Id = ?", (profile_Id, ))
            #Fetch_the_First_row_in_the_output
            Item_quantity = connect_data.fetchone()[0]
            #Closing_the_connection
    data_connect.close()
    #Values_returned_for_above_function
    return (login_check, First_Name, Item_quantity)

@app.route("/")
def main_page():
    #Getting_the_values_from_detailed_login_and_assigning_it_to_these_below_mentioned_values
    login_check, First_Name, Item_quantity = detailed_login()
    with sqlite3.connect('customerdb.db') as data_connect:
        connect_data = data_connect.cursor()
        #Getting_prod_detail_from_the_table
        connect_data.execute('SELECT prod_number, item_name, item_cost, item_spec, image, inventory FROM catalog_prod')
        itemData = connect_data.fetchall()
        #Pulling_Cart_id_Item_name
        connect_data.execute('SELECT Cat_Id, item_name FROM catalog_div')
        categoryData = connect_data.fetchall()
    itemData = parse(itemData)   
    if 'mail' not in session:
        return render_template('index.html')
    else:
        return render_template('item_home.html', itemData=itemData, login_check=login_check, First_Name=First_Name, Item_quantity=Item_quantity, categoryData=categoryData)

#Function_to_Checkout_success
@app.route("/success")
def Checkout_success():
    return render_template('success.html')

#Function_to_login_navigation_page
@app.route("/cancel")
def Checkout_cancel():
    return render_template('cancel.html')


from werkzeug.utils import secure_filename

#Removing_the_prod_from_cart
@app.route("/remove")
def remove():
    with sqlite3.connect('customerdb.db') as data_connect:
        connect_data = data_connect.cursor()
        #Selecting_the_Product_details
        connect_data.execute('SELECT prod_number, item_name, item_cost, item_spec, image, inventory FROM catalog_prod')
        output_data = connect_data.fetchall()
    data_connect.close()
    #Rendering_to_product_remove_page
    return render_template('product_remove.html', output_data=output_data)

#Function_to_remove_item
@app.route("/removeItem")
def removeItem():
    #Getting_the_product_ID
    prod_number = request.args.get('prod_number')
    #Connection_to_database
    with sqlite3.connect('customerdb.db') as data_connect:
        try:
            connect_data = data_connect.cursor()
            #Deleting_the_fetched_prod_id
            connect_data.execute('DELETE FROM catalog_prod WHERE prod_number = ?', (prod_number, ))
            data_connect.commit()
            status_m = "Successfully Deleted"
        except:
            #If_unsuccessfull_rolling_Back_to_the_previous_state
            data_connect.rollback()
            status_m = "Error"
    data_connect.close()
    #Printing_success_or_error_message
    print(status_m)
    #Redirect_to_the_main_page
    return redirect(url_for('main_page'))

#Function_for_display_category
@app.route("/displayCategory")
def displayCategory():
        #Getting_the_information_from_detailed_login_page
        login_check, First_Name, Item_quantity = detailed_login()
        #Requesting_the_id
        cat_id = request.args.get("Cat_Id")
        with sqlite3.connect('customerdb.db') as data_connect:
            connect_data = data_connect.cursor()
            #Selecting_the_prod_details_from_produ_ct_table
            connect_data.execute("SELECT catalog_prod.prod_number, catalog_prod.item_name, catalog_prod.item_cost, catalog_prod.image, catalog_div.item_name FROM catalog_prod, catalog_div WHERE catalog_prod.Cat_Id = catalog_div.Cat_Id AND catalog_div.Cat_Id = ?", (cat_id, ))
            output_data = connect_data.fetchall()
        data_connect.close()
        catname_id = output_data[0][4]
        #Parsing_the_data
        output_data = parse(output_data)
        #returning_the_values_taken_from_prod_table
        return render_template('item_display.html', output_data=output_data, login_check=login_check, First_Name=First_Name, Item_quantity=Item_quantity, catname_id=catname_id)

#Function_to_write_profile_home
@app.route("/account/profile")
def profileHome():
    #Checking_if_the_user_is_not_Logged_in
    if 'mail' not in session:
        #If_not_logged_in_redirecting_to_the_main_page
        return redirect(url_for('main_page'))
    login_check, First_Name, Item_quantity = detailed_login()
    return render_template("Home_profile.html", login_check=login_check, First_Name=First_Name, Item_quantity=Item_quantity)

#Function_to_edit_profile
@app.route("/account/profile/edit")
def Profile_edit():
    #If_user_not_logged_in
    if 'mail' not in session:
        return redirect(url_for('main_page'))
    login_check, First_Name, Item_quantity = detailed_login()
    with sqlite3.connect('customerdb.db') as data_connect:
        connect_data = data_connect.cursor()
        #Fetching_data_from_users_table
        connect_data.execute("SELECT profile_Id, mail, firstName, lastName, address1, zipcode, city, country, phone FROM profile WHERE mail = ?", (session['mail'], ))
        profileData = connect_data.fetchone()
    data_connect.close()
    #Rendering_to_profile_edit_page
    return render_template("Profile edit.html", profileData=profileData, login_check=login_check, First_Name=First_Name, Item_quantity=Item_quantity)

#Function_to_change_pass_word
@app.route("/account/profile/changePassword", methods=["GET", "POST"])
def changePassword():
    #Checking_if_the_user_is_still_Logged_in
    if 'mail' not in session:
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
        with sqlite3.connect('customerdb.db') as data_connect:
            connect_data = data_connect.cursor()
            #Pulling_userdata_of_logged_in_user
            connect_data.execute("SELECT profile_Id, password FROM profile WHERE mail = ?", (session['mail'], ))
            profile_Id, password = connect_data.fetchone()
            #If_it_is_a_change_the_value_gets_updated
            if (password == oldPassword):
                try:
                    #queryfor_appending_the_Pass_wrd
                    connect_data.execute("UPDATE profile SET password = ? WHERE profile_Id = ?", (newPassword, profile_Id))
                    data_connect.commit()
                    #commit_confimation_string
                    status_m="Success"
                except:
                    data_connect.rollback()
                    #Commit_failure_string
                    status_m = "Request Failed"
                    #Redirecting_to_pass_wrd_change_html
                return render_template("Password_change.html", status_m=status_m)
            else:
                status_m = "password entered wrong"
        data_connect.close()
        #Redirecting_to_pass_wrd_change_html
        return render_template("Password_change.html", status_m=status_m)
    else:
        #Redirecting_to_pass_wrd_change_html
        return render_template("Password_change.html")

#Function_to_update_user_account
@app.route("/updateProfile", methods=["GET", "POST"])
def updateProfile():
    #If_the_request_is_post
    if request.method == 'POST':
        #Fectchng_the_email
        mail = request.form['mail']
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
        with sqlite3.connect('customerdb.db') as data_connect:
                try:
                    connect_data = data_connect.cursor()
                    #Query_to_update_the_profile_tabel
                    connect_data.execute('UPDATE profile SET firstName = ?, lastName = ?, address1 = ?, zipcode = ?, city = ?, country = ?, phone = ? WHERE mail = ?', (First_Name, lastName, address1, zipcode, city, country, phone, mail))
                    data_connect.commit()
                    #Printing_Message
                    status_m = "Successful"
                except:
                    #Rolling_back_the_function
                    data_connect.rollback()
                    status_m = "Error - Try Again!"
        data_connect.close()
        #Redirecting_to_profile_edit
        return redirect(url_for('Profile_edit'))

#Function_to_login_navigation_page
@app.route("/loginForm")
def loginForm():
    #if_the_user_still_logged_in
    if 'mail' in session:
        #nagivate_to_the_main_page
        return redirect(url_for('main_page'))
    else:
        #Navigate_to_the_log_in_page
        return render_template('log_in.html', error='')

#Function_to_check_the_user_credentials
@app.route("/login", methods = ['POST', 'GET'])
def login():
    #If_the_Request_method_is_post
    if request.method == 'POST':
        #Getting_the_mail_and_pass_wrd_from_front_end
        mail = request.form['mail']
        #Getting_the_pass_wrd
        password = request.form['password']
        #If_the_validation_is_correct
        if is_valid(mail, password):
            #Assigning_the_mail_to_the_session
            session['mail'] = mail
            #Navigating_to_the_main_page
            return redirect(url_for('main_page'))
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
    prod_number = request.args.get('prod_number')
    with sqlite3.connect('customerdb.db') as data_connect:
        connect_data = data_connect.cursor()
        #Selecting_prod_from_stock_table
        connect_data.execute('SELECT prod_number, item_name, item_cost, item_spec, image, inventory FROM catalog_prod WHERE prod_number = ?', (prod_number, ))
        productData = connect_data.fetchone()
    data_connect.close()
    #Redirecting_to_the_prd_des_page.
    return render_template("prd_Des.html", output_data=productData, login_check = login_check, First_Name = First_Name, Item_quantity = Item_quantity)

#Adding_cart_items
@app.route("/addToCart")
#function_to_add_cart
def addToCart():
    #If_user_not_logged_in
    if 'mail' not in session:
        #Redirect_the_page_to_loginform
        return redirect(url_for('loginForm'))
    else:
        #fetching_the_product_data
        prod_number = int(request.args.get('prod_number'))
        #Establising_connection_to_the_database.
        with sqlite3.connect('customerdb.db') as data_connect:
            connect_data = data_connect.cursor()
            #Selecting_user_data_with_the_help_of_session_id
            connect_data.execute("SELECT profile_Id FROM profile WHERE mail = ?", (session['mail'], ))
            #Getting_the_first_row
            profile_Id = connect_data.fetchone()[0]
            try:
                #inserting_values_to_the_cart
                connect_data.execute("INSERT INTO product_basket (profile_Id, prod_number) VALUES (?, ?)", (profile_Id, prod_number))
                data_connect.commit()
                #Satatus_message
                status_m = "Successfull"
            except:
                #function_to_rol_l
                data_connect.rollback()
                #Status_message
                status_m = "Error"
        #closing_the_connection
        data_connect.close()
        #Redirecting_to_the_main_page
        return redirect(url_for('main_page'))

#Function_For_Cart
@app.route("/cart")
def cart():
    #if_the_user_not_logged_in
    if 'mail' not in session:
        #redurect_to_lgoin_page
        return redirect(url_for('loginForm'))
        #Getting_data_from_detailed_login
    login_check, First_Name, Item_quantity = detailed_login()
    #assigning_the_mail_to_session
    mail = session['mail']
    #establishing_connection_to_the_Db
    with sqlite3.connect('customerdb.db') as data_connect:
        connect_data = data_connect.cursor()
        #Selecting_data_from_customer_table_passing_session_value
        connect_data.execute("SELECT profile_Id FROM profile WHERE mail = ?", (mail, ))
        #Feching_first_row
        profile_Id = connect_data.fetchone()[0]
        #Selecting_values_from_products_table
        connect_data.execute("SELECT catalog_prod.prod_number, catalog_prod.item_name, catalog_prod.item_cost, catalog_prod.image FROM catalog_prod, product_basket WHERE catalog_prod.prod_number = product_basket.prod_number AND product_basket.profile_Id = ?", (profile_Id, ))
        catalog_prod = connect_data.fetchall()
        #Declaring_total_price_to_zero
    totalPrice = 0
    for row in catalog_prod:
        #pushing_the_value_to_row_two
        totalPrice += row[2]
        #redirecting_to_the_item_cart_page
    return render_template("item_cart.html", catalog_prod = catalog_prod, totalPrice=totalPrice, login_check=login_check, First_Name=First_Name, Item_quantity=Item_quantity)



#Removing_the_product_function
@app.route("/removeFromCart")
def removeFromCart():
    #if_the_user_not_logged_in
    if 'mail' not in session:
        #Redirect_to_log_in_page
        return redirect(url_for('loginForm'))
    #assigning_sesson_to_variable
    mail = session['mail']
    #Getting_product_number
    prod_number = int(request.args.get('prod_number'))
    #establishing_connection
    with sqlite3.connect('customerdb.db') as data_connect:
        connect_data = data_connect.cursor()
        #Selecting_values_from_profile_table
        connect_data.execute("SELECT profile_Id FROM profile WHERE mail = ?", (mail, ))
        #Fetching_the_first_row
        profile_Id = connect_data.fetchone()[0]
        try:
            #Script_to_remove_the_prod_form_basket
            connect_data.execute("DELETE FROM product_basket WHERE profile_Id = ? AND prod_number = ?", (profile_Id, prod_number))
            data_connect.commit()
            #Satatus_message
            status_m = "Removed"
        except:
            #Function_to_roll_back
            data_connect.rollback()
            #Status_message
            status_m = "Error - Try Again!"
    data_connect.close()
    #Redirecting_to_rot_page
    return redirect(url_for('main_page'))

#Function_to_log_out
@app.route("/logout")
def logout():
    #If_sesson_is_null
    session.pop('mail', None)
    #Redirect_to_rot_page
    return redirect(url_for('main_page'))

#Function_to_validation_user_name_and_password
def is_valid(mail, password):
    #Connection_to_the_Databse
    data_connect = sqlite3.connect('customerdb.db')
    connect_data = data_connect.cursor()
    #Getting_the_user_credentials_to_the_table
    connect_data.execute('SELECT mail, password FROM profile')
    #Getting_all_the_record
    output_data = connect_data.fetchall()
    #Checking_all_the_credentials_in_talbe
    for row in output_data:
        #If_the_credentials_are_correct_then_the_loop_returns_true
        if row[0] == mail and row[1] == hashlib.md5(password.encode()).hexdigest():
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
        mail = request.form['mail']
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
        with sqlite3.connect('customerdb.db') as data_connect:
            try:
                connect_data = data_connect.cursor()
                #Inserting_data_into_profile_table
                connect_data.execute('INSERT INTO profile (password, mail, firstName, lastName, address1, zipcode, city, country, phone) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', (hashlib.md5(password.encode()).hexdigest(), mail, First_Name, lastName, address1, zipcode, city, country, phone))
                #Commting_the_connection
                data_connect.commit()
                #status_message
                status_m = "Registration_successfull"
            except:
                #Rolling_back_if_request
                data_connect.rollback()
                #status_message
                status_m = "Unsuccessfull - Try Again!"
                #Closing_the_connection
        data_connect.close()
        #Redirecting_to_the_log_in_page
        return render_template("log_in.html", error=status_m)

#Function_to_Register_form
@app.route("/registerationForm")
def registrationForm():
    #Rendering_to_profile_registration
    return render_template("profile_register.html")

#File_name_permission
def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def parse(output_data):
    result = []
    x = 0
    while x < len(output_data):
        z = []
        for y in range(7):
            if x >= len(output_data):
                break
            z.append(output_data[x])
            x += 1
        result.append(z)
    return result

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
