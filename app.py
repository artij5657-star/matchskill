import os
import re
from functools import wraps

from dotenv import load_dotenv
import pymysql

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    jsonify,
    send_from_directory
)

from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from PyPDF2 import PdfReader
from docx import Document


# =========================================================
# 1. LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()


# =========================================================
# FLASK CONFIGURATION
# =========================================================

app = Flask(__name__)

app.secret_key = os.getenv(
    "SECRET_KEY",
    "skillmatch-development-secret-change-this"
)


# =========================================================
# UPLOAD CONFIGURATION
# =========================================================

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf", "docx", "doc"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# =========================================================
# MYSQL CONFIGURATION
# =========================================================

def get_db_connection():
    """Create and return a MySQL database connection."""

    try:
        host = os.getenv("MYSQLHOST") or os.getenv(
            "DB_HOST",
            "localhost"
        )

        port = int(
            os.getenv("MYSQLPORT")
            or os.getenv("DB_PORT", 3306)
        )

        user = os.getenv("MYSQLUSER") or os.getenv(
            "DB_USER",
            "root"
        )

        password = os.getenv("MYSQLPASSWORD") or os.getenv(
            "DB_PASSWORD",
            ""
        )

        database = os.getenv("MYSQLDATABASE") or os.getenv(
            "DB_NAME",
            "skillmatch"
        )

        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
        )

        return connection

    except Exception as e:
        print("Database connection error:", e)
        return None


# =========================================================
# LOGIN REQUIRED DECORATOR
# =========================================================

def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):

        if "user_id" not in session:

            flash(
                "Please login first.",
                "warning"
            )

            return redirect(
                url_for("login")
            )

        return f(*args, **kwargs)

    return decorated_function


# =========================================================
# ADMIN REQUIRED DECORATOR
# =========================================================

def admin_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):

        if "user_id" not in session:

            flash(
                "Please login first.",
                "warning"
            )

            return redirect(
                url_for("login")
            )

        if session.get("role") != "admin":

            flash(
                "Admin access required.",
                "danger"
            )

            return redirect(
                url_for("dashboard")
            )

        return f(*args, **kwargs)

    return decorated_function


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def allowed_file(filename):

    return (
        "." in filename
        and
        filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


# =========================================================
# RESUME TEXT EXTRACTION
# =========================================================

def extract_text_from_resume(filepath):

    extension = filepath.rsplit(".", 1)[1].lower()

    text = ""

    try:

        if extension == "pdf":

            reader = PdfReader(filepath)

            for page in reader.pages:

                page_text = page.extract_text()

                if page_text:
                    text += page_text + "\n"

        elif extension == "docx":

            document = Document(filepath)

            for paragraph in document.paragraphs:
                text += paragraph.text + "\n"

        elif extension == "doc":

            text = ""

    except Exception as e:

        print(
            "Resume extraction error:",
            e
        )

    return text


# =========================================================
# GET USER
# =========================================================

def get_user_by_id(user_id):

    connection = get_db_connection()

    if not connection:
        return None

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                "SELECT * FROM users WHERE id = %s",
                (user_id,)
            )

            user = cursor.fetchone()

        return user

    except Exception as e:

        print(
            "Get user error:",
            e
        )

        return None

    finally:

        connection.close()


# =========================================================
# GET ALL SKILLS
# =========================================================

def get_all_skills():

    connection = get_db_connection()

    if not connection:
        return []

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                "SELECT id, name FROM skills ORDER BY name"
            )

            skills = list(cursor.fetchall())

        return skills

    except Exception as e:

        print(
            "Get skills error:",
            e
        )

        return []

    finally:

        connection.close()


# =========================================================
# GET ALL INTERESTS
# =========================================================

def get_all_interests():

    connection = get_db_connection()

    if not connection:
        return []

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                "SELECT id, name FROM interests ORDER BY name"
            )

            interests = list(cursor.fetchall())

        return interests

    except Exception as e:

        print(
            "Get interests error:",
            e
        )

        return []

    finally:

        connection.close()


# =========================================================
# EXTRACT SKILLS FROM RESUME
# =========================================================

def extract_skills_from_text(text):

    text_lower = text.lower()

    skills = get_all_skills()

    detected_skills = []

    for skill in skills:

        skill_name = skill["name"].lower()

        pattern = (
            r"\b"
            +
            re.escape(skill_name)
            +
            r"\b"
        )

        if re.search(
            pattern,
            text_lower
        ):

            detected_skills.append(
                skill["name"]
            )

    return detected_skills


