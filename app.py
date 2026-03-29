import streamlit as st
import pandas as pd
import database as db
import datetime

st.set_page_config(page_title="Club Connect", layout="wide")

st.markdown("""
<style>
/* Global Styles */
.stApp { 
    background-color: #ffffff; 
    color: #2d2d2d; 
}

/* University Header */
.uni-header {
    background-color: #ffffff;
    padding: 1rem 2rem;
    border-bottom: 3px solid #8b1d1d;
    margin-bottom: 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.uni-logo {
    color: #8b1d1d;
    font-size: 24px;
    font-weight: 800;
    letter-spacing: -1px;
    text-transform: uppercase;
}

/* Force Global White Background and Black Text for ALL Inputs and Widgets */
input, textarea, select, div[data-baseweb="select"] > div {
    background-color: #ffffff !important;
    color: #000000 !important;
    caret-color: #000000 !important;
    border: 1px solid #8b1d1d !important;
}

/* Force ALL Labels and text to be black */
[data-testid="stWidgetLabel"] p, .stMarkdown p, .stMarkdown li, span, label, div, [data-testid="stHeader"] {
    color: #000000 !important;
}

/* Specific Streamlit Widget Selectors */
[data-testid="stTextInput"] input, 
[data-testid="stNumberInput"] input, 
[data-testid="stTextArea"] textarea,
[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
[data-testid="stDateInput"] input,
[data-testid="stTimeInput"] input {
    background-color: #ffffff !important;
    color: #000000 !important;
    border: 1px solid #8b1d1d !important;
    border-radius: 4px !important;
}

/* Dropdown / Selectbox internal arrow fix */
[data-testid="stSelectbox"] svg {
    fill: #8b1d1d !important;
    color: #8b1d1d !important;
}

/* Number Input + / - buttons fix */
[data-testid="stNumberInput"] button {
    background-color: #ffffff !important;
    color: #000000 !important;
    border: 1px solid #8b1d1d !important;
}
[data-testid="stNumberInput"] button:hover {
    background-color: #fef2f2 !important;
}

/* Autocomplete/Dropdown styling - Aggressive Overrides */
div[data-baseweb="popover"], 
div[data-baseweb="menu"], 
div[role="listbox"], 
ul[role="listbox"],
[data-baseweb="select"] + div,
[data-baseweb="popover"] * {
    background-color: #ffffff !important;
    color: #000000 !important;
}

div[role="option"], 
[data-baseweb="menu"] li,
div[data-baseweb="popover"] div {
    background-color: #ffffff !important;
    color: #000000 !important;
}

div[role="option"]:hover, 
[data-baseweb="menu"] li:hover,
div[data-baseweb="popover"] div:hover {
    background-color: #fef2f2 !important;
    color: #8b1d1d !important;
}

/* Tabs Styling */
button[data-baseweb="tab"] {
    background-color: #ffffff !important;
    color: #000000 !important;
    border: 1px solid #8b1d1d !important;
    border-bottom: none !important;
    margin-right: 5px !important;
    transition: all 0.3s ease !important;
}

button[data-baseweb="tab"]:hover {
    background-color: #8b1d1d !important;
    color: #ffffff !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    border-bottom: 3px solid #8b1d1d !important;
    color: #8b1d1d !important;
    font-weight: bold !important;
}

/* Dataframe/Table */
div[data-testid="stDataFrame"], div[data-testid="stTable"] {
    background-color: #ffffff !important;
    border: 2px solid #8b1d1d !important;
    border-radius: 8px !important;
    padding: 1px !important;
}

/* Aggressive internal grid lines for all table-like roles */
[data-testid="stDataFrame"] [role="gridcell"], 
[data-testid="stDataFrame"] [role="columnheader"],
[data-testid="stDataFrame"] td, 
[data-testid="stDataFrame"] th,
div[data-testid="stTable"] td,
div[data-testid="stTable"] th {
    border: 1px solid #8b1d1d !important;
    font-weight: bold !important;
    color: #000000 !important;
}

div[data-testid="stDataFrame"] *, div[data-testid="stTable"] * {
    background-color: #ffffff !important;
    color: #000000 !important;
}

/* Tab Panels (Information Tabs) */
[data-baseweb="tab-panel"] {
    background-color: #ffffff !important;
    color: #000000 !important;
    border: 1px solid #8b1d1d !important;
    padding: 2rem !important;
    border-radius: 0 0 8px 8px !important;
}

/* Typography */
h1, h2, h3 { 
    font-family: 'Playfair Display', serif; 
    color: #8b1d1d !important; 
    border-left: 10px solid #8b1d1d;
    padding-left: 20px;
    margin-bottom: 1.5rem !important;
}

/* Forms */
[data-testid="stForm"], .stForm { 
    background-color: #ffffff !important; 
    border: 1px solid #8b1d1d !important; 
    border-top: 8px solid #8b1d1d !important;
    border-radius: 8px !important; 
    box-shadow: 0 4px 20px rgba(0,0,0,0.1) !important; 
    padding: 3rem !important; 
}

/* Buttons (Regular, Nav, and Submit) */
.stButton button, [data-testid="baseButton-primary"], [data-testid="baseButton-secondary"], 
[data-testid="stFormSubmitButton"] button { 
    background-color: #ffffff !important; 
    color: #000000 !important; 
    border: 2px solid #8b1d1d !important;
    border-radius: 4px !important; 
    text-transform: uppercase;
    font-weight: 700 !important;
    padding: 0.6rem 2rem !important;
    transition: all 0.3s ease !important;
}

.stButton button:hover, [data-testid="stFormSubmitButton"] button:hover { 
    background-color: #8b1d1d !important; 
    color: #ffffff !important; 
}
</style>

<div class="uni-header">
    <div class="uni-logo">Club Connect</div>
    <div style="color: #666; font-size: 14px; font-weight: 600;">University Event Management</div>
</div>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.role = None
    st.session_state.club_id = None
    st.session_state.student_id = None

# Auto-login from URL session token
if not st.session_state.logged_in and "session" in st.query_params:
    token = st.query_params["session"]
    user = db.validate_session(token)
    if user:
        st.session_state.logged_in = True
        st.session_state.user_id = user["user_id"]
        st.session_state.role = user["role"]
        st.session_state.club_id = user["club_id"]
        st.session_state.student_id = user["student_id"]
        st.rerun()

def login():
    st.title("Login to Club Connect")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            user = db.authenticate_user(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user_id = user["user_id"]
                st.session_state.role = user["role"]
                st.session_state.club_id = user["club_id"]
                st.session_state.student_id = user["student_id"]
                
                # Create persistent session
                token = db.create_session(user["user_id"])
                if token:
                    st.query_params["session"] = token
                
                st.success(f"Welcome {username}! Logged in as {user['role']}")
                st.rerun()
            else:
                st.error("Invalid Username or Password")

def logout():
    # Remove from DB and URL
    token = st.query_params.get("session")
    if token:
        db.delete_session(token)
    st.query_params.clear()
    
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.role = None
    st.session_state.club_id = None
    st.session_state.student_id = None
    st.rerun()


if not st.session_state.logged_in:
    login()
else:
    role = st.session_state.role
    
    if role == "ADMIN":
        menu = ["Admin Dashboard", "Register Club", "Register Student", "Manage Clubs", "Manage Students", "Add Venue", "Logout"]
    elif role == "CLUB":
        menu = ["Club Dashboard", "My Profile", "Add Event", "My Events", "Edit/Delete My Events", "Logout"]
    elif role == "STUDENT":
        menu = ["Student Dashboard", "Browse Events", "Register for Event", "My Registrations", "Submit Feedback", "Logout"]
    else:
        menu = []
    
    # Custom Horizontal Navigation Bar (No Circles)
    if "choice" not in st.session_state:
        st.session_state.choice = menu[0]
        
    cols = st.columns(len(menu))
    for i, item in enumerate(menu):
        if cols[i].button(item, key=f"nav_{item}"):
            st.session_state.choice = item
            if item == "Logout":
                logout()
            st.rerun()
            
    choice = st.session_state.choice

    # Hero Section / Title
    st.markdown(f"<h1>🎓 {role} Control Center</h1>", unsafe_allow_html=True)

    # ---------------- ADMIN PANEL ----------------
    if role == "ADMIN":
        if choice == "Admin Dashboard":
            st.header("Admin Dashboard")
            st.write("Welcome to the Admin Panel. Use the navigation to manage master entities and accounts.")
            st.info("Remember: Admins manage accounts and profiles, but do not create events.")
            
        elif choice == "Register Club":
            st.header("Register a New Club")
            with st.form("club_form"):
                name = st.text_input("Club Name")
                c_type = st.selectbox("Club Type", ["Technical", "Cultural", "Sports", "Literary", "Social", "Other"])
                desc = st.text_area("Description")
                email = st.text_input("Email")
                contact = st.text_input("Contact Number")
                year = st.number_input("Founded Year", min_value=1900, max_value=2100, step=1)
                
                if st.form_submit_button("Register Club"):
                    res = db.add_club(name, c_type, desc, email, contact, year)
                    if res > 0:
                        st.success("Club registered and login account automatically created!")
                        # Small delay for visual feedback before refresh
                        import time
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Registration failed. Please check if the email is unique or all fields are correct.")

        elif choice == "Register Student":
            st.header("Register a New Student")
            with st.form("student_form"):
                name = st.text_input("Student Name")
                roll_no = st.text_input("Roll No")
                dept = st.text_input("Department")
                sem = st.number_input("Semester", min_value=1, max_value=12, step=1)
                email = st.text_input("Email")
                phone = st.text_input("Phone Number")
                
                if st.form_submit_button("Register Student"):
                    if db.add_student(name, roll_no, dept, sem, email, phone) > 0:
                        st.success(f"Student Registered Successfully! Login account created (Username: {name.lower().replace(' ', '')}, Password: {roll_no})")


        elif choice == "Manage Clubs":
            st.header("Manage Registered Clubs")
            clubs_df = db.get_all_clubs()
            if clubs_df.empty:
                st.info("No clubs registered yet. Go to 'Register Club' to add one.")
            else:
                st.table(clubs_df)
            
            tab1, tab2 = st.tabs(["Update Profile", "Delete Club"])
            with tab1:
                with st.form("update_club"):
                    c_id = st.number_input("Club ID to Update", min_value=1, step=1)
                    n_name = st.text_input("New Club Name")
                    n_type = st.text_input("New Type")
                    n_desc = st.text_area("New Description")
                    n_email = st.text_input("New Email")
                    n_contact = st.text_input("New Contact")
                    n_year = st.number_input("New Founded Year", min_value=1900, step=1)
                    if st.form_submit_button("Update Profile"):
                        if db.update_club(c_id, n_name, n_type, n_desc, n_email, n_contact, n_year) > 0:
                             st.success("Club updated!")
            with tab2:
                with st.form("delete_club_form"):
                    d_id = st.number_input("Club ID to Delete", min_value=1, step=1)
                    st.warning("Warning: Deleting a club will also delete its login account.")
                    if st.form_submit_button("Delete Club"):
                        if db.delete_club(d_id) > 0:
                            st.success("Club deleted!")

        elif choice == "Manage Students":
            st.header("Manage Registered Students")
            students_df = db.get_all_students()
            if students_df.empty:
                st.info("No students registered yet. Go to 'Register Student' to add one.")
            else:
                st.table(students_df)
            tab1, tab2 = st.tabs(["Update Profile", "Delete Student"])
            with tab1:
                with st.form("update_stud"):
                    s_id = st.number_input("Student ID to Update", min_value=1, step=1)
                    n_name = st.text_input("New Name")
                    n_roll = st.text_input("New Roll No")
                    n_dept = st.text_input("New Dept")
                    n_sem = st.number_input("New Sem", min_value=1, max_value=12, step=1)
                    n_email = st.text_input("New Email")
                    n_phone = st.text_input("New Phone")
                    if st.form_submit_button("Update Profile"):
                        if db.update_student(s_id, n_name, n_roll, n_dept, n_sem, n_email, n_phone) > 0:
                             st.success("Student updated!")

            with tab2:
                with st.form("delete_student_form"):
                    d_id = st.number_input("Student ID to Delete", min_value=1, step=1)
                    st.warning("Warning: Deleting a student will also delete their login account and all event history.")
                    if st.form_submit_button("Delete Student"):
                        if db.delete_student(d_id) > 0:
                            st.success("Student deleted!")
                         
        elif choice == "Add Venue":
            st.header("Venue Master")
            with st.form("add_ven"):
                vname = st.text_input("Venue Name")
                loc = st.text_input("Location")
                cap = st.number_input("Capacity", step=1)
                vtype = st.text_input("Type (e.g., Lab, Hall)")
                if st.form_submit_button("Add Venue"):
                    if db.add_venue(vname, loc, cap, vtype) > 0: st.success("Venue added")
                    
                    
    # ---------------- CLUB PANEL ----------------
    elif role == "CLUB":
        if choice == "Club Dashboard":
            st.header("Club Dashboard")
            st.write("Welcome host! From here you can manage your events and view your public profile.")
            events = db.get_events_by_club(st.session_state.club_id)
            if not events.empty:
                st.table(events)
            else:
                st.info("No events found for your club.")

        elif choice == "My Profile":
            st.header("My Club Profile")
            profile = db.get_club_by_id(st.session_state.club_id)
            if not profile.empty:
                for col in profile.columns:
                    st.write(f"**{col}:** {profile.iloc[0][col]}")
            else:
                st.write("Profile not found.")

        elif choice == "Add Event":
            st.header("Add New Event")
            
            # Fetch venues for dropdown
            venues_df = db.get_all_venues()
            if venues_df.empty:
                st.warning("No venues found. Please ask an Admin to add venues first.")
            else:
                venue_options = {f"{row['VENUE_NAME']} ({row['LOCATION']})": row['VENUE_ID'] for _, row in venues_df.iterrows()}
                
                with st.form("add_event_form"):
                    v_label = st.selectbox("Select Venue", options=list(venue_options.keys()))
                    venue_id = venue_options[v_label]
                    
                    name = st.text_input("Event Name")
                    category = st.selectbox("Event Category", ["TECHNICAL", "CULTURAL", "SPORTS", "LITERARY", "WORKSHOP", "SEMINAR", "COMPETITION"])
                    date = st.date_input("Event Date")
                    start = st.time_input("Start Time")
                    end = st.time_input("End Time")
                    desc = st.text_area("Description")
                    status = st.selectbox("Event Status", ["UPCOMING", "COMPLETED", "CANCELLED"])
                    deadline = st.date_input("Registration Deadline")
                    max_p = st.number_input("Max Participants", min_value=1, step=1)
                    
                    if st.form_submit_button("Create Event"):
                        full_start = datetime.datetime.combine(date, start)
                        full_end = datetime.datetime.combine(date, end)
                        result = db.add_event(st.session_state.club_id, venue_id, name, category, date, full_start, full_end, desc, status, deadline, max_p)
                        if result > 0:
                            st.success("Event added successfully!")
                        elif result == 0:
                             st.error("Event could not be added.")
                        # Errors are already shown by database.py via st.error if result is -1

        elif choice == "My Events":
            st.header("My Events")
            st.table(db.get_events_by_club(st.session_state.club_id))

        elif choice == "Edit/Delete My Events":
            st.header("Manage My Existing Events")
            tab1, tab2 = st.tabs(["Edit Event", "Delete Event"])
            with tab1:
                my_events = db.get_events_by_club(st.session_state.club_id)
                if my_events.empty:
                    st.info("You haven't created any events yet.")
                else:
                    event_options = {f"{row['EVENT_NAME']} (ID: {row['EVENT_ID']})": row for _, row in my_events.iterrows()}
                    selected_event_label = st.selectbox("Select Event to Edit", options=list(event_options.keys()))
                    e = event_options[selected_event_label]
                    
                    with st.form("edit_event_form"):
                        st.info(f"Editing: {e['EVENT_NAME']} (ID: {e['EVENT_ID']})")
                        
                        # Fetch venues for dropdown
                        venues_df = db.get_all_venues()
                        venue_options = {f"{row['VENUE_NAME']} ({row['LOCATION']})": row['VENUE_ID'] for _, row in venues_df.iterrows()}
                        
                        # Find current venue index
                        v_keys = list(venue_options.keys())
                        current_v_id = e['VENUE_ID']
                        v_idx = 0
                        for i, k in enumerate(v_keys):
                            if venue_options[k] == current_v_id:
                                v_idx = i
                                break
                        
                        v_label = st.selectbox("Venue", options=v_keys, index=v_idx)
                        venue_id = venue_options[v_label]
                        
                        name = st.text_input("Event Name", value=e['EVENT_NAME'])
                        
                        categories = ["TECHNICAL", "CULTURAL", "SPORTS", "LITERARY", "WORKSHOP", "SEMINAR", "COMPETITION"]
                        cat_idx = categories.index(e['EVENT_CATEGORY']) if e['EVENT_CATEGORY'] in categories else 0
                        category = st.selectbox("Event Category", categories, index=cat_idx)
                        
                        date = st.date_input("Event Date", value=e['EVENT_DATE'])
                        # Convert TIMESTAMP/DATETIME to python time object for st.time_input
                        curr_start = e['START_TIME'].time() if hasattr(e['START_TIME'], 'time') else datetime.time(9, 0)
                        curr_end = e['END_TIME'].time() if hasattr(e['END_TIME'], 'time') else datetime.time(17, 0)
                        
                        start = st.time_input("Start Time", value=curr_start)
                        end = st.time_input("End Time", value=curr_end)
                        desc = st.text_area("Description", value=e['DESCRIPTION'] if e['DESCRIPTION'] else "")
                        
                        statuses = ["UPCOMING", "COMPLETED", "CANCELLED"]
                        stat_idx = statuses.index(e['EVENT_STATUS']) if e['EVENT_STATUS'] in statuses else 0
                        status = st.selectbox("Event Status", statuses, index=stat_idx)
                        
                        deadline = st.date_input("Registration Deadline", value=e['REGISTRATION_DEADLINE'] if e['REGISTRATION_DEADLINE'] else e['EVENT_DATE'])
                        max_p = st.number_input("Max Participants", min_value=1, value=int(e['MAX_PARTICIPANTS']), step=1)
                        
                        if st.form_submit_button("Update Event"):
                            full_start = datetime.datetime.combine(date, start)
                            full_end = datetime.datetime.combine(date, end)
                            result = db.update_event(e['EVENT_ID'], st.session_state.club_id, venue_id, name, category, date, full_start, full_end, desc, status, deadline, max_p)
                            if result > 0:
                                st.success("Event Updated Successfully!")
                                st.rerun()
                            elif result == 0:
                                st.error("No changes made or event not found.")
                            else:
                                st.error("Failed to update event due to a database error.")
            with tab2:
                with st.form("delete_event_form"):
                    event_id_del = st.number_input("Event ID to Delete", min_value=1, step=1)
                    if st.form_submit_button("Delete"):
                        if db.delete_event(event_id_del, st.session_state.club_id) > 0:
                            st.success("Event Deleted Successfully!")


    # ---------------- STUDENT PANEL ----------------
    elif role == "STUDENT":
        if choice == "Student Dashboard":
            st.header("Student Dashboard")
            st.write("Welcome! This is your hub for engaging with college clubs.")
            profile = db.get_student_by_id(st.session_state.student_id)
            if not profile.empty:
                st.subheader(f"Hello, {profile['STUDENT_NAME'].iloc[0]}")
                st.write(f"**Department:** {profile['DEPARTMENT'].iloc[0]}")

        elif choice == "Browse Events":
            st.header("Browse Upcoming Events")
            events = db.get_upcoming_events()
            
            if not events.empty:
                # Basic search/filtering functionality
                search_term = st.text_input("Search events by Name, Category, or Club...")
                if search_term:
                    mask = (events['EVENT_NAME'].str.contains(search_term, case=False, na=False)) | \
                           (events['EVENT_CATEGORY'].str.contains(search_term, case=False, na=False)) | \
                           (events['CLUB_NAME'].str.contains(search_term, case=False, na=False))
                    filtered_events = events[mask]
                else:
                    filtered_events = events
                st.table(filtered_events)
            else:
                st.info("No upcoming events exactly now.")

        elif choice == "Register for Event":
            st.header("Register")
            with st.form("reg_form"):
                e_id = st.number_input("Event ID", min_value=1, step=1)
                if st.form_submit_button("Register"):
                    status = db.check_if_registered(st.session_state.student_id, e_id)
                    if status == "REGISTERED":
                        st.error("You are already registered for this event!")
                    else:
                        details = db.get_event_details(e_id)
                        if details.empty:
                            st.error("Invalid Event ID.")
                        elif details["EVENT_STATUS"].iloc[0] != "UPCOMING":
                            st.error("Cannot register for an event that is not 'UPCOMING'.")
                        else:
                            if db.register_for_event(st.session_state.student_id, e_id) > 0:
                                st.success("Registered Successfully!")

        elif choice == "My Registrations":
            st.header("My Registrations")
            regs = db.get_student_registrations(st.session_state.student_id)
            st.table(regs)
            
            st.subheader("Cancel Registration")
            with st.form("cancel_reg_form"):
                e_id_cancel = st.number_input("Event ID to Cancel", min_value=1, step=1)
                if st.form_submit_button("Cancel my spot"):
                    if db.cancel_registration(st.session_state.student_id, e_id_cancel) > 0:
                        st.success("Registration Cancelled.")

        elif choice == "Submit Feedback":
            st.header("Submit Event Feedback")
            st.info("Feedback can only be provided for COMPLETED events you registered for.")
            with st.form("feedback_form"):
                e_id_fb = st.number_input("Event ID", min_value=1, step=1)
                rating = st.slider("Rating (1-5)", 1, 5, 5)
                comments = st.text_area("Additional Comments")
                if st.form_submit_button("Submit"):
                    # Light validation
                    event_info = db.get_event_details(e_id_fb)
                    if event_info.empty or event_info['EVENT_STATUS'].iloc[0] != 'COMPLETED':
                        st.error("Event is not completed or does not exist.")
                    else:
                        reg_stat = db.check_if_registered(st.session_state.student_id, e_id_fb)
                        if not reg_stat:
                            st.error("You didn't register for this event.")
                        else:
                            if db.submit_feedback(st.session_state.student_id, e_id_fb, rating, comments) > 0:
                                st.success("Feedback submitted!")
