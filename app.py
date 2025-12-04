import streamlit as st
from google.cloud import firestore
from google.oauth2 import service_account
import json
from datetime import datetime, timedelta, date

# --- 1. CONFIGURATION AND FIREBASE INITIALIZATION ---

# NOTE: For this to run, you MUST set up Firebase Admin SDK credentials.
# Replace the placeholder below with the content of your Firebase Admin SDK
# Service Account JSON file.
# The 'st.secrets' method is the recommended way for Streamlit Cloud.

# Try to load credentials from Streamlit secrets (recommended for deployment)
try:
    key_dict = st.secrets["firebase_credentials"]
except:
    # Fallback/Local testing: If you are running locally, you must provide
    # your service account file content here (as a dictionary or JSON string).
    # NEVER commit this to a public repository.
    st.error("🚨 Firebase credentials not found in st.secrets. Please configure `secrets.toml`.")
    # Use a dummy structure to prevent the app from crashing immediately
    key_dict = {}

try:
    if key_dict:
        creds = service_account.Credentials.from_service_account_info(key_dict)
        db = firestore.Client(credentials=creds, project=creds.project_id)
        # Dummy User ID since Streamlit is usually single-user or uses server-side auth
        # Adjust 'app_id' as per your original structure if necessary
        USER_ID = "streamlit_user_1"
        APP_ID = "default-app-id"
        TASK_COLLECTION_PATH = f"artifacts/{APP_ID}/users/{USER_ID}/tasks"
        
        # Initialize session state for task list and loading status
        if 'tasks' not in st.session_state:
            st.session_state.tasks = []
        if 'loading' not in st.session_state:
            st.session_state.loading = True
    else:
        db = None
        TASK_COLLECTION_PATH = None
        st.session_state.tasks = []

except Exception as e:
    st.error(f"Failed to initialize Firebase: {e}")
    db = None
    TASK_COLLECTION_PATH = None
    st.session_state.tasks = []


# --- 2. UTILITY FUNCTIONS ---

def get_relative_date(due_date: date) -> str:
    """Calculates relative date status (Today, Tomorrow, Overdue, etc.)."""
    today = date.today()
    diff = (due_date - today).days

    if diff < 0:
        return 'Overdue'
    elif diff == 0:
        return 'Today'
    elif diff == 1:
        return 'Tomorrow'
    elif diff <= 7:
        return f'{diff} days away'
    else:
        return 'Later'

def format_due_date(due_date: date) -> str:
    """Formats the date for display."""
    return due_date.strftime('%a, %b %d')

def load_tasks_from_firestore():
    """Fetches all tasks from Firestore and stores them in session state."""
    if not db:
        st.session_state.loading = False
        return

    try:
        tasks_ref = db.collection(TASK_COLLECTION_PATH)
        docs = tasks_ref.stream()
        
        tasks_list = []
        for doc in docs:
            task = doc.to_dict()
            # Convert Firestore timestamp to datetime.date object
            if 'dueDate' in task and isinstance(task['dueDate'], str):
                task['dueDate'] = datetime.strptime(task['dueDate'], '%Y-%m-%d').date()
            if 'createdAt' in task and hasattr(task['createdAt'], 'to_datetime'):
                task['createdAt'] = task['createdAt'].to_datetime()
                
            tasks_list.append({'id': doc.id, **task})

        # Sort tasks: incomplete first, then by due date
        tasks_list.sort(key=lambda t: (t['completed'], t['dueDate']))
        st.session_state.tasks = tasks_list
        st.session_state.loading = False
    except Exception as e:
        st.error(f"Error loading tasks: {e}")
        st.session_state.loading = False

# Ensure tasks are loaded on the first run
if st.session_state.loading:
    load_tasks_from_firestore()

# --- 3. CRUD OPERATIONS (Firestore) ---

def add_task(name, due_date, type, subject, teacher):
    """Adds a new task to Firestore."""
    if not db: return

    try:
        tasks_ref = db.collection(TASK_COLLECTION_PATH)
        tasks_ref.add({
            'name': name,
            'dueDate': due_date.isoformat(), # Store as ISO string
            'type': type,
            'subject': subject,
            'teacher': teacher,
            'completed': False,
            'createdAt': firestore.SERVER_TIMESTAMP
        })
        st.toast(f"Task '{name}' added successfully!", icon='✅')
        load_tasks_from_firestore() # Reload tasks to update UI
    except Exception as e:
        st.error(f"Error adding task: {e}")

def toggle_task(task_id, completed_status):
    """Updates the completion status of a task in Firestore."""
    if not db: return
    try:
        doc_ref = db.collection(TASK_COLLECTION_PATH).document(task_id)
        doc_ref.update({'completed': not completed_status})
        st.toast("Task updated!", icon='👍')
        load_tasks_from_firestore() # Reload tasks to update UI
    except Exception as e:
        st.error(f"Error updating task: {e}")