# =========================================================
# RESUME SCORE
# =========================================================

def calculate_resume_score(skills):

    base_score = 50

    score = (
        base_score
        +
        (len(skills) * 8)
    )

    return min(
        score,
        100
    )


# =========================================================
# GET USER SKILLS
# =========================================================

def get_user_skills(user_id):

    connection = get_db_connection()

    if not connection:
        return []

    query = """
        SELECT s.id, s.name
        FROM skills s
        INNER JOIN user_skills us
            ON s.id = us.skill_id
        WHERE us.user_id = %s
        ORDER BY s.name
    """

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                query,
                (user_id,)
            )

            skills = list(cursor.fetchall())

        return skills

    except Exception as e:

        print(
            "Get user skills error:",
            e
        )

        return []

    finally:

        connection.close()


# =========================================================
# GET USER INTERESTS
# =========================================================

def get_user_interests(user_id):

    connection = get_db_connection()

    if not connection:
        return []

    query = """
        SELECT i.id, i.name
        FROM interests i
        INNER JOIN user_interests ui
            ON i.id = ui.interest_id
        WHERE ui.user_id = %s
        ORDER BY i.name
    """

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                query,
                (user_id,)
            )

            interests = list(cursor.fetchall())

        return interests

    except Exception as e:

        print(
            "Get user interests error:",
            e
        )

        return []

    finally:

        connection.close()


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def index():

    if "user_id" in session:

        return redirect(
            url_for("dashboard")
        )

    return render_template(
        "index.html"
    )


# =========================================================
# REGISTER
# =========================================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        if not name or not email or not password:

            flash(
                "Please fill all required fields.",
                "danger"
            )

            return redirect(
                url_for("register")
            )

        if len(password) < 6:

            flash(
                "Password must contain at least 6 characters.",
                "danger"
            )

            return redirect(
                url_for("register")
            )

        connection = get_db_connection()

        if not connection:

            flash(
                "Database connection failed.",
                "danger"
            )

            return redirect(
                url_for("register")
            )

        try:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT id
                    FROM users
                    WHERE email = %s
                    """,
                    (email,)
                )

                existing_user = cursor.fetchone()

                if existing_user:

                    flash(
                        "Email already registered.",
                        "warning"
                    )

                    return redirect(
                        url_for("login")
                    )

                password_hash = generate_password_hash(
                    password
                )

                cursor.execute(
                    """
                    INSERT INTO users
                    (
                        name,
                        email,
                        password_hash,
                        role
                    )
                    VALUES
                    (
                        %s,
                        %s,
                        %s,
                        'student'
                    )
                    """,
                    (
                        name,
                        email,
                        password_hash
                    )
                )

            flash(
                "Registration successful! Please login.",
                "success"
            )

            return redirect(
                url_for("login")
            )

        except Exception as e:

            print(
                "Registration error:",
                e
            )

            flash(
                "Registration failed.",
                "danger"
            )

            return redirect(
                url_for("register")
            )

        finally:

            connection.close()

    return render_template(
        "register.html"
    )


# =========================================================
# LOGIN
# =========================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        connection = get_db_connection()

        if not connection:

            flash(
                "Database connection failed.",
                "danger"
            )

            return redirect(
                url_for("login")
            )

        try:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT *
                    FROM users
                    WHERE email = %s
                    """,
                    (email,)
                )

                user = cursor.fetchone()

        except Exception as e:

            print(
                "Login database error:",
                e
            )

            user = None

        finally:

            connection.close()

        if user and check_password_hash(
            user["password_hash"],
            password
        ):

            session["user_id"] = user["id"]
            session["name"] = user["name"]
            session["email"] = user["email"]
            session["role"] = user["role"]

            flash(
                f"Welcome back, {user['name']}!",
                "success"
            )

            return redirect(
                url_for("dashboard")
            )

        flash(
            "Invalid email or password.",
            "danger"
        )

    return render_template(
        "login.html"
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(
        url_for("index")
    )


# =========================================================
# PROFILE
# =========================================================

@app.route(
    "/profile",
    methods=["GET", "POST"]
)
@login_required
def profile():

    user_id = session["user_id"]

    connection = get_db_connection()

    if not connection:

        flash(
            "Database connection failed.",
            "danger"
        )

        return redirect(
            url_for("dashboard")
        )

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        education = request.form.get(
            "education",
            ""
        ).strip()

        college = request.form.get(
            "college",
            ""
        ).strip()

        location = request.form.get(
            "location",
            ""
        ).strip()

        bio = request.form.get(
            "bio",
            ""
        ).strip()

        github = request.form.get(
            "github",
            ""
        ).strip()

        linkedin = request.form.get(
            "linkedin",
            ""
        ).strip()

        skills_text = request.form.get(
            "skills_text",
            ""
        ).strip()

        interests_text = request.form.get(
            "interests_text",
            ""
        ).strip()

        try:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    UPDATE users
                    SET
                        name = %s,
                        phone = %s,
                        education = %s,
                        college = %s,
                        location = %s,
                        bio = %s,
                        github = %s,
                        linkedin = %s,
                        skills_text = %s,
                        interests_text = %s
                    WHERE id = %s
                    """,
                    (
                        name,
                        phone,
                        education,
                        college,
                        location,
                        bio,
                        github,
                        linkedin,
                        skills_text,
                        interests_text,
                        user_id
                    )
                )

            session["name"] = name

            flash(
                "Profile updated successfully.",
                "success"
            )

        except Exception as e:

            print(
                "Profile update error:",
                e
            )

            flash(
                "Could not update profile.",
                "danger"
            )

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT *
                FROM users
                WHERE id = %s
                """,
                (user_id,)
            )

            user = cursor.fetchone()

    finally:

        connection.close()

    skills = get_all_skills()
    interests = get_all_interests()

    return render_template(
        "profile.html",
        user=user,
        skills=skills,
        interests=interests
    )


# =========================================================
# RESUME PAGE
# =========================================================

@app.route(
    "/resume",
    methods=["GET", "POST"]
)
@login_required
def resume():

    user_id = session["user_id"]

    if request.method == "POST":

        if "resume" not in request.files:

            flash(
                "Please select a resume file.",
                "danger"
            )

            return redirect(
                url_for("resume")
            )

        file = request.files["resume"]

        if file.filename == "":

            flash(
                "Please select a resume file.",
                "danger"
            )

            return redirect(
                url_for("resume")
            )

        if not allowed_file(
            file.filename
        ):

            flash(
                "Only PDF, DOCX and DOC files are allowed.",
                "danger"
            )

            return redirect(
                url_for("resume")
            )

        filename = secure_filename(
            file.filename
        )

        filename = f"{user_id}_{filename}"

        filepath = os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename
        )

        file.save(filepath)

        resume_text = extract_text_from_resume(
            filepath
        )

        detected_skills = extract_skills_from_text(
            resume_text
        )

        resume_score = calculate_resume_score(
            detected_skills
        )

        connection = get_db_connection()

        if connection:

            try:

                with connection.cursor() as cursor:

                    cursor.execute(
                        """
                        UPDATE users
                        SET
                            resume_filename = %s,
                            resume_score = %s,
                            resume_text = %s
                        WHERE id = %s
                        """,
                        (
                            filename,
                            resume_score,
                            resume_text,
                            user_id
                        )
                    )

            except Exception as e:

                print(
                    "Resume database error:",
                    e
                )

            finally:

                connection.close()

        flash(
            f"Resume uploaded successfully! Score: {resume_score}/100",
            "success"
        )

        return redirect(
            url_for("resume")
        )

    user = get_user_by_id(
        user_id
    )

    return render_template(
        "resume.html",
        user=user
    )


# =========================================================
# RESUME DOWNLOAD
# =========================================================

