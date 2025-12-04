import streamlit as st
import pandas as pd
from datetime import date, timedelta
import uuid

# --- 1. CONFIGURATION AND INITIAL SETUP ---

# Custom CSS for a modern, 'Inter' font, and Tailwind-like appearance
st.markdown("""
    <style>
        /* Define custom colors and fonts (Mimicking the CSS variables) */
        :root {
            --primary-color: #4f46e5;
            --primary-hover: #4338ca;
            --success-color: #10b981;
            --danger-color: #ef4444;
            --bg-color: #f9fafb;
        }

        /* Use Inter font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@100..900&display=swap');
        html, body, .stApp {
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-color);
        }

        /* Center the main content and apply max-width (mimicking max-w-4xl mx-auto) */
        .stApp > header {
            display: none; /* Hide the default Streamlit header */
        }
        .st-emotion-cache-18ni7ap { /* Class for Streamlit's main content wrapper */
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        .st-emotion-cache-z5xscs { /* Class for the top-level container */
            max-width: 900px !important;
            padding-left: 1rem;
            padding-right: 1rem;
            margin-left: auto;
            margin-right: auto;
        }
        
        /* Custom card styling (mimicking bg-white p-6 rounded-xl shadow-lg) */
        .card-container {
            background-color: white;
            padding: 1.5rem;
            border-radius: 0.75rem;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            margin-bottom: 2rem;
        }

        /* Task Item Styling */
        .task-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0.75rem 1rem;
            margin-bottom: 0.75rem;
            background-color: white;
            border-radius: 0.5rem;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
            transition: all 0.3s ease;
            border: 1px solid #e5e7eb;
        }
        .task-item:hover {
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.06);
        }

        .task-completed {
            background-color: #f3f4f6;
            opacity: 0.7;
        }

        .task-completed .task-title {
            text-decoration: line-through;
            color: #6b7280;
        }
        
        .task-title {
            font-weight: 500;
            color: #1f2937;
        }

        .task-badge {
            display: inline-flex;
            align-items: center;
            padding: 0.125rem 0.625rem;
            margin-top: 0.25rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            line-height: 1;
            font-weight: 500;
            background-color: #e0e7ff; /* indigo-100 */
            color: #4338ca; /* indigo-800 */
        }
    </style>
""", unsafe_allow_html=True)

# Initialize Session State for tasks (Replaces Firestore)
if 'tasks' not in st.session_state:
    st.session_state.tasks = []
    
# Initialize a simple message (Replaces the message box)
if 'message' not in st.session_state:
    st.session_state.message = None

# List of subjects for the dropdown
SUBJECT_OPTIONS = ["General", "Math", "Science", "History", "English", "Project", "Exam Prep"]


# --- 2. FIRESTORE REPLACEMENT (DATA MANAGEMENT FUNCTIONS) ---

def add_task(title, subject, due_date):
    """Adds a new task to the session state."""
    new_task = {
        'id': str(uuid.uuid4()),
        'title': title,
        'subject': subject,
        'due_date': due_date,
        'completed': False
    }
    st.session_state.tasks.append(new_task)
    st.session_state.message = ("Task added successfully!", "success")

def toggle_task(task_id):
    """Toggles the completion status of a task."""
    for task in st.session_state.tasks:
        if task['id'] == task_id:
            task['completed'] = not task['completed']
            # Remove the success message when toggling, as it's a UI action
            st.session_state.message = None 
            break

def delete_task(task_id):
    """Deletes a task from the session state."""
    # Use a list comprehension to filter out the task to be deleted
    st.session_state.tasks = [task for task in st.session_state.tasks if task['id'] != task_id]
    st.session_state.message = ("Task deleted.", "success")


# --- 3. UI RENDERING FUNCTIONS ---

def get_due_date_display(task):
    """Calculates the due date string and style based on completion and date."""
    due_date = pd.to_datetime(task['due_date']).date()
    today = date.today()
    
    if task['completed']:
        return "Completed", "#6b7280" # gray-500
    
    diff_days = (due_date - today).days

    if diff_days == 0:
        return "Due Today", "#dc2626" # red-600
    elif diff_days == 1:
        return "Due Tomorrow", "#f59e0b" # yellow-600
    elif diff_days < 0:
        return "Overdue", "#ef4444" # danger-color (red-500)
    else:
        return f"Due in {diff_days} days", "#4b5563" # gray-600

def render_task_item(task):
    """Renders a single task item using markdown for custom styling."""
    
    # Calculate due date display
    date_display, date_color = get_due_date_display(task)
    
    completed_class = 'task-completed' if task['completed'] else ''
    
    # Create columns for layout: [Toggle] [Title/Subject] [Due Date] [Delete Button]
    col1, col2, col3, col4 = st.columns([0.8, 4, 2.5, 0.8])

    with col1:
        # Checkbox for toggling completion
        st.checkbox(
            label="",
            value=task['completed'],
            key=f"toggle_{task['id']}",
            on_change=toggle_task,
            args=(task['id'],),
            label_visibility="hidden"
        )
        # Note: The custom CSS for the task-item above will handle the visual completion state.

    with col2:
        st.markdown(f"""
            <div class="{completed_class}">
                <p class="task-title">{task['title']}</p>
                <span class="task-badge">{task['subject']}</span>
            </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
            <div style="text-align: right; min-width: 100px; color: {date_color}; font-weight: 600;">
                {date_display}
            </div>
        """, unsafe_allow_html=True)

    with col4:
        # Delete button
        st.button(
            "🗑️",
            key=f"delete_{task['id']}",
            on_click=delete_task,
            args=(task['id'],),
            help="Delete Task"
        )

def render_task_list():
    """Renders the entire task list, sorted and styled."""
    tasks = st.session_state.tasks
    
    # Sort tasks: Incomplete first, then by earliest due date (Replaces Firebase sorting)
    tasks.sort(key=lambda t: (t['completed'], pd.to_datetime(t['due_date'])))

    # Task List Header
    task_count = len(tasks)
    st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <h2 style="font-size: 1.5rem; font-weight: 600; color: #1f2937;">My Tasks</h2>
            <span style="font-size: 1rem; font-weight: 400; color: #6b7280;">{task_count} task{'s' if task_count != 1 else ''}</span>
        </div>
    """, unsafe_allow_html=True)

    # Task List Container (Mimicking the scrollable area)
    if task_count == 0:
        st.markdown("""
            <div style="text-align: center; padding: 2rem; color: #6b7280; font-style: italic;">
                No tasks yet! Add your first assignment above.
            </div>
        """, unsafe_allow_html=True)
    else:
        # Use a container with fixed height and overflow-y for scrollability
        list_container = st.container(height=400, border=False)
        with list_container:
            for task in tasks:
                # Use a custom div to wrap each task for better styling isolation
                st.markdown(f'<div class="task-item {task.get("completed", False) and "task-completed"}">', unsafe_allow_html=True)
                render_task_item(task)
                st.markdown('</div>', unsafe_allow_html=True)
                
# --- 4. MAIN APP STRUCTURE ---

def main():
    """Defines the layout and logic of the Streamlit application."""
    st.set_page_config(page_title="School Task Manager", layout="wide")

    # Header
    st.markdown("""
        <header style="text-align: center; margin-bottom: 2.5rem;">
            <h1 style="font-size: 2.25rem; font-weight: 800; color: #1f2937; margin-bottom: 0.5rem;">School Task Manager</h1>
            <p style="font-size: 1.125rem; color: #6b7280;">Plan your assignments, projects, and exams.</p>
        </header>
    """, unsafe_allow_html=True)

    # --- Task Input Form ---
    with st.container():
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        st.markdown('<h2 style="font-size: 1.5rem; font-weight: 600; color: #1f2937; margin-bottom: 1rem;">Add New Task</h2>', unsafe_allow_html=True)
        
        # Use a form container for better input management
        with st.form(key='task_form', clear_on_submit=True):
            
            col_title, col_subject, col_due = st.columns([2, 1, 1])
            
            with col_title:
                task_title = st.text_input(
                    label="Task Title",
                    placeholder="e.g., Math Homework Chapter 5",
                    label_visibility="visible"
                )
            
            with col_subject:
                task_subject = st.selectbox(
                    label="Subject/Category",
                    options=SUBJECT_OPTIONS,
                    index=0 # General
                )
            
            with col_due:
                task_due_date = st.date_input(
                    label="Due Date",
                    value=date.today() + timedelta(days=1), # Default to tomorrow
                    min_value=date.today()
                )

            # Submit button
            submitted = st.form_submit_button(
                label='Add Task',
                use_container_width=True
            )

            # Form submission logic
            if submitted:
                if task_title and task_due_date:
                    add_task(task_title, task_subject, task_due_date.isoformat())
                    # The Streamlit app will automatically RERUN and show the updated list
                else:
                    st.error('Please fill in the Task Title and Due Date.')
        
        st.markdown('</div>', unsafe_allow_html=True)

    # --- Task List ---
    with st.container():
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        render_task_list()
        st.markdown('</div>', unsafe_allow_html=True)

    # --- Status Message Box (Replaces the fixed bottom-right box) ---
    if st.session_state.message:
        message, msg_type = st.session_state.message
        if msg_type == 'success':
            st.toast(message, icon="✅")
        elif msg_type == 'error':
            st.toast(message, icon="❌")
        
        # Clear the message after showing it once
        st.session_state.message = None

if __name__ == '__main__':
    main()
