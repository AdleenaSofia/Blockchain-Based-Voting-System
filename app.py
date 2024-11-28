from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from markupsafe import Markup
from flask_mysqldb import MySQL
from datetime import datetime
from blockchain_connection import voting_system_contract, w3
import mysql.connector
import pandas as pd
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Note the corrected key name


mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="monstax22",
        database='bbvs1'
    )
mycursor = mydb.cursor()

@app.route('/')
def startup():
    return render_template('students/startup.html')

@app.route('/admin/login', methods=['GET','POST'])
def login():

    if request.method == 'POST':
        #get username and password from the login form
        username = request.form['username']
        password = request.form['password']

        sql_statement = "SELECT * FROM admin where username = %s AND password = %s"
        mycursor.execute(sql_statement,(username,password))
        user = mycursor.fetchone()

        if user:
            #Store user data in session if login is successful
            session['loggedin']=True
            session['id']=user[0]
            session['username'] = user[1]
            return redirect(url_for('dashboard'))
        else:
            #if login unsuccessful
            flash('Invalid username or password. Do try again.')
            return redirect(url_for('login'))
        
    return render_template('admin/login.html')


#Admin parts
@app.route('/admin/dashboard')
def dashboard():
    if 'loggedin' in session:
        mycursor.execute("SELECT COUNT(*) FROM student")
        student_count = mycursor.fetchone()[0]

        mycursor.execute("SELECT COUNT(*) FROM election")
        election_count = mycursor.fetchone()[0]

        # Retrieve the 3 latest elections
        mycursor.execute("""
            SELECT e.ElectionID, e.ElectionName, e.ElectionDate,
                   (SELECT COUNT(*) FROM Candidate WHERE Candidate.ElectionID = e.ElectionID) AS total_candidates,
                   (SELECT COUNT(*) FROM Ballot WHERE Ballot.ElectionID = e.ElectionID) AS total_voters
            FROM Election e
            ORDER BY e.ElectionDate DESC
            LIMIT 3
        """)
        latest_elections = mycursor.fetchall()

        return render_template('admin/dashboard.html',
                               student_count=student_count,
                               election_count=election_count,
                               latest_elections=latest_elections)
    else:
        return redirect(url_for('login'))

@app.route('/admin/student')
def student():
    return render_template('admin/student.html')

#list all students data using get_all_students()
@app.route('/admin/list_of_student')
def list_of_student():
    query = request.args.get('query', '').strip()
    if query:
        students = search_student(query)
    else:
        students = get_all_students()
    return render_template('admin/list_of_student.html',students=students)

def get_all_students():
    sql="SELECT Name,StudentID,Email,Course,Semester FROM Student"
    mycursor.execute(sql)
    result = mycursor.fetchall()

    students = []
    for row in result:
        students.append({
            'name': row[0],
            'StudentID': row[1],
            'email':row[2],
            'course': row[3],
            'semester': row[4]
        })
    return students

def search_student(query=""):
    # if query is provided , add a where clause to filter results
    if query:
        sql="""
        SELECT Name,StudentID,Email,Course,Semester FROM Student
        WHERE Name LIKE %s OR StudentID LIKE %s OR
        Course LIKE %s OR Semester LIKE %s
        """
        like_query=f"%{query}%" # Add wildcards for partial matching
        mycursor.execute(sql,(like_query,like_query,like_query,like_query))
    else:
        sql="SELECT Name,StudentID,Email,Course,Semester FROM Student"
        mycursor.execute(sql)

    result = mycursor.fetchall()

    students = []
    for row in result:
        students.append({
            'name': row[0],
            'StudentID': row[1],
            'email':row[2],
            'course': row[3],
            'semester': row[4]
        })
    return students