@app.route("/resume/download")
@login_required
def download_resume():

    user_id = session["user_id"]

    user = get_user_by_id(
        user_id
    )

    if not user or not user.get(
        "resume_filename"
    ):

        flash(
            "No resume uploaded.",
            "warning"
        )

        return redirect(
            url_for("resume")
        )

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        user["resume_filename"],
        as_attachment=True
    )


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
@login_required
def dashboard():

    user_id = session["user_id"]

    user = get_user_by_id(
        user_id
    )

    connection = get_db_connection()

    opportunities = []

    if connection:

        try:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT *
                    FROM opportunities
                    ORDER BY created_at DESC
                    LIMIT 6
                    """
                )

                opportunities = list(
                    cursor.fetchall()
                )

        except Exception as e:

            print(
                "Dashboard opportunities error:",
                e
            )

        finally:

            connection.close()

    return render_template(
        "dashboard.html",
        user=user,
        opportunities=opportunities
    )


# =========================================================
# MATCHING ALGORITHM
# =========================================================

def calculate_match_score(
    user_skills,
    user_interests,
    opportunity_skills,
    opportunity_interests
):

    user_skill_names = {
        skill["name"].lower()
        for skill in user_skills
    }

    user_interest_names = {
        interest["name"].lower()
        for interest in user_interests
    }

    opportunity_skill_names = {
        skill["name"].lower()
        for skill in opportunity_skills
    }

    opportunity_interest_names = {
        interest["name"].lower()
        for interest in opportunity_interests
    }

    skill_score = (
        len(
            user_skill_names
            &
            opportunity_skill_names
        )
        /
        len(opportunity_skill_names)
        *
        100
    ) if opportunity_skill_names else 0

    interest_score = (
        len(
            user_interest_names
            &
            opportunity_interest_names
        )
        /
        len(opportunity_interest_names)
        *
        100
    ) if opportunity_interest_names else 0

    return round(
        skill_score * 0.70
        +
        interest_score * 0.30
    )


# =========================================================
# GET OPPORTUNITIES
# =========================================================

def get_opportunities():

    connection = get_db_connection()

    if not connection:
        return []

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT *
                FROM opportunities
                ORDER BY created_at DESC
                """
            )

            # IMPORTANT:
            # Convert fetchall result into a real list.
            opportunities = list(
                cursor.fetchall()
            )

            for opportunity in opportunities:

                cursor.execute(
                    """
                    SELECT
                        s.id,
                        s.name
                    FROM skills s
                    INNER JOIN opportunity_skills os
                        ON s.id = os.skill_id
                    WHERE os.opportunity_id = %s
                    """,
                    (opportunity["id"],)
                )

                opportunity["skills"] = list(
                    cursor.fetchall()
                )

                cursor.execute(
                    """
                    SELECT
                        i.id,
                        i.name
                    FROM interests i
                    INNER JOIN opportunity_interests oi
                        ON i.id = oi.interest_id
                    WHERE oi.opportunity_id = %s
                    """,
                    (opportunity["id"],)
                )

                opportunity["interests"] = list(
                    cursor.fetchall()
                )

        return opportunities

    except Exception as e:

        print(
            "Get opportunities error:",
            e
        )

        return []

    finally:

        connection.close()


# =========================================================
# MATCHES
# =========================================================

@app.route("/matches")
@login_required
def matches():

    user_id = session["user_id"]

    user_skills = get_user_skills(
        user_id
    )

    user_interests = get_user_interests(
        user_id
    )

    opportunities = list(
        get_opportunities()
    )

    for opportunity in opportunities:

        opportunity["score"] = calculate_match_score(
            user_skills,
            user_interests,
            opportunity.get("skills", []),
            opportunity.get("interests", [])
        )

    opportunities.sort(
        key=lambda x: x.get("score", 0),
        reverse=True
    )

    return render_template(
        "matches.html",
        opportunities=opportunities,
        matches=opportunities
    )


# =========================================================
# JOBS
# =========================================================

@app.route("/jobs")
@login_required
def jobs():

    user_id = session["user_id"]

    user_skills = get_user_skills(
        user_id
    )

    user_interests = get_user_interests(
        user_id
    )

    opportunities = list(
        get_opportunities()
    )

    jobs = [
        opportunity
        for opportunity in opportunities
        if str(
            opportunity.get("type", "")
        ).lower() == "job"
    ]

    for job in jobs:

        job["score"] = calculate_match_score(
            user_skills,
            user_interests,
            job.get("skills", []),
            job.get("interests", [])
        )

    jobs.sort(
        key=lambda x: x.get("score", 0),
        reverse=True
    )

    return render_template(
        "matches.html",
        opportunities=jobs,
        matches=jobs,
        page_title="Job Matching"
    )


# =========================================================
# PROJECTS
# =========================================================

@app.route("/projects")
@login_required
def projects():

    user_id = session["user_id"]

    user_skills = get_user_skills(
        user_id
    )

    user_interests = get_user_interests(
        user_id
    )

    opportunities = list(
        get_opportunities()
    )

    projects = [
        opportunity
        for opportunity in opportunities
        if str(
            opportunity.get("type", "")
        ).lower() == "project"
    ]

    for project in projects:

        project["score"] = calculate_match_score(
            user_skills,
            user_interests,
            project.get("skills", []),
            project.get("interests", [])
        )

    projects.sort(
        key=lambda x: x.get("score", 0),
        reverse=True
    )

    return render_template(
        "matches.html",
        opportunities=projects,
        matches=projects,
        page_title="Project Matching"
    )


