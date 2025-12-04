import streamlit as st
import pandas as pd
from datetime import datetime
import uuid

# --- FIRESTORE INTEGRATION NOTES ---
# To switch to real-time Firestore persistence, you would need to:
# 1. Install the library: pip install google-cloud-firestore
# 2. Configure credentials (e.g., set GOOGLE_APPLICATION_CREDENTIALS environment variable).
# 3. Initialize the Firestore client (db = firestore.Client()).
# 4. Replace all references to st.session_state.tasks with the appropriate Firestore CRUD operations
#    (get, set, update, delete).
# 5. For real-time updates in Streamlit, you would typically poll the database at intervals or use
#    an external service to push updates, as Streamlit is request/response based.
# ------------------------------------


# --- Configuration and Initialization ---

# Use the Inter font style (Streamlit uses Markdown/CSS which can be customized)
st.set_page_config(
    page_title="Streamlit School Task Manager", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for styling (Glassmorphism effect is hard to replicate exactly in Streamlit's model,
# but we can use background and rounded containers for a clean look.)
st.markdown("""
<style>
    /* Gradient Background */
    .stApp {
        background: linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%);
        background-attachment: fixed;
        color: #1e3a8a; /* Indigo 900 */
        font-family: 'Inter', sans-serif;
    }
    
    /* Main Content Container Styling */
    .main-content-container {
        padding: 2.5rem;
        border-radius: 1.5rem;
        background-color: rgba(255, 255, 255, 0.4); /* Light semi-transparent */
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        border: 1px solid rgba(255, 255, 255, 0.4);
        margin-top: 2rem;
    }
    
    /* Task Item Styling */
    .task-item-container {
        padding: 1rem;
        margin-bottom: 0.75rem;
        border-radius: 0.75rem;
        background-color: rgba(255, 255, 255, 0.7);
        border-left: 5px solid transparent;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    /* Completed Task Styling */
    .completed-task-style {
        opacity: 0.6;
        text-decoration: line-through;
        border-left: 5px solid #6ee7b7;
    }
    
    /* Custom button styling for Add Task */
    .stButton>button {
        background-color: #4f46e5; /* Indigo 600 */
        color: white;
        font-weight: bold;
        padding: 0.75rem 1rem;
        border-radius: 0.5rem;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        background-color: #4338ca; /* Indigo 700 */
        transform: scale(1.01);
    }
    
    /* Remove default input styles */
    .stTextInput>div>div>input {
        border-radius: 0.5rem;
        background-color: rgba(255, 255, 255, 0.8);
        border: none !important; 
    }
    
    /* Title and Header */
    h1 {
        color: #1e3a8a !important;
        font-weight: 800;
        letter-spacing: -0.05em;
        text-shadow: 1px 1px 2px rgba(255, 255, 255, 0.5);
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state for tasks if it doesn't exist
if 'tasks' not in st.session_state:
    st.session_state.tasks = []
    # Add some mock tasks for a fresh start
    st.session_state.tasks.append({
        'id': str(uuid.uuid4()),
        'title': 'Final History Paper Outline',
        'dueDate': datetime.now().date().isoformat(),
        'subject': 'World History',
        'teacher': 'Mr. Smith',
        'completed': False,
        'createdAt': datetime.now()
    })
    st.session_state.tasks.append({
        'id': str(uuid.uuid4()),
        'title': 'Read Chapter 5 - Optics',
        'dueDate': (datetime.now().date() + pd.Timedelta(days=3)).isoformat(),
        'subject': 'Physics',
        'teacher': 'Ms. Jones',
        'completed': False,
        'createdAt': datetime.now()
    })
    st.session_state.tasks.append({
        'id': str(uuid.uuid4()),
        'title': 'Completed Calculus Problem Set',
        'dueDate': (datetime.now().date() - pd.Timedelta(days=1)).isoformat(),
        'subject': 'Calculus',
        'teacher': 'Dr. Evans',
        'completed': True,
        'createdAt': datetime.now()
    })


# --- Helper Functions (CRUD Operations on Session State) ---

def add_task(subject, title, teacher, due_date):
    """Adds a new task to the session state."""
    new_task = {
        'id': str(uuid.uuid4()),
        'title': title,
        'dueDate': due_date.isoformat(),
        'subject': subject,
        'teacher': teacher if teacher else 'N/A',
        'completed': False,
        'createdAt': datetime.now()
    }
    st.session_state.tasks.append(new_task)
    # Rerun to clear form inputs and refresh the list
    st.rerun()

def toggle_completion(task_id):
    """Toggles the completion status of a task."""
    for task in st.session_state.tasks:
        if task['id'] == task_id:
            task['completed'] = not task['completed']
            break

def delete_task(task_id):
    """Deletes a task from the session state."""
    st.session_state.tasks = [task for task in st.session_state.tasks if task['id'] != task_id]

def update_field(task_id, field, new_value):
    """Updates a specific field of a task."""
    for task in st.session_state.tasks:
        if task['id'] == task_id:
            task[field] = new_value
            break


# --- Application UI Functions ---

def render_task_form():
    """Renders the input form for new tasks."""
    st.subheader("Add New Assignment", anchor=False)
    
    # Use st.form for grouping inputs and preventing unwanted reruns
    with st.form(key='task_form', clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            task_subject = st.text_input("Subject", placeholder="e.g., Chemistry", key='form_subject', required=True)
        with col2:
            task_teacher = st.text_input("Teacher (Optional)", placeholder="e.g., Ms. Jones", key='form_teacher')
            
        col3, col4 = st.columns(2)
        with col3:
            task_title = st.text_input("Assignment Title", placeholder="e.g., Essay Draft", key='form_title', required=True)
        with col4:
            task_due_date = st.date_input("Due Date", value=datetime.now().date(), key='form_date')
            
        # The form submit button
        submit_button = st.form_submit_button(
            label='➕ Add Task',
            type="primary"
        )

    # Handle submission outside the form structure
    if submit_button:
        # Streamlit forms already handle required fields, but we add a final check
        if task_subject and task_title and task_due_date:
            add_task(task_subject, task_title, task_teacher, task_due_date)
        else:
            st.error("Subject, Title, and Due Date are required.")

def render_task_list():
    """Renders the sorted list of tasks."""
    
    st.subheader("Upcoming Tasks", anchor=False)
    
    tasks = sorted(st.session_state.tasks, key=task_sort_key)

    if not tasks:
        st.info("🎉 You have no tasks yet! Add your first assignment above.")
        return

    # Use a container to visually separate the list
    list_container = st.container()

    for task in tasks:
        # Determine styling based on completion status
        task_style = "completed-task-style" if task['completed'] else ""
        
        # Use an Expander for task details, giving an 'editable field' feel via st.text_input/st.checkbox
        with list_container.container():
            
            # --- Main Task Item Row ---
            col_check, col_details, col_delete = st.columns([1, 10, 1])
            
            # 1. Checkbox (Toggle completion)
            col_check.checkbox(
                label="", 
                value=task['completed'], 
                key=f"check_{task['id']}", 
                on_change=toggle_completion, 
                args=(task['id'],),
                label_visibility="collapsed"
            )

            # 2. Task Details Display
            with col_details:
                
                # --- Editable Fields ---
                # Subject (using a placeholder to simulate the editable field)
                new_subject = st.text_input(
                    label="Subject",
                    value=task.get('subject', 'N/A'),
                    key=f"subject_{task['id']}",
                    label_visibility="collapsed",
                    disabled=task['completed']
                )
                if new_subject != task.get('subject', 'N/A'):
                    update_field(task['id'], 'subject', new_subject)

                # Title
                new_title = st.text_input(
                    label="Title",
                    value=task['title'],
                    key=f"title_{task['id']}",
                    label_visibility="collapsed",
                    disabled=task['completed']
                )
                if new_title != task['title']:
                    update_field(task['id'], 'title', new_title)
                    
                # Teacher
                new_teacher = st.text_input(
                    label="Teacher",
                    value=task.get('teacher', 'N/A'),
                    key=f"teacher_{task['id']}",
                    label_visibility="collapsed",
                    disabled=task['completed']
                )
                if new_teacher != task.get('teacher', 'N/A'):
                    update_field(task['id'], 'teacher', new_teacher)

                # Due Date (Read-only display)
                st.markdown(
                    f'<p style="font-size: 0.8rem; color: #4338ca; margin-top: -0.5rem;">Due: {datetime.strptime(task["dueDate"], "%Y-%m-%d").strftime("%b %d, %Y")}</p>', 
                    unsafe_allow_html=True
                )
                
            # 3. Delete Button
            col_delete.button(
                "🗑️", 
                key=f"delete_{task['id']}", 
                on_click=delete_task, 
                args=(task['id'],),
                type="secondary"
            )
            
            # Apply styling using Markdown for the custom container
            st.markdown(
                f'<div class="task-item-container {task_style}"></div>', 
                unsafe_allow_html=True
            )


def task_sort_key(task):
    """Key function for sorting tasks: Incomplete first, then by Due Date (earliest first)."""
    completion_value = 1 if task['completed'] else 0
    
    # Try to parse the date for sorting
    try:
        date_value = datetime.strptime(task['dueDate'], "%Y-%m-%d")
    except ValueError:
        # Put tasks with invalid dates at the very end
        date_value = datetime(2099, 12, 31) 
        
    return (completion_value, date_value)


# --- Main Application Layout ---

def main():
    """The main function that draws the Streamlit app."""
    
    # Wrap the entire content in the custom styled container
    st.markdown('<div class="main-content-container">', unsafe_allow_html=True)
    
    st.title("School Task Manager")
    st.markdown('<p style="color: #4338ca; margin-bottom: 1.5rem; border-bottom: 1px solid #c7d2fe; padding-bottom: 1rem;">Manage your assignments and deadlines in real-time (Simulated persistence).</p>', unsafe_allow_html=True)
    
    # Simulated User/Auth Status (for context alignment with the original app)
    user_id = "simulated-user-" + (str(hash(st.session_state.tasks)) % 1000) # Simple mock ID
    
    st.markdown(
        f"""
        <div style="padding: 0.75rem; background-color: rgba(255, 255, 255, 0.5); border-radius: 0.5rem; box-shadow: inset 0 1px 3px 0 rgba(0, 0, 0, 0.1);">
            <span style="font-weight: 600; color: #3730a3;">Status: Ready (Session State)</span>
            <span style="float: right; font-size: 0.75rem; color: #4338ca; overflow: hidden; max-width: 50%; text-overflow: ellipsis; white-space: nowrap;">
                User ID: {user_id}
            </span>
        </div>
        """, unsafe_allow_html=True
    )
    
    st.divider()

    # Render Input Form
    render_task_form()
    
    st.divider()

    # Render Task List
    render_task_list()
    
    st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
