import sqlite3

database = "instance/fairapp.db"

connection = sqlite3.connect(database)
cursor = connection.cursor()

# -----------------------------
# FIX USER TABLE
# -----------------------------

user_columns = [
    column[1]
    for column in cursor.execute(
        "PRAGMA table_info(user)"
    ).fetchall()
]

if "created_at" not in user_columns:
    cursor.execute(
        "ALTER TABLE user ADD COLUMN created_at DATETIME"
    )
    print("Added user.created_at")


# -----------------------------
# FIX LOAN TABLE
# -----------------------------

loan_columns = [
    column[1]
    for column in cursor.execute(
        "PRAGMA table_info(loan)"
    ).fetchall()
]

if "repayment_status" not in loan_columns:
    cursor.execute(
        "ALTER TABLE loan ADD COLUMN repayment_status VARCHAR(30)"
    )
    print("Added loan.repayment_status")


if "created_at" not in loan_columns:
    cursor.execute(
        "ALTER TABLE loan ADD COLUMN created_at DATETIME"
    )
    print("Added loan.created_at")


# -----------------------------
# SAVE CHANGES
# -----------------------------

connection.commit()
connection.close()

print()
print("====================================")
print(" FAIRAPP DATABASE FIXED SUCCESSFULLY ")
print("====================================")