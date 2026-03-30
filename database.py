import oracledb
import os
import pandas as pd
import streamlit as st
import datetime
import uuid
import hashlib

@st.cache_resource
def get_connection():
    try:
        user = st.secrets.get("DB_USER", os.getenv("DB_USER", "system"))
        password = st.secrets.get("DB_PASSWORD", os.getenv("DB_PASSWORD", "oracle"))
        dsn = st.secrets.get("DB_DSN", os.getenv("DB_DSN", "localhost:1521/xepdb1"))
        
        # Thin mode is default
        oracledb.init_oracle_client() 
        connection = oracledb.connect(user=user, password=password, dsn=dsn)
        return connection
    except Exception as e:
        try:
            user = st.secrets.get("DB_USER", os.getenv("DB_USER", "system"))
            password = st.secrets.get("DB_PASSWORD", os.getenv("DB_PASSWORD", "oracle"))
            dsn = st.secrets.get("DB_DSN", os.getenv("DB_DSN", "localhost:1521/xepdb1"))
            connection = oracledb.connect(user=user, password=password, dsn=dsn)
            return connection
        except Exception as inner_e:
            st.error(f"Error connecting to Oracle Database: {inner_e}")
            return None

def sanitize_params(params):
    # Oracle's DPY-3002 error triggers on numpy.int64 and numpy.float64
    # We convert them back to native int/float using .item()
    if isinstance(params, (list, tuple)):
        sanitized = []
        for p in params:
            if hasattr(p, 'item') and callable(getattr(p, 'item')):
                sanitized.append(p.item())
            else:
                sanitized.append(p)
        return type(params)(sanitized)
    elif isinstance(params, dict):
        sanitized = {}
        for k, p in params.items():
            if hasattr(p, 'item') and callable(getattr(p, 'item')):
                sanitized[k] = p.item()
            else:
                sanitized[k] = p
        return sanitized
    return params

