from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
import re
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database connection parameters
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'password',
    'database': 'mysql_python'
}

def get_db_connection():
    connection = mysql.connector.connect(**db_config)
    return connection

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/customer_registration', methods=['GET', 'POST'])
def customer_registration():
    if request.method == 'POST':
        # Process registration form
        customer_name = request.form['customer_name']
        customer_age = request.form['customer_age']
        customer_gender = request.form['customer_gender']
        contact_number = request.form['contact_number']
        email_id = request.form['email_id']
        password_user = request.form['password_user']
        address = request.form['address']
        nominee_name = request.form['nominee_name']
        nominee_relationship = request.form['nominee_relationship']

        # Validate inputs (basic validation, can be extended)
        if not re.match(r'^[a-zA-Z ]{2,50}$', customer_name):
            flash('Invalid Customer Name! Please enter a valid name [3-50 characters]')
            return redirect(url_for('customer_registration'))
        if not re.match(r'^(1[8-9]|[2-9][0-9]|1[0-2][0-9]|130)$', customer_age):
            flash('Invalid Customer Age! Please enter a valid Customer Age [18-130]')
            return redirect(url_for('customer_registration'))
        if not re.match(r'^(male|female|Others)$', customer_gender, re.IGNORECASE):
            flash('Invalid Gender! Please enter a valid Gender(male|female|Others)')
            return redirect(url_for('customer_registration'))
        if not re.match(r'^\d{10}$', contact_number):
            flash('Invalid Contact Number! Please enter a valid 10 digit number')
            return redirect(url_for('customer_registration'))
        if not re.match(r'^[a-z\d]+@[a-z]{2,30}\.com$', email_id):
            flash('Invalid Email Id! Please enter a valid Email Id(.com)')
            return redirect(url_for('customer_registration'))
        if not re.match(r'^[a-zA-Z\W\d]{8,30}$', password_user):
            flash('Invalid Password! Please enter a valid Password[5-30 characters][include at least one special character and number]')
            return redirect(url_for('customer_registration'))
        if not re.match(r'^[a-zA-Z\d\W]{5,150}$', address):
            flash('Invalid Address! Please enter a valid Address[5-150 characters]')
            return redirect(url_for('customer_registration'))
        if not re.match(r'^[a-zA-Z ]{2,50}$', nominee_name):
            flash('Invalid Nominee Name! Please enter a valid Nominee Name[2-50 characters]')
            return redirect(url_for('customer_registration'))
        if not re.match(r'^[a-zA-Z ]{2,80}$', nominee_relationship):
            flash('Invalid Nominee Relationship! Please enter a valid Nominee Relationship[2-80 characters]')
            return redirect(url_for('customer_registration'))

        # Check if customer exists
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM customer_info WHERE Contact_Number = %s OR Email_Id = %s", (contact_number, email_id))
        existing = cursor.fetchone()
        if existing:
            flash('Customer with same Phone number or Email Id already exists.')
            cursor.close()
            connection.close()
            return redirect(url_for('customer_registration'))

        # Generate unique customer id
        customer_id = ''.join(random.sample('0123456789', 7))

        # Insert customer into database
        sql = ("INSERT INTO customer_info (Customer_id, Customer_Name, Customer_Age, Customer_Gender, Contact_Number, "
               "Email_Id, Password, Address, Nominee_Name, Nominee_relationship) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
        val = (customer_id, customer_name, customer_age, customer_gender.capitalize(), contact_number, email_id, password_user,
               address, nominee_name, nominee_relationship)
        cursor.execute(sql, val)
        connection.commit()
        cursor.close()
        connection.close()
        flash(f'Registration successful! Your Customer ID is {customer_id}')
        return redirect(url_for('home'))

    return render_template('customer_registration.html')

@app.route('/customer_login', methods=['GET', 'POST'])
def customer_login():
    if request.method == 'POST':
        customer_id = request.form['customer_id']
        password = request.form['password']

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT Password FROM customer_info WHERE Customer_id = %s", (customer_id,))
        result = cursor.fetchone()
        cursor.close()
        connection.close()

        if result and result[0] == password:
            session['customer_id'] = customer_id
            return redirect(url_for('customer_dashboard'))
        else:
            flash('Invalid Customer ID or Password')
            return redirect(url_for('customer_login'))

    return render_template('customer_login.html')

@app.route('/customer_dashboard')
def customer_dashboard():
    if 'customer_id' not in session:
        flash('Please login first')
        return redirect(url_for('customer_login'))

    customer_id = session['customer_id']
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM customer_info WHERE Customer_id = %s", (customer_id,))
    customer = cursor.fetchone()

    cursor.execute("SELECT * FROM policy_info WHERE Customer_id = %s", (customer_id,))
    policies = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template('customer_dashboard.html', customer=customer, policies=policies)

@app.route('/select_policy', methods=['GET', 'POST'])
def select_policy():
    if 'customer_id' not in session:
        flash('Please login first')
        return redirect(url_for('customer_login'))

    customer_id = session['customer_id']

    health_insurances = [
        {"policy_name": "HDFC Ergo Health Insurance", "sum_assured": 5000000, "premium": 9000, "term": 1},
        {"policy_name": "Max Bupa Health Insurance", "sum_assured": 10000000, "premium": 12000, "term": 1},
        {"policy_name": "Star Health Insurance", "sum_assured": 8000000, "premium": 10500, "term": 1}
    ]
    motor_insurances = [
        {"policy_name": "Third-Party Liability Insurance", "sum_assured": 10000, "premium": 500, "term": 1},
        {"policy_name": "Comprehensive Insurance", "sum_assured": 20000, "premium": 1000, "term": 2},
        {"policy_name": "Motorcycle Insurance", "sum_assured": 5000, "premium": 250, "term": 1}
    ]
    general_insurances = [
        {"policy_name": "Bajaj Allianz General Insurance", "sum_assured": 500000, "premium": 7000, "term": 1},
        {"policy_name": "TATA AIG General Insurance", "sum_assured": 800000, "premium": 8000, "term": 1},
        {"policy_name": "ICICI Lombard General Insurance", "sum_assured": 700000, "premium": 7500, "term": 1}
    ]

    if request.method == 'POST':
        category = request.form.get('category')
        selected_policy_index = int(request.form.get('policy_index', -1))

        if category and selected_policy_index >= 0:
            if category == 'health':
                selected_policy = health_insurances[selected_policy_index]
            elif category == 'motor':
                selected_policy = motor_insurances[selected_policy_index]
            elif category == 'general':
                selected_policy = general_insurances[selected_policy_index]
            else:
                flash('Invalid category selected')
                return redirect(url_for('select_policy'))

            # Insert policy info into database
            connection = get_db_connection()
            cursor = connection.cursor()
            policy_id = ''.join(random.sample('0123456789', 7))
            sql = ("INSERT INTO policy_info (Customer_id, Policy_id, Policy_Name, Sum_Assured, Premium, Term) "
                   "VALUES (%s, %s, %s, %s, %s, %s)")
            val = (customer_id, policy_id, selected_policy['policy_name'], selected_policy['sum_assured'],
                   selected_policy['premium'], selected_policy['term'])
            cursor.execute(sql, val)
            connection.commit()
            cursor.close()
            connection.close()
            flash(f"Policy '{selected_policy['policy_name']}' selected successfully! Policy ID: {policy_id}")
            return redirect(url_for('customer_dashboard'))
        else:
            flash('Please select a policy to continue')
            return redirect(url_for('select_policy'))

    return render_template('select_policy.html', health_insurances=health_insurances,
                           motor_insurances=motor_insurances, general_insurances=general_insurances)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('home'))

@app.route('/agent_login', methods=['GET', 'POST'])
def agent_login():
    if request.method == 'POST':
        password = request.form['password']
        if password == 'Insurance@1515':
            session['agent_logged_in'] = True
            return redirect(url_for('agent_dashboard'))
        else:
            flash('Incorrect Password')
            return redirect(url_for('agent_login'))
    return render_template('agent_login.html')

@app.route('/agent_dashboard')
def agent_dashboard():
    if not session.get('agent_logged_in'):
        flash('Please login as agent first')
        return redirect(url_for('agent_login'))

    connection = get_db_connection()
    cursor = connection.cursor()
    sql = """SELECT c.Customer_id, c.Customer_Name, c.Contact_Number, c.Email_Id, c.Address, p.Policy_id, p.Policy_Name, p.Sum_Assured, p.Premium, p.Term
             FROM customer_info c
             LEFT JOIN policy_info p ON c.Customer_id = p.Customer_id"""
    cursor.execute(sql)
    results = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template('agent_dashboard.html', data=results)

if __name__ == '__main__':
    app.run(debug=True)