@app.route('/admin/add_student', methods=['POST', 'GET'])
def add_student():
    if request.method == 'POST':
        StudentID = request.form.get('student-id')
        Name = request.form.get('name')
        Email = request.form.get('email')
        Course = request.form.get('course')
        Semester = request.form.get('semester')

        # Debugging print to check values
        print("StudentID:", StudentID)
        print("Name:", Name)
        print("Email:", Email)
        print("Course:", Course)
        print("Semester:", Semester)

        try:
            if not StudentID:  # Check if StudentID is missing
                flash("Student ID is required.", "error")
                return redirect(url_for('add_student'))
            
            sql = "INSERT INTO Student (StudentID,Name,Email,Course,Semester) VALUES (%s,%s,%s,%s,%s)"
            val = (StudentID, Name, Email, Course, Semester)
            mycursor.execute(sql, val)
            mydb.commit()

            flash('Student added successfully!', 'success')
        except Exception as e:
            mydb.rollback()
            flash(f'Error adding student: {e}', 'error')

        return redirect(url_for('add_student'))
    
    return render_template('admin/add_student.html')
#get student data to update
@app.route('/admin/get_student/<string:student_id>')
def get_student(student_id):
    sql = "SELECT Name, StudentID, Email, Course, Semester FROM Student WHERE StudentID = %s"
    val = (student_id,)
    mycursor.execute(sql, val)
    result = mycursor.fetchone()

    if result:
        student = {
            'name': result[0],
            'student_id': result[1],
            'email': result[2],
            'course': result[3],
            'semester': result[4]
        }
        return jsonify(student)
    return jsonify({'error': 'Student not found'}), 404


@app.route('/admin/update_student/<string:student_id>', methods=['POST'])
def update_student(student_id):
    try:
        name = request.form['name']
        email = request.form['email']
        new_student_id = request.form['student_id']
        course = request.form['course']
        semester = request.form['semester']

        sql = """UPDATE Student
                 SET Name = %s, Email = %s, StudentID = %s, Course = %s, Semester = %s
                 WHERE StudentID = %s"""
        val = (name, email, new_student_id, course, semester, student_id)
        mycursor.execute(sql, val)
        mydb.commit()

        flash('Student updated successfully', 'success')
    except Exception as e:
        mydb.rollback()
        flash(f'Error updating student: {e}', 'error')

    return redirect(url_for('list_of_student'))


@app.route('/admin/delete_student/<string:student_id>', methods=['POST'])
def delete_student(student_id):
    try:
        sql="DELETE FROM Student where StudentID = %s"
        val = (student_id,)
        mycursor.execute(sql,val)
        mydb.commit()

        flash('Student deleted successfully!','success')
    except Exception as e:
        mydb.rollback()
        flash(f'Error deleting student: {e}','error')

    return redirect(url_for('list_of_student'))

#add student using file
REQUIRED_COLUMNS = {'StudentID', 'Name', 'Email', 'Course', 'Semester'}

@app.route('/admin/upload_student_file', methods=['POST'])
def upload_student_file():
    if 'fileStudent' not in request.files:
        flash('File is missing!', 'error')
        return redirect(url_for('add_student'))
    
    file = request.files['fileStudent']
    if file.filename == '':
        flash('No file selected!', 'error')
        return redirect(url_for('add_student'))

    try:
        # Read the file (adjust this if using .csv instead of .xlsx)
        df = pd.read_excel(file)
        
        # Check if all required columns are present
        if not REQUIRED_COLUMNS.issubset(df.columns):
            missing_columns = REQUIRED_COLUMNS - set(df.columns)
            flash(f'Missing required columns: {", ".join(missing_columns)}', 'error')
            return redirect(url_for('add_student'))
        
        # Process each row and insert into database
        for _, row in df.iterrows():
            sql = "INSERT INTO Student (StudentID, Name, Email, Course, Semester) VALUES (%s, %s, %s, %s, %s)"
            val = (row['StudentID'], row['Name'], row['Email'], row['Course'], row['Semester'])
            mycursor.execute(sql, val)
        
        mydb.commit()
        flash('Students added successfully!', 'success')
    except Exception as e:
        mydb.rollback()
        flash(f'Error processing file: {e}', 'error')

    return redirect(url_for('add_student'))