def fetch_data(query, params=()):
    conn = get_connection()
    if conn:
        try:
            clean_params = sanitize_params(params)
            df = pd.read_sql(query, conn, params=clean_params)
            return df
        except Exception as e:
            st.error(f"Error fetching data: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

def execute_query(query, params=()):
    conn = get_connection()
    if conn:
        try:
            clean_params = sanitize_params(params)
            cursor = conn.cursor()
            cursor.execute(query, clean_params)
            conn.commit()
            count = cursor.rowcount
            cursor.close()
            # print(f"DEBUG: Executed Query: {query} | Params: {clean_params} | Count: {count}")
            return count
        except Exception as e:
            st.error(f"Error executing query: {e}")
            # print(f"DEBUG ERROR: Query: {query} | Params: {params} | Error: {e}")
            return -1
    return False
def call_procedure_standard_out(proc_name, params):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            status_var = cursor.var(str)
            message_var = cursor.var(str)
            clean_params = sanitize_params(list(params))
            proc_params = clean_params + [status_var, message_var]
            cursor.callproc(proc_name, proc_params)
            conn.commit()
            val_status = status_var.getvalue()
            val_msg = message_var.getvalue()
            cursor.close()
            if val_status == 'SUCCESS':
                st.success(val_msg)
                return 1
            else:
                st.error(val_msg)
                return -1
        except Exception as e:
            st.error(f"Error executing procedure {proc_name}: {e}")
            return -1
    return False

# --- AUTHENTICATION ---
def authenticate_user(username, password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    query = """
    SELECT USER_ID, ROLE, CLUB_ID, STUDENT_ID 
    FROM APP_USERS 
    WHERE LOWER(USERNAME) = LOWER(:1) AND PASSWORD = :2 AND IS_ACTIVE = 'Y'
    """
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(query, (username, hashed_password))
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                return {
                    "user_id": result[0],
                    "role": result[1],
                    "club_id": result[2],
                    "student_id": result[3]
                }
        except Exception as e:
            st.error(f"Error authenticating: {e}")
            return None
    return None

def get_all_users():
    return fetch_data("SELECT * FROM APP_USERS ORDER BY USER_ID DESC")

def add_app_user(username, password, role, club_id=None, student_id=None):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    query = """INSERT INTO APP_USERS (USERNAME, PASSWORD, ROLE, CLUB_ID, STUDENT_ID) 
               VALUES (:1, :2, :3, :4, :5)"""
    return execute_query(query, (username, hashed_password, role, club_id, student_id))

def deactivate_user(user_id):
    return execute_query("UPDATE APP_USERS SET IS_ACTIVE = 'N' WHERE USER_ID = :1", [user_id])

def activate_user(user_id):
    return execute_query("UPDATE APP_USERS SET IS_ACTIVE = 'Y' WHERE USER_ID = :1", [user_id])


# --- MASTER DATA ---

# CLUBS
def get_all_clubs():
    return fetch_data("SELECT * FROM CLUBS ORDER BY CLUB_ID DESC")

def get_club_by_id(club_id):
    return fetch_data("SELECT * FROM CLUBS WHERE CLUB_ID = :1", [club_id])

def add_club(name, c_type, desc, email, contact, year):
    return call_procedure_standard_out('proc_add_club', [name, c_type, desc, email, contact, year])

def update_club(club_id, name, c_type, desc, email, contact, year):
    return call_procedure_standard_out('proc_update_club', [club_id, name, c_type, desc, email, contact, year])

def delete_club(club_id):
    return call_procedure_standard_out('proc_delete_club', [club_id])

# STUDENTS
def get_all_students():
    return fetch_data("SELECT * FROM STUDENTS ORDER BY STUDENT_ID DESC")

def get_student_by_id(student_id):
    return fetch_data("SELECT * FROM STUDENTS WHERE STUDENT_ID = :1", [student_id])

def add_student(name, roll_no, dept, sem, email, phone):
    return call_procedure_standard_out('proc_add_student', [name, roll_no, dept, sem, email, phone])

def update_student(student_id, name, roll_no, dept, sem, email, phone):
    return call_procedure_standard_out('proc_update_student', [student_id, name, roll_no, dept, sem, email, phone])

def delete_student(student_id):
    return call_procedure_standard_out('proc_delete_student', [student_id])

# VENUES
def get_all_venues():
    return fetch_data("SELECT * FROM VENUES ORDER BY VENUE_ID DESC")

def add_venue(name, location, capacity, v_type):
    return call_procedure_standard_out('proc_add_venue', [name, location, capacity, v_type])


# --- TRANSACTION DATA (EVENTS) ---
def get_all_events():
    return fetch_data("SELECT * FROM EVENTS ORDER BY EVENT_ID DESC")

def get_events_by_club(club_id):
    query = "SELECT * FROM EVENTS WHERE CLUB_ID = :1 ORDER BY EVENT_DATE DESC"
    return fetch_data(query, [club_id])

def get_upcoming_events():
    query = """
    SELECT e.EVENT_ID, c.CLUB_NAME, v.VENUE_NAME, e.EVENT_NAME, e.EVENT_CATEGORY, e.EVENT_DATE, 
           e.START_TIME, e.END_TIME, e.DESCRIPTION, e.REGISTRATION_DEADLINE, e.MAX_PARTICIPANTS
    FROM EVENTS e 
    JOIN CLUBS c ON e.CLUB_ID = c.CLUB_ID 
    JOIN VENUES v ON e.VENUE_ID = v.VENUE_ID 
    WHERE e.EVENT_STATUS = 'UPCOMING' 
    ORDER BY e.EVENT_DATE ASC
    """
    return fetch_data(query)

def get_event_details(event_id):
    query = """
    SELECT e.*, c.CLUB_NAME, v.VENUE_NAME
    FROM EVENTS e 
    JOIN CLUBS c ON e.CLUB_ID = c.CLUB_ID 
    JOIN VENUES v ON e.VENUE_ID = v.VENUE_ID 
    WHERE e.EVENT_ID = :1
    """
    return fetch_data(query, [event_id])

def add_event(club_id, venue_id, name, category, date, start, end, desc, status, deadline, max_p):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            status_var = cursor.var(str)
            message_var = cursor.var(str)
            event_id_var = cursor.var(int)
            
            clean_params = sanitize_params([club_id, venue_id, name, category, date, start, end, desc, deadline, max_p])
            proc_params = clean_params + [status_var, message_var, event_id_var]
            
            cursor.callproc('create_event', proc_params)
            conn.commit()
            
            val_status = status_var.getvalue()
            val_msg = message_var.getvalue()
            cursor.close()
            
            if val_status == 'SUCCESS':
                st.success(val_msg)
                return 1
            else:
                st.error(val_msg)
                return -1
        except Exception as e:
            st.error(f"Error executing procedure: {e}")
            return -1
    return False

def update_event(event_id, club_id, venue_id, name, category, date, start, end, desc, status, deadline, max_p):
    query = """
    UPDATE EVENTS SET VENUE_ID=:1, EVENT_NAME=:2, EVENT_CATEGORY=:3, EVENT_DATE=:4, START_TIME=:5, END_TIME=:6, 
                      DESCRIPTION=:7, EVENT_STATUS=:8, REGISTRATION_DEADLINE=:9, MAX_PARTICIPANTS=:10, UPDATED_AT=CURRENT_TIMESTAMP
    WHERE EVENT_ID=:11 AND CLUB_ID=:12"""
    return execute_query(query, (venue_id, name, category, date, start, end, desc, status, deadline, max_p, event_id, club_id))

def delete_event(event_id, club_id):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            status_var = cursor.var(str)
            message_var = cursor.var(str)
            
            clean_params = sanitize_params([event_id, club_id])
            proc_params = clean_params + [status_var, message_var]
            
            cursor.callproc('delete_event_by_club', proc_params)
            conn.commit()
            
            val_status = status_var.getvalue()
            val_msg = message_var.getvalue()
            cursor.close()
            
            if val_status == 'SUCCESS':
                st.success(val_msg)
                return 1
            else:
                st.error(val_msg)
                return -1
        except Exception as e:
            st.error(f"Error executing procedure: {e}")
            return -1
    return False


# --- TRANSACTION DATA (REGISTRATIONS) ---
def get_student_registrations(student_id):
    query = """
    SELECT e.EVENT_NAME, e.EVENT_DATE, e.START_TIME, r.REGISTRATION_STATUS, r.REGISTRATION_DATE, e.EVENT_STATUS, r.EVENT_ID
    FROM REGISTRATIONS r
    JOIN EVENTS e ON r.EVENT_ID = e.EVENT_ID
    WHERE r.STUDENT_ID = :1
    ORDER BY r.REGISTRATION_DATE DESC
    """
    return fetch_data(query, [student_id])

def get_registrations_for_event(event_id):
    query = """
    SELECT s.STUDENT_NAME, s.ROLL_NO, s.DEPARTMENT, s.EMAIL, r.REGISTRATION_DATE, r.REGISTRATION_STATUS
    FROM REGISTRATIONS r
    JOIN STUDENTS s ON r.STUDENT_ID = s.STUDENT_ID
    WHERE r.EVENT_ID = :1
    ORDER BY r.REGISTRATION_DATE DESC
    """
    return fetch_data(query, [event_id])

def register_for_event(student_id, event_id):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            status_var = cursor.var(str)
            message_var = cursor.var(str)
            
            clean_params = sanitize_params([event_id, student_id])
            proc_params = clean_params + [status_var, message_var]
            
            cursor.callproc('register_for_event', proc_params)
            conn.commit()
            
            val_status = status_var.getvalue()
            val_msg = message_var.getvalue()
            cursor.close()
            
            if val_status == 'SUCCESS':
                st.success(val_msg)
                return 1
            else:
                st.error(val_msg)
                return -1
        except Exception as e:
            st.error(f"Error executing procedure: {e}")
            return -1
    return False

def cancel_registration(student_id, event_id):
    query = "UPDATE REGISTRATIONS SET REGISTRATION_STATUS = 'CANCELLED' WHERE STUDENT_ID = :1 AND EVENT_ID = :2"
    return execute_query(query, (student_id, event_id))

def check_if_registered(student_id, event_id):
    query = "SELECT REGISTRATION_STATUS FROM REGISTRATIONS WHERE STUDENT_ID = :1 AND EVENT_ID = :2"
    res = fetch_data(query, (student_id, event_id))
    if not res.empty:
        return res.iloc[0, 0]  # returns 'REGISTERED' or 'CANCELLED'
    return None

    return execute_query(query, (event_id, student_id, rating, comments))

# --- ANNOUNCEMENTS ---
def get_announcements_by_club(club_id):
    query = """
    SELECT TITLE, MESSAGE, POSTED_AT 
    FROM ANNOUNCEMENTS 
    WHERE CLUB_ID = :1 
    ORDER BY POSTED_AT DESC
    """
    return fetch_data(query, [club_id])

def get_latest_announcements(limit=5):
    query = f"""
    SELECT a.TITLE, a.MESSAGE, a.POSTED_AT, c.CLUB_NAME 
    FROM ANNOUNCEMENTS a 
    JOIN CLUBS c ON a.CLUB_ID = c.CLUB_ID 
    ORDER BY a.POSTED_AT DESC 
    FETCH FIRST {limit} ROWS ONLY
    """
    return fetch_data(query)

def add_announcement(club_id, title, message):
    return call_procedure_standard_out('proc_add_announcement', [club_id, title, message])

# --- ATTENDANCE ---
def mark_attendance(event_id, roll_no):
    return call_procedure_standard_out('proc_mark_attendance', [event_id, roll_no])

def get_attendance_for_event(event_id):
    query = """
    SELECT s.STUDENT_NAME, s.ROLL_NO, s.DEPARTMENT, a.MARKED_AT 
    FROM ATTENDANCE a 
    JOIN STUDENTS s ON a.STUDENT_ID = s.STUDENT_ID 
    WHERE a.EVENT_ID = :1 
    ORDER BY a.MARKED_AT DESC
    """
    return fetch_data(query, [event_id])

# --- MEMBERSHIP ---
def join_club(student_id, club_id):
    return call_procedure_standard_out('proc_join_club', [student_id, club_id])

def get_student_memberships(student_id):
    query = """
    SELECT c.CLUB_NAME, m.MEMBER_ROLE, m.JOIN_DATE, m.STATUS, c.EMAIL 
    FROM MEMBERSHIP m 
    JOIN CLUBS c ON m.CLUB_ID = c.CLUB_ID 
    WHERE m.STUDENT_ID = :1
    """
    return fetch_data(query, [student_id])

def get_club_members(club_id):
    query = """
    SELECT m.MEMBERSHIP_ID, s.STUDENT_NAME, s.ROLL_NO, m.MEMBER_ROLE, m.JOIN_DATE, m.STATUS 
    FROM MEMBERSHIP m 
    JOIN STUDENTS s ON m.STUDENT_ID = s.STUDENT_ID 
    WHERE m.CLUB_ID = :1 
    ORDER BY s.STUDENT_NAME
    """
    return fetch_data(query, [club_id])

def update_member_role(membership_id, new_role):
    query = "UPDATE MEMBERSHIP SET MEMBER_ROLE = :1 WHERE MEMBERSHIP_ID = :2"
    return execute_query(query, [new_role, membership_id])

# --- SESSIONS ---
def create_session(user_id, ip="0.0.0.0"):
    token = str(uuid.uuid4())
    query = "INSERT INTO USER_SESSIONS (SESSION_TOKEN, USER_ID, IP_ADDRESS) VALUES (:1, :2, :3)"
    if execute_query(query, (token, user_id, ip)):
        return token
    return None

def validate_session(token):
    query = """
    SELECT u.USER_ID, u.ROLE, u.CLUB_ID, u.STUDENT_ID 
    FROM USER_SESSIONS s
    JOIN APP_USERS u ON s.USER_ID = u.USER_ID
    WHERE s.SESSION_TOKEN = :1 AND s.STATUS = 'ACTIVE'
    """
    res = fetch_data(query, [token])
    if not res.empty:
        return {
            "user_id": res.iloc[0]['USER_ID'],
            "role": res.iloc[0]['ROLE'],
            "club_id": res.iloc[0]['CLUB_ID'],
            "student_id": res.iloc[0]['STUDENT_ID']
        }
    return None

def delete_session(token):
    return execute_query("DELETE FROM USER_SESSIONS WHERE SESSION_TOKEN = :1", [token])