# =========================================================
# OPPORTUNITY DETAILS
# =========================================================

@app.route(
    "/opportunity/<int:opportunity_id>"
)
@login_required
def opportunity(opportunity_id):

    connection = get_db_connection()

    if not connection:

        flash(
            "Database connection failed.",
            "danger"
        )

        return redirect(
            url_for("matches")
        )

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT *
                FROM opportunities
                WHERE id = %s
                """,
                (opportunity_id,)
            )

            opportunity_data = cursor.fetchone()

            if not opportunity_data:

                flash(
                    "Opportunity not found.",
                    "warning"
                )

                return redirect(
                    url_for("matches")
                )

            cursor.execute(
                """
                SELECT
                    s.id,
                    s.name
                FROM skills s
                INNER JOIN opportunity_skills os
                    ON s.id = os.skill_id
                WHERE os.opportunity_id = %s
                """,
                (opportunity_id,)
            )

            opportunity_data["skills"] = list(
                cursor.fetchall()
            )

            cursor.execute(
                """
                SELECT
                    i.id,
                    i.name
                FROM interests i
                INNER JOIN opportunity_interests oi
                    ON i.id = oi.interest_id
                WHERE oi.opportunity_id = %s
                """,
                (opportunity_id,)
            )

            opportunity_data["interests"] = list(
                cursor.fetchall()
            )

    except Exception as e:

        print(
            "Opportunity error:",
            e
        )

        flash(
            "Could not load opportunity.",
            "danger"
        )

        return redirect(
            url_for("matches")
        )

    finally:

        connection.close()

    user_skills = get_user_skills(
        session["user_id"]
    )

    user_interests = get_user_interests(
        session["user_id"]
    )

    opportunity_data["score"] = calculate_match_score(
        user_skills,
        user_interests,
        opportunity_data.get("skills", []),
        opportunity_data.get("interests", [])
    )

    return render_template(
        "opportunity.html",
        opportunity=opportunity_data
    )


# =========================================================
# APPLY
# =========================================================

@app.route(
    "/apply/<int:opportunity_id>",
    methods=["POST"]
)
@login_required
def apply(opportunity_id):

    user_id = session["user_id"]

    connection = get_db_connection()

    if not connection:

        flash(
            "Database connection failed.",
            "danger"
        )

        return redirect(
            url_for(
                "opportunity",
                opportunity_id=opportunity_id
            )
        )

    try:

        with connection.cursor() as cursor:

            # Check opportunity exists
            cursor.execute(
                """
                SELECT id
                FROM opportunities
                WHERE id = %s
                """,
                (opportunity_id,)
            )

            opportunity_exists = cursor.fetchone()

            if not opportunity_exists:

                flash(
                    "Opportunity not found.",
                    "warning"
                )

                return redirect(
                    url_for("matches")
                )

            # Check existing application
            cursor.execute(
                """
                SELECT id
                FROM applications
                WHERE user_id = %s
                AND opportunity_id = %s
                """,
                (
                    user_id,
                    opportunity_id
                )
            )

            existing_application = cursor.fetchone()

            if existing_application:

                flash(
                    "You have already applied.",
                    "info"
                )

            else:

                cursor.execute(
                    """
                    INSERT INTO applications
                    (
                        user_id,
                        opportunity_id,
                        status
                    )
                    VALUES
                    (
                        %s,
                        %s,
                        'Applied'
                    )
                    """,
                    (
                        user_id,
                        opportunity_id
                    )
                )

                flash(
                    "Application submitted successfully!",
                    "success"
                )

    except Exception as e:

        print(
            "Application error:",
            e
        )

        flash(
            "Could not submit application.",
            "danger"
        )

    finally:

        connection.close()

    return redirect(
        url_for(
            "opportunity",
            opportunity_id=opportunity_id
        )
    )


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route("/admin")
@admin_required
def admin():

    connection = get_db_connection()

    if not connection:

        flash(
            "Database connection failed.",
            "danger"
        )

        return redirect(
            url_for("dashboard")
        )

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    id,
                    name,
                    email,
                    role,
                    created_at
                FROM users
                ORDER BY created_at DESC
                """
            )

            users = list(
                cursor.fetchall()
            )

            cursor.execute(
                """
                SELECT *
                FROM opportunities
                ORDER BY created_at DESC
                """
            )

            opportunities = list(
                cursor.fetchall()
            )

            cursor.execute(
                """
                SELECT
                    a.id,
                    a.status,
                    a.applied_at,
                    u.name AS user_name,
                    u.email AS user_email,
                    o.title AS opportunity_title
                FROM applications a
                INNER JOIN users u
                    ON a.user_id = u.id
                INNER JOIN opportunities o
                    ON a.opportunity_id = o.id
                ORDER BY a.applied_at DESC
                """
            )

            applications = list(
                cursor.fetchall()
            )

    except Exception as e:

        print(
            "Admin error:",
            e
        )

        flash(
            "Could not load admin dashboard.",
            "danger"
        )

        return redirect(
            url_for("dashboard")
        )

    finally:

        connection.close()

    return render_template(
        "admin.html",
        users=users,
        opportunities=opportunities,
        applications=applications
    )


