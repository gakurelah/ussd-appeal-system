from flask import Flask, request
from db import get_connection

app = Flask(__name__)

@app.route('/ussd', methods=['POST'])
def ussd():
    session_id = request.form.get('sessionId')
    service_code = request.form.get('serviceCode')
    phone_number = request.form.get('phoneNumber')
    text = request.form.get('text')  # This is what user enters step by step

    # Split input by '*' to track user input history
    inputs = text.split("*")

    if text == "":
        response = "CON Welcome to the Marks Appeal System\n"
        response += "1. Check my marks\n"
        response += "2. Appeal my marks\n"
        response += "3. Exit"
    elif text == "1":
        response = "CON Please enter your Student ID:"
    elif inputs[0] == "1" and len(inputs) == 2:
        student_id = inputs[1]
        marks = get_student_marks(student_id)
        if marks:
            response = "END Your Marks:\n"
            for module, mark in marks:
                response += f"{module}: {mark}\n"
        else:
            response = "END Error: Student ID not found."
    elif text == "2":
        response = "CON Please enter your Student ID:"
    elif inputs[0] == "2" and len(inputs) == 2:
        student_id = inputs[1]
        modules = get_student_modules(student_id)
        if modules:
            response = "CON Select module to appeal:\n"
            for i, (module, mark) in enumerate(modules):
                response += f"{i+1}. {module}: {mark}\n"
        else:
            response = "END Error: No modules found or invalid ID."
    elif inputs[0] == "2" and len(inputs) == 3:
        response = "CON Enter reason for your appeal:"
    elif inputs[0] == "2" and len(inputs) == 4:
        student_id = inputs[1]
        selected_index = int(inputs[2]) - 1
        reason = inputs[3]
        modules = get_student_modules(student_id)
        if 0 <= selected_index < len(modules):
            module_name = modules[selected_index][0]
            submit_appeal(student_id, module_name, reason)
            response = "END Thank you. Your appeal has been submitted."
        else:
            response = "END Error: Invalid module selection."
    elif text == "3":
        response = "END Thank you for using the system."
    else:
        response = "END Invalid input. Please try again."

    return response, 200, {'Content-Type': 'text/plain'}

# Helper functions
def get_student_marks(student_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT module_name, mark FROM marks WHERE student_id = %s", (student_id,))
        return cursor.fetchall()
    except Exception as e:
        print("Error:", e)
        return None
    finally:
        cursor.close()
        conn.close()

def get_student_modules(student_id):
    return get_student_marks(student_id)

def submit_appeal(student_id, module_name, reason):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO appeals (student_id, module_name, reason, status_id) VALUES (%s, %s, %s, %s)",
                       (student_id, module_name, reason, 1))  # status_id = 1 = Pending
        conn.commit()
    except Exception as e:
        print("Appeal submission error:", e)
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

