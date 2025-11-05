from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "dev-secret-change-me"

# ---------- Database connection ----------
# Update the values below to match your local MySQL setup.
db_config = {
    'host': 'localhost',
    'user': 'root',        # change to your mysql user
    'password': 'dp5060',        # change to your mysql password
    'database': 'sqli_demo'
}

def get_db_conn():
    return mysql.connector.connect(**db_config)

# ---------- Routes ----------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_conn()
        cursor = conn.cursor(dictionary=True)
        # Parameterized query (safe)
        query = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'"
        cursor.execute(query)
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            session['username'] = user['username']
            flash('Logged in successfully', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Please provide username and password', 'danger')
            return redirect(url_for('register'))

        try:
            conn = get_db_conn()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            conn.commit()
            cursor.close()
            conn.close()
            flash('Registration successful — you can now log in', 'success')
            return redirect(url_for('login'))
        except mysql.connector.IntegrityError:
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))
        except Exception as e:
            flash('Database error: ' + str(e), 'danger')
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Logged out', 'info')
    return redirect(url_for('home'))

if __name__ == '__main__':
    # print routes for debugging
    print("Starting app. Registered endpoints:")
    for rule in sorted(app.url_map.iter_rules(), key=lambda r: r.rule):
        print(f"{rule.endpoint:20s} -> {rule.rule}  methods={','.join(sorted(rule.methods))}")
    app.run(debug=True)
