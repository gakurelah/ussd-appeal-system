from flask import Flask, render_template, request, redirect, url_for, session
from db import get_connection

app = Flask(__name__)
app.secret_key = 'secret-key-change-this'

# Dummy admin user (for simplicity)
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == ADMIN_USERNAME and request.form['password'] == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect('/dashboard')
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'admin' not in session:
        return redirect('/login')
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT a.id, s.name AS student_name, a.module_name, a.reason, ast.status_name
        FROM appeals a
        JOIN students s ON a.student_id = s.student_id
        JOIN appeal_status ast ON a.status_id = ast.id
        ORDER BY a.created_at DESC
    """)
    appeals = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('dashboard.html', appeals=appeals)

@app.route('/update/<int:appeal_id>', methods=['GET', 'POST'])
def update(appeal_id):
    if 'admin' not in session:
        return redirect('/login')

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        new_status = int(request.form['status_id'])
        cursor.execute("UPDATE appeals SET status_id = %s WHERE id = %s", (new_status, appeal_id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect('/dashboard')

    cursor.execute("SELECT id, status_name FROM appeal_status")
    statuses = cursor.fetchall()

    cursor.execute("SELECT * FROM appeals WHERE id = %s", (appeal_id,))
    appeal = cursor.fetchone()

    cursor.close()
    conn.close()
    return render_template('update.html', statuses=statuses, appeal=appeal)

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(port=5001, debug=True)