@app.route('/admin/vote')
def vote():
    mycursor.execute("""
        SELECT ElectionID, ElectionName, ElectionDate 
        FROM Election 
        ORDER BY ElectionDate DESC
    """)
    elections = mycursor.fetchall()
    return render_template('admin/vote.html',elections=elections)

#for Election analyics
def fetch_election_details(election_id):
    """Fetch the election details."""
    mycursor.execute("SELECT ElectionName, ElectionDate FROM Election WHERE ElectionID = %s", (election_id,))
    return mycursor.fetchone()


def fetch_candidates_for_cards(election_id):
    """Fetch candidates and their details for displaying in card boxes."""
    mycursor.execute("""
        SELECT c.CandidateID, s.Name, s.StudentID, s.Semester, s.Course, COUNT(b.VoteID) AS vote_count
        FROM Candidate c
        JOIN Student s ON c.StudentID = s.StudentID
        LEFT JOIN Ballot b ON c.CandidateID = b.CandidateID
        WHERE c.ElectionID = %s
        GROUP BY c.CandidateID
    """, (election_id,))
    candidates = mycursor.fetchall()
    return [
        {
            "CandidateID": candidate[0],
            "Name": candidate[1],
            "StudentID": candidate[2],
            "Semester": candidate[3],
            "Course": candidate[4],
            "vote_count": candidate[5],
        }
        for candidate in candidates
    ]


def fetch_candidates_for_graph(election_id):
    """Fetch candidate IDs, names, and vote counts for the graph."""
    mycursor.execute("""
        SELECT s.Name, COUNT(b.VoteID) AS vote_count
        FROM Candidate c
        JOIN Student s ON c.StudentID = s.StudentID
        LEFT JOIN Ballot b ON c.CandidateID = b.CandidateID
        WHERE c.ElectionID = %s
        GROUP BY c.CandidateID
    """, (election_id,))
    candidates_result = mycursor.fetchall()
    return {
        "labels": [result[0] for result in candidates_result],  # Candidate names
        "data": [result[1] for result in candidates_result],    # Vote counts
    }


def fetch_participation_stats(election_id):
    """Fetch the number of students who voted and who did not."""
    mycursor.execute("""
        SELECT 
            (SELECT COUNT(*) FROM Ballot WHERE ElectionID = %s) AS voted,
            (SELECT COUNT(*) FROM Student) - (SELECT COUNT(*) FROM Ballot WHERE ElectionID = %s) AS not_voted
    """, (election_id, election_id))
    participation = mycursor.fetchone()
    return {"voted": participation[0], "not_voted": participation[1]}


def fetch_participants(election_id):
    """Fetch students who participated in the election."""
    mycursor.execute("""
        SELECT DISTINCT s.StudentID, s.Name, s.Course, s.Semester
        FROM Student s
        JOIN Ballot b ON s.StudentID = b.VoterID
        WHERE b.ElectionID = %s
    """, (election_id,))
    participants = mycursor.fetchall()
    return [{"StudentID": p[0], "Name": p[1], "Course": p[2], "Semester": p[3]} for p in participants]


def fetch_non_participants(election_id):
    """Fetch students who did not participate in the election."""
    mycursor.execute("""
        SELECT s.StudentID, s.Name, s.Course, s.Semester
        FROM Student s
        WHERE NOT EXISTS (
            SELECT 1
            FROM Ballot b
            WHERE s.StudentID = b.VoterID AND b.ElectionID = %s
        )
    """, (election_id,))
    non_participants = mycursor.fetchall()
    return [{"StudentID": np[0], "Name": np[1], "Course": np[2], "Semester": np[3]} for np in non_participants]


