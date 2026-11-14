import os
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


# =========================================================
# FAIRAPP CONFIGURATION
# =========================================================

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "temporary-development-key")

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///fairapp.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# =========================================================
# USER MODEL
# =========================================================

class User(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(120),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    phone = db.Column(
        db.String(20),
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    verification_status = db.Column(
        db.String(30),
        default="Pending"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    loans = db.relationship(
        "Loan",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )


# =========================================================
# LOAN MODEL
# =========================================================

class Loan(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    amount = db.Column(
        db.Float,
        nullable=False
    )

    purpose = db.Column(
        db.String(500),
        nullable=False
    )

    repayment_period = db.Column(
        db.String(50),
        nullable=False
    )

    security_type = db.Column(
        db.String(100),
        nullable=False
    )

    guarantor_name = db.Column(
        db.String(120)
    )

    guarantor_phone = db.Column(
        db.String(30)
    )

    status = db.Column(
        db.String(30),
        default="Pending"
    )

    repayment_status = db.Column(
        db.String(30),
        default="Not Started"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


# =========================================================
# DATABASE CREATION
# =========================================================

with app.app_context():

    db.create_all()


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def index():

    total_members = User.query.count()

    total_loans = Loan.query.count()

    approved_loans = Loan.query.filter_by(
        status="Approved"
    ).count()

    pending_loans = Loan.query.filter_by(
        status="Pending"
    ).count()

    total_amount = db.session.query(
        db.func.sum(Loan.amount)
    ).filter(
        Loan.status == "Approved"
    ).scalar()

    if total_amount is None:
        total_amount = 0

    return render_template(
        "index.html",
        total_members=total_members,
        total_loans=total_loans,
        approved_loans=approved_loans,
        pending_loans=pending_loans,
        total_amount=total_amount
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

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        # Password validation
        if len(password) < 8:

            flash(
                "Password must contain at least 8 characters.",
                "error"
            )

            return redirect(
                url_for("register")
            )

        # Check existing email
        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:

            flash(
                "Email already registered. Please login.",
                "error"
            )

            return redirect(
                url_for("login")
            )

        # Create user
        new_user = User(

            name=name,

            email=email,

            phone=phone,

            password=generate_password_hash(
                password
            ),

            verification_status="Pending"
        )

        db.session.add(new_user)

        db.session.commit()

        flash(
            "Account created successfully. Please login.",
            "success"
        )

        return redirect(
            url_for("login")
        )

    return render_template(
        "register.html"
    )


# =========================================================
# USER LOGIN
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

        user = User.query.filter_by(
            email=email
        ).first()

        if user and check_password_hash(
            user.password,
            password
        ):

            session["user_id"] = user.id

            session["user_name"] = user.name

            flash(
                "Welcome back to FairApp!",
                "success"
            )

            return redirect(
                url_for("dashboard")
            )

        flash(
            "Invalid email or password.",
            "error"
        )

    return render_template(
        "login.html"
    )


# =========================================================
# USER LOGOUT
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
# DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    # Get all registered members
    total_members = User.query.count()

    # Get ALL loan applications
    all_loans = Loan.query.order_by(
        Loan.id.desc()
    ).all()

    # Loan statistics
    total_loans = len(all_loans)

    pending_loans = len([
        loan for loan in all_loans
        if loan.status == "Pending"
    ])

    approved_loans = len([
        loan for loan in all_loans
        if loan.status == "Approved"
    ])

    rejected_loans = len([
        loan for loan in all_loans
        if loan.status == "Rejected"
    ])

    # Add applicant name
    loan_data = []

    for loan in all_loans:

        user = User.query.get(
            loan.user_id
        )

        if user:

            applicant_name = user.name

        else:

            applicant_name = "Unknown Applicant"

        loan.applicant_name = applicant_name

        loan_data.append(loan)

    return render_template(

        "dashboard.html",

        loans=loan_data,

        total_members=total_members,

        total_loans=total_loans,

        pending_loans=pending_loans,

        approved_loans=approved_loans,

        rejected_loans=rejected_loans
    )


# =========================================================
# VERIFY USER
# =========================================================

@app.route(
    "/verify",
    methods=["GET", "POST"]
)
def verify():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    user = User.query.get(
        session["user_id"]
    )

    if request.method == "POST":

        user.verification_status = "Verified"

        db.session.commit()

        flash(
            "Your account has been submitted for verification.",
            "success"
        )

        return redirect(
            url_for("dashboard")
        )

    return render_template(
        "verify.html",
        user=user
    )


# =========================================================
# APPLY FOR LOAN
# =========================================================

@app.route(
    "/apply-loan",
    methods=["GET", "POST"]
)
@app.route(
    "/apply_loan",
    methods=["GET", "POST"]
)
def apply_loan():

    if "user_id" not in session:

        flash(
            "Please login before applying for a loan.",
            "error"
        )

        return redirect(
            url_for("login")
        )

    if request.method == "POST":

        amount_text = request.form.get(
            "amount",
            ""
        ).strip()

        purpose = request.form.get(
            "purpose",
            ""
        ).strip()

        repayment_period = request.form.get(
            "repayment_period",
            ""
        ).strip()

        security_type = request.form.get(
            "security_type",
            ""
        ).strip()

        guarantor_name = request.form.get(
            "guarantor_name",
            ""
        ).strip()

        guarantor_phone = request.form.get(
            "guarantor_phone",
            ""
        ).strip()

        # Validate amount
        try:

            amount = float(
                amount_text
            )

        except ValueError:

            flash(
                "Please enter a valid loan amount.",
                "error"
            )

            return redirect(
                url_for("apply_loan")
            )

        if amount <= 0:

            flash(
                "Loan amount must be greater than zero.",
                "error"
            )

            return redirect(
                url_for("apply_loan")
            )

        # Validate security
        if not security_type:

            flash(
                "Please select a security type.",
                "error"
            )

            return redirect(
                url_for("apply_loan")
            )

        # Guarantor validation
        if security_type.lower() in [
            "guarantor",
            "guarantor / co-signer",
            "guarantor/co-signer"
        ]:

            if not guarantor_name or not guarantor_phone:

                flash(
                    "Please enter guarantor name and phone number.",
                    "error"
                )

                return redirect(
                    url_for("apply_loan")
                )

        new_loan = Loan(

            user_id=session["user_id"],

            amount=amount,

            purpose=purpose,

            repayment_period=repayment_period,

            security_type=security_type,

            guarantor_name=guarantor_name,

            guarantor_phone=guarantor_phone,

            status="Pending",

            repayment_status="Not Started"
        )

        db.session.add(
            new_loan
        )

        db.session.commit()

        flash(
            "Loan application submitted successfully. It is waiting for admin approval.",
            "success"
        )

        return redirect(
            url_for("dashboard")
        )

    return render_template(
        "apply_loan.html"
    )


# =========================================================
# REPAYMENT
# =========================================================

@app.route(
    "/repayment",
    methods=["GET", "POST"]
)
def repayment():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    user_loans = Loan.query.filter_by(
        user_id=session["user_id"]
    ).all()

    approved_loans = [

        loan

        for loan in user_loans

        if loan.status == "Approved"

    ]

    if request.method == "POST":

        loan_id = request.form.get(
            "loan_id"
        )

        loan = Loan.query.filter_by(

            id=loan_id,

            user_id=session["user_id"]

        ).first()

        if loan:

            loan.repayment_status = "Paid"

            db.session.commit()

            flash(
                "Repayment recorded successfully.",
                "success"
            )

        return redirect(
            url_for("repayment")
        )

    return render_template(
        "repayment.html",
        loans=approved_loans
    )


# =========================================================
# ADMIN PANEL
# NO PASSWORD REQUIRED
# =========================================================

@app.route("/admin")
def admin():

    # Get all users
    users = User.query.order_by(
        User.created_at.desc()
    ).all()

    # Get all loans
    loans = Loan.query.order_by(
        Loan.created_at.desc()
    ).all()

    # Statistics
    total_members = User.query.count()

    total_applications = Loan.query.count()

    pending_loans = Loan.query.filter_by(
        status="Pending"
    ).count()

    approved_loans = Loan.query.filter_by(
        status="Approved"
    ).count()

    rejected_loans = Loan.query.filter_by(
        status="Rejected"
    ).count()

    total_approved_amount = db.session.query(
        db.func.sum(Loan.amount)
    ).filter(
        Loan.status == "Approved"
    ).scalar()

    if total_approved_amount is None:

        total_approved_amount = 0

    return render_template(

        "admin.html",

        users=users,

        loans=loans,

        total_members=total_members,

        total_applications=total_applications,

        pending_loans=pending_loans,

        approved_loans=approved_loans,

        rejected_loans=rejected_loans,

        total_approved_amount=total_approved_amount
    )


# =========================================================
# APPROVE LOAN
# =========================================================

@app.route(
    "/admin/approve/<int:loan_id>",
    methods=["POST"]
)
def approve_loan(loan_id):

    loan = Loan.query.get_or_404(
        loan_id
    )

    # Only pending applications
    # can be approved
    if loan.status == "Pending":

        loan.status = "Approved"

        db.session.commit()

        flash(
            "Loan approved successfully.",
            "success"
        )

    return redirect(
        url_for("admin")
    )


# =========================================================
# REJECT LOAN
# =========================================================

@app.route(
    "/admin/reject/<int:loan_id>",
    methods=["POST"]
)
def reject_loan(loan_id):

    loan = Loan.query.get_or_404(
        loan_id
    )

    # Only pending applications
    # can be rejected
    if loan.status == "Pending":

        loan.status = "Rejected"

        db.session.commit()

        flash(
            "Loan rejected.",
            "success"
        )

    return redirect(
        url_for("admin")
    )


# =========================================================
# RUN FAIRAPP
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )
