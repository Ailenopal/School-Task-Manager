import streamlit as st
from datetime import datetime, timedelta

# --- Configuration ---
# Setting the page configuration must be done at the top level before any st element
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
        'isCompleted': False,
        'customDayLabel': 'Next Fri' # Added custom label for consistency
    })
    st.session_state.tasks.append({
        'id': 2,
        'subject': 'English',
        'teacher': 'Ms. Jane',
        'description': 'Read "The Great Gatsby" chapters 1-3.',
        'dueDate': datetime.now().date() + timedelta(days=2),
        'isCompleted': True,
        'customDayLabel': None # Optional label
    })

# --- Helper Functions (defined globally) ---

def get_day_of_week(date_obj):
    """Returns the long weekday name for a date object."""
    if date_obj:
        return date_obj.strftime("%A")
    return ""

def sort_tasks(tasks):
    """Sorts tasks: Incomplete first, then by earliest due date."""
    # Sorting key is a tuple: (completion status, due date)
    return sorted(tasks, key=lambda x: (x['isCompleted'], x['dueDate']))

def add_task(subject, teacher, due_date_str, description, day_label):
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
        'isCompleted': False,
        'customDayLabel': day_label if day_label else None # Store the custom label
    })
    st.success("Task added successfully!")
    st.rerun() # Trigger rerun to clear the form and update the list

def toggle_completion(task_id):
    """Toggles the completion status of a task and reruns the app."""
    for task in st.session_state.tasks:
        if task['id'] == task_id:
            task['isCompleted'] = not task['isCompleted']
            break
    # Rerun to update the display immediately and re-sort
    st.rerun() 

def delete_task(task_id):
    """Deletes a task by ID and reruns the app."""
    st.session_state.tasks = [task for task in st.session_state.tasks if task['id'] != task_id]
    st.rerun() 

# --- Main Application Function ---
def main():
    # --- Custom CSS Styling (Dark Mode) ---
    st.markdown("""
        <style>
            /* Set a dark background color for the entire page */
            body {
                background-color: #1f2937; /* Slate 800 */
            }
            /* Ensure the main Streamlit container also adopts the dark background */
            .stApp {
                background-color: #1f2937;
            }
            
            .stButton>button {
                width: 100%;
                background-color: #6366f1; /* Indigo 500 */
                color: white;
                font-weight: bold;
                border-radius: 0.5rem;
            }
            .stButton>button:hover {
                background-color: #4f46e5; /* Indigo 600 */
            }
            /* Custom styling for the task list container (Incomplete: Slate 700, Complete: Slate 600) */
            .task-card-incomplete {
                border-left: 5px solid #6366f1; /* Lighter Purple Border */
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -2px rgba(0, 0, 0, 0.2);
                background-color: #374151; /* Slate 700 */
            }
            .task-card-complete {
                border-left: 5px solid #34d399; /* Lighter Green Border */
                opacity: 0.7;
                background-color: #4b5563; /* Slate 600 */
            }
            
            /* Change input field colors for better dark mode visibility */
            /* Streamlit handles some internal component colors, but setting text explicitly here */
            .stTextInput>div>div>input, .stTextArea>div>div>textarea {
                color: #f3f4f6; /* Very light gray text */
                background-color: #4b5563; /* Slate 600 background */
            }
        </style>
    """, unsafe_allow_html=True)


    # --- Header (Updated for Dark Mode) ---
    st.markdown(
        """
        <div style="text-align: center; padding: 20px; background-color: #374151; border-radius: 1rem; margin-bottom: 20px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);">
            <h1 style="font-size: 2.5rem; font-weight: 800; color: #f9fafb;">📚 School Task Manager</h1>
            <p style="color: #9ca3af; font-size: 0.875rem;">Tasks are saved for the current browser session only.</p>
        </div>
        """, unsafe_allow_html=True
    )

    # --- Add New Assignment Form ---
    # Streamlit headers use the default theme color, but we ensure the input area container is styled correctly
    st.header("Add New Assignment")
    with st.container(border=True):
        # We use a form with clear_on_submit=True to reset inputs after successful submission
        with st.form(key='task_form', clear_on_submit=True):
            
            # Row 1: Subject, Teacher
            col1, col2 = st.columns(2)
            subject = col1.text_input("Subject (e.g., Math, History)", key='subject_input')
            teacher = col2.text_input("Teacher's Name", key='teacher_input')

            # Row 2: Due Date, Day of Week (Editable custom label)
            col3, col4 = st.columns(2)
            
            # Due Date input
            default_date = datetime.now().date() + timedelta(days=1)
            due_date = col3.date_input(
                "Due Date", 
                key='due_date_input', 
                min_value=datetime.now().date(), 
                value=default_date
            )
            
            # Allow user to choose/input a custom day label, defaulting to the calculated day name
            calculated_day = get_day_of_week(due_date)
            # Changed label and removed disabled=True to allow user input
            day_label = col4.text_input("Day Label (e.g., 'Today', 'EOD', 'Weekend')", value=calculated_day, key='day_label_input')

            # Row 3: Description
            description = st.text_area("Task Description", key='description_input', height=100)

            # Submit button
            submit_button = st.form_submit_button(
                label='Add Task', 
                use_container_width=True,
            )

            if submit_button:
                # Streamlit forms capture all inputs at once on submit
                if subject and teacher and due_date and description:
                    # Pass the new day_label to the add_task function
                    add_task(subject, teacher, due_date.strftime('%Y-%m-%d'), description, day_label)
                else:
                    st.error("Please fill in all required fields.")


    # --- Assignments Due List ---
    st.header("Assignments Due")
    sorted_tasks = sort_tasks(st.session_state.tasks)

    if not sorted_tasks:
        st.info("No assignments yet! Add a new task above.")
    else:
        # Loop through sorted tasks and render cards
        for task in sorted_tasks:
            card_class = "task-card-complete" if task['isCompleted'] else "task-card-incomplete"
            
            # Calculate date components
            due_day = get_day_of_week(task['dueDate'])
            formatted_date = task['dueDate'].strftime("%b %d, %Y")
            
            # Use custom label if available, otherwise use calculated day
            custom_label = task.get('customDayLabel')
            display_text = f"{custom_label}, {formatted_date}" if custom_label else f"{due_day}, {formatted_date}"
            
            # Conditional text styling using inline HTML/CSS (Updated for Dark Mode)
            
            # Incomplete: White main text, Light gray secondary text
            # Complete: Medium light gray text (faded)
            subject_style = 'color: #9ca3af; text-decoration: line-through;' if task['isCompleted'] else 'font-weight: bold; color: #f9fafb; font-size: 1.125rem;'
            desc_style = 'color: #9ca3af; text-decoration: line-through;' if task['isCompleted'] else 'color: #d1d5db;'
            teacher_color = '#9ca3af' if task['isCompleted'] else '#a0aec0' # Light gray for teacher name

            # Badge color remains the same (Indigo/Green)
            date_badge_bg = '#34d399' if task['isCompleted'] else '#6366f1'

            # Use st.container to create the card layout
            with st.container(border=True):
                # Apply custom CSS class for visual styling
                st.markdown(f'<div class="{card_class}" style="padding: 1rem; border-radius: 0.75rem; margin-bottom: 0px;">', unsafe_allow_html=True)
                
                cols = st.columns([0.05, 0.65, 0.20, 0.10])
                
                # 1. Checkbox
                cols[0].checkbox(
                    label="", 
                    value=task['isCompleted'], 
                    # Ensure a stable, unique key for the checkbox
                    key=f"check_{task['id']}", 
                    on_change=toggle_completion, 
                    args=(task['id'],) # Pass the task ID to the callback
                )

                # 2. Subject, Teacher, Description (Using updated styles)
                with cols[1]:
                    st.markdown(f"""
                        <p style="{subject_style} margin: 0;">{task['subject']} <span style="font-weight: normal; color: {teacher_color}; font-size: 0.875rem;">/ {task['teacher']}</span></p>
                        <p style="{desc_style} margin-top: 5px; font-size: 0.875rem;">{task['description']}</p>
                    """, unsafe_allow_html=True)

                # 3. Due Date Badge
                with cols[2]:
                    st.markdown(f"""
                        <div style="background-color: {date_badge_bg}; color: white; padding: 5px 10px; border-radius: 1rem; text-align: center; font-size: 0.75rem; font-weight: 600; box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.15); white-space: nowrap;">
                            {display_text}
                        </div>
                    """, unsafe_allow_html=True)
                
                # 4. Delete Button
                cols[3].button(
                    "🗑️",
                    # Ensure a stable, unique key for the button
                    key=f"del_{task['id']}",
                    on_click=delete_task,
                    args=(task['id'],),
                    use_container_width=True
                )

                st.markdown('</div>', unsafe_allow_html=True) # Close the task card div
            
            st.markdown("<br>", unsafe_allow_html=True) # Add spacing between cards

# --- Execution Entry Point ---
if __name__ == "__main__":
    main()