def fetch_votes_by_course(election_id):
    """Fetch vote counts grouped by course."""
    mycursor.execute("""
        SELECT s.Course, COUNT(b.VoteID) AS vote_count
        FROM Student s
        JOIN Ballot b ON s.StudentID = b.VoterID
        WHERE b.ElectionID = %s
        GROUP BY s.Course
    """, (election_id,))
    votes_by_course = mycursor.fetchall()
    return [{"Course": v[0], "vote_count": v[1]} for v in votes_by_course]


def fetch_votes_by_semester(election_id):
    """Fetch vote counts grouped by semester."""
    mycursor.execute("""
        SELECT s.Semester, COUNT(b.VoteID) AS vote_count
        FROM Student s
        JOIN Ballot b ON s.StudentID = b.VoterID
        WHERE b.ElectionID = %s
        GROUP BY s.Semester
    """, (election_id,))
    votes_by_semester = mycursor.fetchall()
    return [{"Semester": v[0], "vote_count": v[1]} for v in votes_by_semester]

@app.route('/admin/ElectionAnalytics/<int:election_id>')
def ElectionAnalytics(election_id):
    """Main route function to render the Election Analytics page."""
    # Fetch all necessary data using helper functions
    election = fetch_election_details(election_id)
    candidates = fetch_candidates_for_cards(election_id)  # For cards
    candidates_result = fetch_candidates_for_graph(election_id)  # For graphs
    participation = fetch_participation_stats(election_id)
    participants = fetch_participants(election_id)
    non_participants = fetch_non_participants(election_id)
    votes_by_course = fetch_votes_by_course(election_id)
    votes_by_semester = fetch_votes_by_semester(election_id)

    # Pass the data to the template
    return render_template(
        'admin/electionAnalytics.html',
        election=election,
        candidates=candidates,  # For cards
        candidates_result=json.dumps(candidates_result),  # For graphs
        participation=json.dumps(participation),
        votes_by_course=json.dumps(votes_by_course),
        votes_by_semester=json.dumps(votes_by_semester),
        participants=json.dumps(participants),
        non_participants=json.dumps(non_participants),
    )

#students chart
@app.route('/admin/student_counts_by_course', methods=['GET'])
def student_counts_by_course():
    try:
        mycursor.execute("SELECT Course, COUNT(*) as total FROM Student GROUP BY Course")
        result = mycursor.fetchall()
        course_data = [{'course': row[0], 'total': row[1]} for row in result]
        return jsonify(course_data)
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)})
    
@app.route('/admin/student_counts_by_semester', methods=['GET'])
def student_counts_by_semester():
    try:
        mycursor.execute("SELECT Semester, COUNT(*) as total FROM Student GROUP BY Semester")
        result = mycursor.fetchall()
        semester_data = [{'semester': row[0], 'total': row[1]} for row in result]
        return jsonify(semester_data)
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)})

#Election Part
@app.route('/election/ElectionForm')
def ElectionForm():
    return render_template('election/ElectionForm.html')

@app.route('/election/submit_election_form',methods=['POST'])
def submit_election_form():
    election_name=request.form.get('electionName')
    election_date = request.form.get('date')
    
    try:
        sql = "INSERT INTO Election (ElectionName,ElectionDate,status) VALUES (%s,%s,%s)"
        values = (election_name,election_date,'pending')
        mycursor.execute(sql,values)
        mydb.commit()

        election_id = mycursor.lastrowid
    except Exception as e:
        mydb.rollback()
        print("Error: ", e)
        return "Internal Server Error", 500
    return redirect(url_for('ElectionStart', election_id=election_id))

@app.route('/election/ElectionStart')
def ElectionStart():
    sql = "SELECT ElectionID, ElectionName, ElectionDate FROM Election ORDER BY ElectionID DESC LIMIT 1"
    mycursor.execute(sql)
    election = mycursor.fetchone()

    if election:
        election_id = election[0]
        election_name = election[1]
        if election[2] is not None:
            election_date = election[2].strftime("%d %B %Y")
        else:
            election_date = "Date Not Available"
    else:
        election_id = None
        election_name = "Election Not Found"
        election_date = "Date Not Found"

    return render_template(
        'election/ElectionStart.html',
        election_id=election_id,
        election_name=election_name,
        election_date=election_date
    )

