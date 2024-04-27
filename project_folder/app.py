from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

# Connect to the database
db = mysql.connector.connect(host="localhost", user="root", password="root", database="college_database")
cursor = db.cursor()

# Define the routes
@app.route('/')
def index():
    """Renders the home page."""
    return render_template('index.html')

@app.route('/create_student', methods=['POST'])
def create_student():
    """Creates a new student record in the database."""

    # Validate the user input+
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    phone_number = request.form.get('phone_number')
    major = request.form.get('major')
    graduation_year = request.form.get('graduation_year')

    if not (first_name and last_name and email and phone_number and major and graduation_year):
        return render_template('error.html', error_message="Please fill in all required fields")

    # Try to insert the new student record into the database
    try:
        with db.cursor() as cursor:
            sql = """
            INSERT INTO students (first_name, last_name, email, phone_number, major, graduation_year)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (first_name, last_name, email, phone_number, major, graduation_year))
            db.commit()
    except mysql.connector.errors.DatabaseError as e:
        # If there is an error, return a more helpful error message to the user
        return render_template('error.html', error_message="Error creating student record: {}".format(e))

    return redirect(url_for('index'))

@app.route('/insert_course', methods=['POST'])
def insert_course():
    """Creates a new course record in the database."""

    # Validate the user input
    if not request.form['course_name']:
        return render_template('error.html', error_message="Invalid course name")
    if not request.form['course_description']:
        return render_template('error.html', error_message="Invalid course description")
    if not request.form['department']:
        return render_template('error.html', error_message="Invalid department")
    if not request.form['credit_hours']:
        return render_template('error.html', error_message="Invalid credit hours")

    # Try to insert the new course record into the database
    try:
        sql = """
        INSERT INTO courses (course_name, course_description, department, credit_hours)
        VALUES (%s, %s, %s, %s)
        """
        cursor = db.cursor()  # Reopen the cursor
        cursor.execute(sql, (request.form['course_name'], request.form['course_description'], request.form['department'], request.form['credit_hours']))
        db.commit()
    except mysql.connector.errors.DatabaseError as e:
        # If there is an error, return a more helpful error message to the user
        return render_template('error.html', error_message="Error creating course record: {}".format(e))
    finally:
        cursor.close()

    return redirect(url_for('index'))


@app.route('/delete_student', methods=['POST'])
def delete_student():
    """Deletes a student record from the database."""
    
    # Validate the user input
    student_id = request.form.get('student_id')

    if not student_id:
        return render_template('error.html', error_message="Invalid student ID")

    try:
        # Check if the student ID exists in the database
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM students WHERE student_id = %s", (student_id,))
            student = cursor.fetchone()

            if not student:
                return render_template('error.html', error_message=f"Student with ID {student_id} does not exist")

        # Delete the student record
        with db.cursor() as cursor:
            cursor.execute("DELETE FROM students WHERE student_id = %s", (student_id,))
            db.commit()
    except mysql.connector.errors.DatabaseError as e:
        return render_template('error.html', error_message="Error deleting student record: {}".format(e))

    return redirect(url_for('index'))


@app.route('/update_student', methods=['POST'])
def update_student():
  """Updates a student record in the database."""

  # Validate the user input
  if not request.form['student_id']:
    return render_template('error.html', error_message="Invalid student ID")
  if not request.form['first_name']:
    return render_template('error.html', error_message="Invalid first name")
  if not request.form['last_name']:
    return render_template('error.html', error_message="Invalid last name")
  if not request.form['email']:
    return render_template('error.html', error_message="Invalid email address")
  if not request.form['phone_number']:
    return render_template('error.html', error_message="Invalid phone number")
  if not request.form['major']:
    return render_template('error.html', error_message="Invalid major")
  if not request.form['graduation_year']:
    return render_template('error.html', error_message="Invalid graduation year")

  # Try to update the student record in the database
  try:
    sql = """
    UPDATE students
    SET first_name = %s, last_name = %s, email = %s, phone_number = %s, major = %s, graduation_year = %s
    WHERE student_id = %s
    """
    cursor.execute(sql, (request.form['first_name'], request.form['last_name'], request.form['email'], request.form['phone_number'], request.form['major'], request.form['graduation_year'], request.form['student_id']))
    db.commit()
  except mysql.connector.errors.DatabaseError as e:
    # If there is an error, return a more helpful error message to the user
    return render_template('error.html', error_message="Error updating student record: {}".format(e))

  # Close the database cursor
  cursor.close()

  # Redirect the user to the home page
  return redirect(url_for('index'))

@app.route('/view_database', methods=['POST'])
def view_database():
    """Renders a page to view a table in the database."""

    # Validate the user input
    table_name = request.form.get('table_name')
    if not table_name:
        return render_template('error.html', error_message="Invalid table name")

    # Perform a query to fetch data from the specified table
    try:
        with db.cursor() as cursor:
            cursor.execute(f'SELECT * FROM `{table_name}`')

            data = cursor.fetchall()
    except mysql.connector.Error as e:
        return render_template('error.html', error_message=f"Error fetching data from {table_name}: {e}")
    
    return render_template('view_table.html', table_name=table_name, data=data)


from flask import abort

@app.route('/enroll_student', methods=['POST'])
def enroll_student():
    data = request.form

    # Validate student_id, course_id, and grade
    student_id = data.get('student_id')
    course_id = data.get('course_id')
    grade = data.get('grade')

    if not (student_id and course_id and grade):
        return render_template('error.html', error_message="Invalid input data")

    try:
        student_id = int(student_id)
        course_id = int(course_id)
        # Add further validation for grade if necessary

        # Insert enrollment record into the database
        cursor = db.cursor()
        sql = """
        INSERT INTO enrollments (student_id, course_id, grade)
        VALUES (%s, %s, %s)
        """
        cursor.execute(sql, (student_id, course_id, grade))
        db.commit()
        cursor.close()

        return redirect(url_for('index'))
    except (ValueError, mysql.connector.errors.DatabaseError) as e:
        return render_template('error.html', error_message=f"Error enrolling student: {e}")