def delete_task(task_id, task_name):
    """Deletes a task from Firestore."""
    if not db: return
    try:
        doc_ref = db.collection(TASK_COLLECTION_PATH).document(task_id)
        doc_ref.delete()
        st.toast(f"Task '{task_name}' deleted!", icon='🗑️')
        load_tasks_from_firestore() # Reload tasks to update UI
    except Exception as e:
        st.error(f"Error deleting task: {e}")

# --- 4. STREAMLIT UI COMPONENTS ---

st.set_page_config(page_title="My Study Planner", layout="wide", initial_sidebar_state="collapsed")

# Header
st.title("📚 My Study Planner")
st.markdown("Manage your school tasks and deadlines.")
st.caption(f"Logged in as: `{USER_ID}` (Simulation)")
st.markdown("---")

# Task Addition Form
with st.container(border=True):
    st.subheader("➕ Add New Task")
    
    # Use st.form for a single-submit button experience
    with st.form(key='task_form'):
        col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])

        with col1:
            task_name = st.text_input("Task Name", placeholder="e.g., Math Homework")
        with col2:
            due_date = st.date_input("Due Date", min_value=date.today(), value=date.today())
        with col3:
            task_type = st.selectbox("Type", ['Homework', 'Project', 'Exam/Test', 'Other'])
        with col4:
            task_subject = st.text_input("Subject", placeholder="e.g., Algebra II")
        with col5:
            task_teacher = st.text_input("Teacher (Optional)", placeholder="e.g., Ms. Smith")
        
        # Submit button
        submit_button = st.form_submit_button(label='Add Task', use_container_width=True, 
                                            disabled=not db, type="primary")

        if submit_button:
            if not task_name or not task_subject:
                st.warning("Please fill in Task Name and Subject.")
            elif db:
                add_task(task_name, due_date, task_type, task_subject, task_teacher)
            else:
                st.error("Cannot add task. Database is not initialized.")


st.markdown("---")

# --- 5. TASK DISPLAY ---

st.header("📋 Task List")

if st.session_state.loading:
    st.info("Loading tasks...")
elif not db:
    st.error("Cannot connect to Firebase. Check your credentials.")
elif not st.session_state.tasks:
    st.info("🎉 No tasks found! Time to add one.")
else:
    # Categorize tasks
    upcoming_tasks = []
    next_week_tasks = []
    later_tasks = []
    
    today = date.today()
    seven_days_away = today + timedelta(days=7)
    
    for task in st.session_state.tasks:
        due_date = task['dueDate']
        
        if due_date <= today + timedelta(days=1): # Today and Tomorrow
            upcoming_tasks.append(task)
        elif due_date <= seven_days_away:
            next_week_tasks.append(task)
        else:
            later_tasks.append(task)
            
    # Function to render a task card
    def render_task_group(title, icon, tasks_list):
        st.subheader(f"{icon} {title}")
        
        if not tasks_list:
            if title.startswith("Upcoming"):
                st.caption("No tasks due today or tomorrow!")
            else:
                st.caption(f"No tasks in the '{title}' category.")
            return

        cols = st.columns(3)
        for i, task in enumerate(tasks_list):
            with cols[i % 3]: # Distribute cards across 3 columns
                is_completed = task.get('completed', False)
                relative_date = get_relative_date(task['dueDate'])
                
                # Determine border and style
                border_style = 'green' if is_completed else ('red' if relative_date in ['Today', 'Tomorrow', 'Overdue'] else 'yellow')
                
                # Use st.expander for a card-like look
                with st.expander(f"**{'✅' if is_completed else ''} {task['name']}**", expanded=False):
                    st.markdown(f"**Due:** {format_due_date(task['dueDate'])} ({relative_date})")
                    st.markdown(f"**Type:** {task['type']}")
                    st.markdown(f"**Subject:** {task['subject']}")
                    if task['teacher']:
                         st.markdown(f"**Teacher:** {task['teacher']}")
                    
                    st.markdown("---")
                    
                    # Action Buttons
                    col_btn_1, col_btn_2 = st.columns(2)
                    
                    with col_btn_1:
                        if is_completed:
                            st.button("Undo", key=f"toggle_{task['id']}", 
                                      on_click=toggle_task, args=(task['id'], is_completed), use_container_width=True)
                        else:
                            st.button("Complete", key=f"toggle_{task['id']}", 
                                      on_click=toggle_task, args=(task['id'], is_completed), use_container_width=True, type="primary")

                    with col_btn_2:
                        # Use a unique key for the delete button
                        st.button("Delete", key=f"delete_{task['id']}", 
                                  on_click=delete_task, args=(task['id'], task['name']), use_container_width=True, type="secondary")

        st.markdown("<br>", unsafe_allow_html=True) # Add spacing between sections

    # Render all groups
    render_task_group("🔥 Upcoming (Today & Tomorrow)", "📅", upcoming_tasks)
    render_task_group("⏳ Next 7 Days", "🗓️", next_week_tasks)
    render_task_group("🌲 Later (Beyond 7 Days)", "🕰️", later_tasks)