@app.route('/get_candidate/<string:student_id>',methods=['GET'])
def get_candidate(student_id):
    sql="SELECT Name,StudentID,Course, Semester FROM student WHERE StudentID = %s"
    mycursor.execute(sql,(student_id,))
    candidate=mycursor.fetchone()
    if candidate:
        return jsonify({"success": True,
                        "name":candidate[0],
                        "StudentID":candidate[1],
                        "course": candidate[2],
                        "semester": candidate[3]
                        })
    else:
        return jsonify({"success": False})

@app.route('/save_candidate', methods=['POST'])
def save_candidate():
    data = request.get_json()
    student_id = data['studentID']
    election_id = data['electionID']
    
    # Insert into the Candidate table
    sql = "INSERT INTO Candidate (ElectionID, StudentID) VALUES (%s, %s)"
    mycursor.execute(sql, (election_id, student_id))
    mydb.commit()
    
    return jsonify({"success": True})



@app.route('/start_election/<int:election_id>', methods=['POST'])
def start_election(election_id):
    sql_update_status = "UPDATE Election SET status = 'ongoing' WHERE ElectionID = %s"
    mycursor.execute(sql_update_status, (election_id,))
    mydb.commit()

    # Redirect to the election results page after starting the election
    return redirect(url_for('ElectionResult', election_id=election_id))


@app.route('/election/ElectionResult/<int:election_id>')
def ElectionResult(election_id):
    sql_election = "SELECT ElectionName, ElectionDate FROM Election WHERE ElectionID = %s"
    mycursor.execute(sql_election, (election_id,))
    election = mycursor.fetchone()
    if election:
        election_name = election[0]
        election_date = election[1].strftime("%d %B %Y")
    else:
        election_name = "Election Not Found"
        election_date = "Date Not Found"

    # Fetch candidates and their vote counts
    sql_candidates = """
        SELECT s.Name, s.Semester, s.Course, c.CandidateID, IFNULL(COUNT(b.VoteID), 0) as vote_count
        FROM Candidate c
        LEFT JOIN Student s ON c.StudentID = s.StudentID
        LEFT JOIN Ballot b ON c.CandidateID = b.CandidateID
        WHERE c.ElectionID = %s
        GROUP BY c.CandidateID
        ORDER BY vote_count DESC
    """
    mycursor.execute(sql_candidates, (election_id,))
    candidates = mycursor.fetchall()
    
    # Prepare data for the template
    candidate_data = [
        {
            "name": candidate[0],
            "semester": candidate[1],
            "course": candidate[2],
            "candidate_id": candidate[3],
            "vote_count": candidate[4]
        }
        for candidate in candidates
    ]

    return render_template(
        'election/ElectionResult.html',
        election_name=election_name,
        election_date=election_date,
        candidates=candidate_data,
        election_id=election_id
    )
    

@app.route('/end_election/<int:election_id>')
def end_election(election_id):
    sql = "UPDATE Election SET status = 'completed' WHERE ElectionID = %s"
    mycursor.execute(sql,(election_id,))
    mydb.commit()
    return redirect(url_for('vote'))

@app.route('/get_votes/<int:election_id>')
def get_votes(election_id):
    sql_votes = """
        SELECT c.CandidateID, IFNULL(COUNT(b.VoteID), 0) as vote_count
        FROM Candidate c
        LEFT JOIN Ballot b ON c.CandidateID = b.CandidateID
        WHERE c.ElectionID = %s
        GROUP BY c.CandidateID
        ORDER BY c.CandidateID
    """
    mycursor.execute(sql_votes, (election_id,))
    votes = [row[1] for row in mycursor.fetchall()]
    
    return jsonify({"votes": votes})