# =========================================================
# ADMIN ADD OPPORTUNITY
# =========================================================

@app.route(
    "/admin/opportunity",
    methods=["POST"]
)
@admin_required
def admin_opportunity():

    title = request.form.get(
        "title",
        ""
    ).strip()

    description = request.form.get(
        "description",
        ""
    ).strip()

    opportunity_type = request.form.get(
        "type",
        "Job"
    ).strip()

    company = request.form.get(
        "company",
        ""
    ).strip()

    location = request.form.get(
        "location",
        ""
    ).strip()

    deadline = request.form.get(
        "deadline",
        ""
    ).strip()

    skills_text = request.form.get(
        "skills",
        ""
    ).strip()

    interests_text = request.form.get(
        "interests",
        ""
    ).strip()

    if not title:

        flash(
            "Opportunity title is required.",
            "danger"
        )

        return redirect(
            url_for("admin")
        )

    connection = get_db_connection()

    if not connection:

        flash(
            "Database connection failed.",
            "danger"
        )

        return redirect(
            url_for("admin")
        )

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO opportunities
                (
                    title,
                    description,
                    type,
                    company,
                    location,
                    deadline
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    title,
                    description,
                    opportunity_type,
                    company,
                    location,
                    deadline if deadline else None
                )
            )

            opportunity_id = cursor.lastrowid

            # -------------------------------------------------
            # ADD SKILLS
            # -------------------------------------------------

            skill_names = [
                x.strip()
                for x in skills_text.split(",")
                if x.strip()
            ]

            for skill_name in skill_names:

                cursor.execute(
                    """
                    SELECT id
                    FROM skills
                    WHERE LOWER(name) = LOWER(%s)
                    """,
                    (skill_name,)
                )

                skill = cursor.fetchone()

                if skill:

                    cursor.execute(
                        """
                        INSERT INTO opportunity_skills
                        (
                            opportunity_id,
                            skill_id
                        )
                        VALUES
                        (
                            %s,
                            %s
                        )
                        """,
                        (
                            opportunity_id,
                            skill["id"]
                        )
                    )

            # -------------------------------------------------
            # ADD INTERESTS
            # -------------------------------------------------

            interest_names = [
                x.strip()
                for x in interests_text.split(",")
                if x.strip()
            ]

            for interest_name in interest_names:

                cursor.execute(
                    """
                    SELECT id
                    FROM interests
                    WHERE LOWER(name) = LOWER(%s)
                    """,
                    (interest_name,)
                )

                interest = cursor.fetchone()

                if interest:

                    cursor.execute(
                        """
                        INSERT INTO opportunity_interests
                        (
                            opportunity_id,
                            interest_id
                        )
                        VALUES
                        (
                            %s,
                            %s
                        )
                        """,
                        (
                            opportunity_id,
                            interest["id"]
                        )
                    )

        flash(
            "Opportunity added successfully.",
            "success"
        )

    except Exception as e:

        print(
            "Admin opportunity error:",
            e
        )

        flash(
            "Could not create opportunity.",
            "danger"
        )

    finally:

        connection.close()

    return redirect(
        url_for("admin")
    )


# =========================================================
# 404 ERROR
# =========================================================

@app.errorhandler(404)
def page_not_found(error):

    return render_template(
        "index.html"
    ), 404


# =========================================================
# 413 ERROR
# =========================================================

@app.errorhandler(413)
def file_too_large(error):

    flash(
        "File is too large. Maximum size is 10 MB.",
        "danger"
    )

    return redirect(
        url_for("resume")
    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )