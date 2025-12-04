import streamlit as st
from datetime import datetime, timedelta

# --- Configuration ---
st.set_page_config(
    page_title="School Task Manager",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Session State Initialization ---
if 'tasks' not in st.session_state:
    st.session_state.tasks = []
    # Add a couple of initial mock tasks
    st.session_state.tasks.append({
        'id': 1,
        'subject': 'Physics',
        'teacher': 'Mr. Smith',
        'description': 'Solve problem set 3 on thermodynamics.',
        'dueDate': datetime.now().date() + timedelta(days=5),
        'isCompleted': False
    })
    st.session_state.tasks.append({
        'id': 2,
        'subject': 'English',
        'teacher': 'Ms. Jane',
        'description': 'Read "The Great Gatsby" chapters 1-3.',
        'dueDate': datetime.now().date() + timedelta(days=2),
        'isCompleted': True
    })

# --- Helper Functions ---

def get_day_of_week(date_obj):
    """Returns the long weekday name for a date object."""
    if date_obj:
        return date_obj.strftime("%A")
    return ""

def sort_tasks(tasks):
    """Sorts tasks: Incomplete first, then by earliest due date."""
    return sorted(tasks, key=lambda x: (x['isCompleted'], x['dueDate']))

def add_task(subject, teacher, due_date_str, description):
    """Adds a new task to the session state."""
    try:
        # Convert YYYY-MM-DD string to Python date object
        due_date_obj = datetime.strptime(due_date_str, '%Y-%m-%d').date()
    except ValueError:
        st.error("Invalid date format.")
        return

    # Generate a unique ID (simple timestamp-based for this demo)
    new_id = int(datetime.now().timestamp() * 1000)

    st.session_state.tasks.append({
        'id': new_id,
        'subject': subject,
        'teacher': teacher,
        'description': description,
        'dueDate': due_date_obj,
        'isCompleted': False
    })
    st.success("Task added successfully!")

def toggle_completion(task_id):
    """Toggles the completion status of a task."""
    for task in st.session_state.tasks:
        if task['id'] == task_id:
            task['isCompleted'] = not task['isCompleted']
            st.rerun() # Rerun to update the display immediately

def delete_task(task_id):
    """Deletes a task by ID."""
    st.session_state.tasks = [task for task in st.session_state.tasks if task['id'] != task_id]
    st.rerun() # Rerun to update the display immediately

# --- UI Components ---

st.markdown("""
    <style>
        .stButton>button {
            width: 100%;
            background-color: #4f46e5;
            color: white;
            font-weight: bold;
            border-radius: 0.5rem;
        }
        .stButton>button:hover {
            background-color: #4338ca;
        }
        /* Custom styling for the task list container */
        .task-card-incomplete {
            border-left: 5px solid #4f46e5;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
            background-color: #ffffff;
        }
        .task-card-complete {
            border-left: 5px solid #10b981;
            opacity: 0.6;
            background-color: #f3f4f6;
        }
    </style>
""", unsafe_allow_html=True)


# --- Header ---
st.markdown(
    """
    <div style="text-align: center; padding: 20px; background-color: white; border-radius: 1rem; margin-bottom: 20px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);">
        <h1 style="font-size: 2.5rem; font-weight: 800; color: #1f2937;">📚 School Task Manager</h1>
        <p style="color: #6b7280; font-size: 0.875rem;">Data stored temporarily in the session.</p>
    </div>
    """, unsafe_allow_html=True
)

# --- Add New Assignment Form ---
st.header("Add New Assignment")
with st.container(border=True):
    with st.form(key='task_form', clear_on_submit=True):
        
        # Row 1: Subject, Teacher
        col1, col2 = st.columns(2)
        subject = col1.text_input("Subject (e.g., Math, History)", key='subject', required=True)
        teacher = col2.text_input("Teacher's Name", key='teacher', required=True)

        # Row 2: Due Date, Day of Week (Display only)
        col3, col4 = st.columns(2)
        
        # Due Date input and helper logic to display day of week
        due_date = col3.date_input("Due Date", key='due_date', min_value=datetime.now().date(), value=datetime.now().date() + timedelta(days=1))
        
        # Display calculated Day of Week (Readonly simulation)
        day_of_week = get_day_of_week(due_date)
        col4.text_input("Day (Auto-calculated)", value=day_of_week, disabled=True, key='due_day')

        # Row 3: Description
        description = st.text_area("Task Description", key='description', height=100, required=True)

        # Submit button
        submit_button = st.form_submit_button(
            label='Add Task', 
            use_container_width=True,
        )

        if submit_button:
            if subject and teacher and due_date and description:
                # Need to convert date object back to string for consistency
                add_task(subject, teacher, due_date.strftime('%Y-%m-%d'), description)
            else:
                st.error("Please fill in all required fields.")

# --- Assignments Due List ---
st.header("Assignments Due")
sorted_tasks = sort_tasks(st.session_state.tasks)

if not sorted_tasks:
    st.info("No assignments yet! Add a new task above.")
else:
    for task in sorted_tasks:
        card_class = "task-card-complete" if task['isCompleted'] else "task-card-incomplete"
        
        # Calculate date strings
        due_day = get_day_of_week(task['dueDate'])
        formatted_date = task['dueDate'].strftime("%b %d, %Y")
        
        # Conditional text styling
        subject_style = 'text-gray-400 text-decoration: line-through;' if task['isCompleted'] else 'font-weight: bold; font-size: 1.125rem;'
        desc_style = 'color: #9ca3af; text-decoration: line-through;' if task['isCompleted'] else 'color: #4b5563;'
        date_badge_bg = '#10b981' if task['isCompleted'] else '#4f46e5'

        # Use a Streamlit expander or just a container for the card layout
        with st.container(border=True):
            st.markdown(f'<div class="{card_class}" style="padding: 1rem; border-radius: 0.75rem;">', unsafe_allow_html=True)
            
            cols = st.columns([0.05, 0.65, 0.20, 0.10])
            
            # 1. Checkbox
            cols[0].checkbox(
                label="", 
                value=task['isCompleted'], 
                key=f"check_{task['id']}", 
                on_change=toggle_completion, 
                args=(task['id'],)
            )

            # 2. Subject, Teacher, Description
            with cols[1]:
                st.markdown(f"""
                    <p style="{subject_style} margin: 0;">{task['subject']} <span style="font-weight: normal; color: #6b7280; font-size: 0.875rem;">/ {task['teacher']}</span></p>
                    <p style="{desc_style} margin-top: 5px; font-size: 0.875rem;">{task['description']}</p>
                """, unsafe_allow_html=True)

            # 3. Due Date Badge
            with cols[2]:
                st.markdown(f"""
                    <div style="background-color: {date_badge_bg}; color: white; padding: 5px 10px; border-radius: 1rem; text-align: center; font-size: 0.75rem; font-weight: 600; box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05); white-space: nowrap;">
                        {due_day}, {formatted_date}
                    </div>
                """, unsafe_allow_html=True)
            
            # 4. Delete Button
            cols[3].button(
                "🗑️",
                key=f"del_{task['id']}",
                on_click=delete_task,
                args=(task['id'],),
                use_container_width=True
            )

            st.markdown('</div>', unsafe_allow_html=True) # Close the task card div
        
        st.markdown("<br>", unsafe_allow_html=True) # Add spacing between cards