#Voter Part
@app.route('/voter/voterLogin',methods=['GET','POST'])
def voterLogin():
    if request.method == 'POST':
        StudentID = request.form['id-input']

        sql="SELECT * FROM Student where StudentID = %s "
        mycursor.execute(sql,(StudentID,))
        user = mycursor.fetchone()

        if user:
            session['loggedin']=True
            session['StudentID']=user[0]
            return redirect(url_for('voterHomepage'))
        else:
            flash('Not registered yet! Please inform you advisor', 'error')
            return redirect(url_for('voterLogin'))
        
    return render_template('students/voterLogin.html')

@app.route('/voter/homepage')
def voterHomepage():
    if 'loggedin' in session:
        StudentID = session['StudentID']
        sql = "SELECT Name, StudentID, Course, Semester FROM Student WHERE StudentID = %s"
        mycursor.execute(sql, (StudentID,))
        student_info = mycursor.fetchone()

        # Check for an ongoing election
        election_sql = "SELECT ElectionID, status FROM Election WHERE status = 'ongoing' ORDER BY ElectionID DESC LIMIT 1"
        mycursor.execute(election_sql)
        active_election = mycursor.fetchone()

        # Determine election status and ID
        if active_election:
            election_id = active_election[0]
            election_status = active_election[1]
        else:
            election_id = None
            election_status = "no_election"

        if student_info:
            return render_template(
                'students/voterHomepage.html', 
                name=student_info[0], 
                id=student_info[1], 
                course=student_info[2], 
                semester=student_info[3],
                election_status=election_status,
                election_id=election_id
            )
        else:
            flash("Student data not found.", "error")
            return redirect(url_for('voterLogin'))
    else:
        flash("Please log in first", "error")
        return redirect(url_for('voterLogin'))


@app.route('/voter/ElectionStart/<int:election_id>')
def voterElectionStart(election_id):
    sql = "SELECT ElectionName FROM Election WHERE ElectionID = %s AND status = 'ongoing'"
    mycursor.execute(sql, (election_id,))
    active_election =mycursor.fetchone()

    if active_election:
        election_name = active_election[0]
        return render_template('students/voterElectionStart.html', election_name=election_name, election_id=election_id)
    else:
        flash("No active election found.", "error")
        return redirect(url_for('voterHomepage'))

@app.route('/voter/Election/<int:election_id>')
def voterElection(election_id):
    if 'loggedin' not in session:
        flash("Please log in first", "error")
        return redirect(url_for('voterLogin'))

    # Fetch election and candidate details
    sql = "SELECT ElectionID, ElectionName FROM Election WHERE ElectionID = %s AND status = 'ongoing'"
    mycursor.execute(sql, (election_id,))
    election = mycursor.fetchone()
    print("Election fetched:", election)

    if election:
        election = dict(zip(mycursor.column_names, election))
        election_name = election['ElectionName']
        
        # Fetch candidate details by joining Candidate and Student tables
        candidate_sql = """
        SELECT c.CandidateID, s.Name, s.StudentID, s.Course, s.Semester
        FROM Candidate c
        JOIN Student s ON c.StudentID = s.StudentID
        WHERE c.ElectionID = %s
        """
        mycursor.execute(candidate_sql, (election_id,))
        candidates = mycursor.fetchall()
        print("Candidates fetched:", candidates)

        return render_template('students/voterElection.html', election_name=election_name, candidates=candidates, election_id=election_id)
    else:
        flash("No ongoing election found.", "error")
        return redirect(url_for('voterHomepage'))


@app.route('/voter/submitVote/<int:election_id>', methods=['POST'])
def submitVote(election_id):
    selected_candidate = request.form.get('selectedCandidate')
    StudentID = session['StudentID']

    if selected_candidate:
        # Insert the vote into the Ballot table
        sql = "INSERT INTO Ballot (VoterID, ElectionID, CandidateID) VALUES (%s, %s, %s)"
        mycursor.execute(sql, (StudentID, election_id, selected_candidate))
        mydb.commit()
        return redirect(url_for('voterSubmit', election_id=election_id))
    else:
        flash("Please select a candidate.", "error")
        return redirect(url_for('voterElection', election_id=election_id))


@app.route('/voter/voterSubmit/<int:election_id>')
def voterSubmit(election_id):
    # Fetch the election status
    sql = "SELECT status FROM Election WHERE ElectionID = %s"
    mycursor.execute(sql, (election_id,))
    election_status = mycursor.fetchone()

    if election_status:
        status = election_status[0]
    else:
        status = "unknown"

    return render_template('students/voterSubmit.html', election_status=status, election_id=election_id)



@app.route('/voter/result/<int:election_id>')
def voterElectionResult(election_id):
    # Query to fetch candidate names and vote counts
    sql = """
    SELECT s.Name, COUNT(b.CandidateID) as VoteCount
    FROM Ballot b
    JOIN Candidate c ON b.CandidateID = c.CandidateID
    JOIN Student s ON c.StudentID = s.StudentID
    WHERE b.ElectionID = %s
    GROUP BY s.Name
    """
    mycursor.execute(sql, (election_id,))
    results = mycursor.fetchall()
    
    # Format the data to use names as labels
    vote_data = {row[0]: row[1] for row in results}
    
    # Fetch election name for display
    election_sql = "SELECT ElectionName FROM Election WHERE ElectionID = %s"
    mycursor.execute(election_sql, (election_id,))
    election_name = mycursor.fetchone()[0]

    return render_template('students/voterResult.html', vote_data=vote_data, election_name=election_name)




@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username',None)
    flash('You have been loggedout.','success')
    return redirect(url_for('login'))

@app.route('/voter/logout')
def voterLogout():
    session.pop('loggedin',None)
    session.pop('StudentID',None)
    flash('You have been loggedout','error')
    return redirect(url_for('voterLogin'))

#blockchain casting vote function
@app.route('/voter/cast_vote<int:election_id>', methods=['POST'])
def cast_vote(election_id):
    if 'loggedin' not in session:
        flash('You must be logged in to vote.','error')
        return redirect(url_for('voterLogin'))
    
    #Get the vote details from the form
    voter_id = session['StudentID']
    candidate_id = request.form.get('selectedCandidate')

    
    #Check if a vote already exists for this voter in the given election
    sql_check = " SELECT * FROM Ballot WHERE VoterID = %s AND ElectionID = %s"
    mycursor.execute(sql_check,(voter_id,election_id))
    existing_vote = mycursor.fetchone()

    if existing_vote:
        flash('You have already voted in this election.' , 'error')
        return redirect(url_for('voterResult', election_id=election_id))
    
    #Insert the vote into database
    try:
        sql_insert = "INSERT INTO Ballot (VoterID, ElectionID, CandidateID) VALUES (%s,%s,%s)"
        mycursor.execute(sql_insert, (voter_id, election_id, candidate_id))
        mydb.commit()

        flash('Vote cast successfully!','success')
        

        #record vote in the blockchain
        try:
            txn = voting_system_contract.functions.castVote(int(candidate_id)).transact({'from': w3.eth.accounts[0]})
            w3.eth.wait_for_transaction_receipt(txn)
            flash('vote recorded on the blockchain!','success')
        except Exception as e:
            print(f"Blockchain Error: {e}")
            flash('Vote recorded locally but not on blockchain,','warning')

        return redirect(url_for('voterSubmit', election_id=election_id))
    except Exception as e:
        mydb.rollback()
        flash(f'Error casting vote: {e}','error')
        return redirect(url_for('voterElection', election_id=election_id)) 

if __name__ == '__main__':
    app.run(debug=True)
