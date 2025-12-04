import streamlit as st
from collections import deque
import time

# --- Configuration ---
GRID_SIZE = 10
CELL_TYPES = {
    'E': 'Empty',       # Default, traversable cell
    'S': 'Start',       # Start node
    'G': 'Goal',        # Goal/End node
    'W': 'Wall',        # Obstacle/Wall (not traversable)
    'V': 'Visited',     # Visited node during search
    'P': 'Path'         # Final shortest path
}

# --- Initialization and State Management ---

def initialize_grid():
    """Creates a 10x10 grid initialized to 'E' (Empty)."""
    grid = [['E' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    st.session_state.grid = grid
    st.session_state.start = None
    st.session_state.goal = None
    st.session_state.current_tool = 'S' # Default tool is 'Start'
    st.session_state.message = "Welcome! Use the controls to set the Start (S) and Goal (G) points."

def get_grid_state():
    """Ensures the grid and state are initialized."""
    if 'grid' not in st.session_state:
        initialize_grid()
    return st.session_state.grid

def reset_simulation():
    """Resets the grid to a fresh state, keeping only walls if present."""
    st.session_state.grid = [['E' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    st.session_state.start = None
    st.session_state.goal = None
    st.session_state.message = "Grid reset. Set the Start and Goal points to begin."

def clear_path():
    """Clears 'Visited' and 'Path' states, keeping S, G, and W."""
    new_grid = get_grid_state()
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            cell = new_grid[r][c]
            if cell in ('V', 'P'):
                new_grid[r][c] = 'E'
    st.session_state.grid = new_grid
    st.session_state.message = "Path cleared. Ready for a new search."

# --- Pathfinding Logic (Breadth-First Search - BFS) ---

def bfs_search(grid, start, goal):
    """
    Performs BFS to find the shortest path.
    Returns: The path (list of coordinates) or None if no path found.
    """
    rows, cols = len(grid), len(grid[0])
    queue = deque([start])
    
    # Store parent coordinates to reconstruct the path: parent[(r, c)] = (parent_r, parent_c)
    parent = {start: None} 
    
    # Directions: (dr, dc) for N, S, E, W
    directions = [(-1, 0), (1, 0), (0, 1), (0, -1)]

    path_found = False

    while queue:
        r, c = queue.popleft()

        # Visualization step: Mark as visited (but skip Start/Goal)
        if (r, c) != start and (r, c) != goal:
            grid[r][c] = 'V'
            # st.session_state.grid = grid # This line is commented out to prevent excessive reruns
            time.sleep(0.02) # Slow down for visualization effect
            st.rerun() # Trigger a rerun to show the visited cell

        if (r, c) == goal:
            path_found = True
            break

        # Explore neighbors
        for dr, dc in directions:
            nr, nc = r + dr, c + dc

            # Check boundaries and if the cell is not a wall and not yet visited (in parent map)
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != 'W' and (nr, nc) not in parent:
                queue.append((nr, nc))
                parent[(nr, nc)] = (r, c)

    if path_found:
        # Reconstruct path
        path = []
        current = goal
        while current:
            path.append(current)
            current = parent[current]
        
        # Mark the path on the grid (excluding Start and Goal)
        for r, c in reversed(path):
            if (r, c) != start and (r, c) != goal:
                grid[r][c] = 'P'
                st.rerun()
                time.sleep(0.05)
        
        st.session_state.message = f"Path found! Shortest distance: {len(path) - 1} steps."
    else:
        st.session_state.message = "No path found between Start and Goal."

    st.session_state.grid = grid
    st.rerun()


# --- UI and Drawing Functions ---

def get_cell_style(cell_type):
    """Returns CSS background color for a cell type."""
    styles = {
        'E': 'bg-white hover:bg-gray-100 cursor-pointer border border-gray-200',
        'S': 'bg-green-500 text-white font-bold border border-green-700',
        'G': 'bg-red-500 text-white font-bold border border-red-700',
        'W': 'bg-gray-800 border border-gray-900',
        'V': 'bg-yellow-200 animate-pulse border border-yellow-400',
        'P': 'bg-blue-400 border border-blue-600',
    }
    return styles.get(cell_type, 'bg-white')

def handle_cell_click(r, c):
    """Handles logic when a user clicks a cell based on the current tool."""
    grid = st.session_state.grid
    tool = st.session_state.current_tool
    
    # Clear any previous path or visited marks before editing
    clear_path()

    if tool == 'S':
        # Remove old start point if one exists
        if st.session_state.start:
            old_r, old_c = st.session_state.start
            grid[old_r][old_c] = 'E'
            
        grid[r][c] = 'S'
        st.session_state.start = (r, c)
        st.session_state.message = f"Start set at ({r}, {c}). Next, set the Goal."
    
    elif tool == 'G':
        # Remove old goal point if one exists
        if st.session_state.goal:
            old_r, old_c = st.session_state.goal
            grid[old_r][old_c] = 'E'
            
        grid[r][c] = 'G'
        st.session_state.goal = (r, c)
        st.session_state.message = f"Goal set at ({r}, {c}). Now place some walls or run the search!"

    elif tool == 'W':
        current_val = grid[r][c]
        if current_val == 'W':
            # Toggle off wall
            grid[r][c] = 'E'
            st.session_state.message = "Wall removed."
        elif current_val in ('S', 'G'):
            st.session_state.message = f"Cannot place a wall on the {CELL_TYPES[current_val]} point."
        else:
            # Toggle on wall
            grid[r][c] = 'W'
            st.session_state.message = "Wall placed."

    st.session_state.grid = grid


def draw_grid():
    """Renders the grid using Streamlit columns and HTML/Tailwind CSS."""
    grid = get_grid_state()
    
    # Use a large container for the whole grid
    grid_html = """
    <div class="grid-container flex flex-col items-center justify-center p-4">
        <div class="grid grid-cols-10 gap-0.5 shadow-xl rounded-lg bg-gray-100 p-2 border-2 border-gray-300">
    """
    
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            cell_type = grid[r][c]
            style = get_cell_style(cell_type)
            
            # The trick: use a hidden button or form to handle the click callback
            # We use an invisible form/button structure to call the handler function
            
            # Create a unique key for the button
            button_key = f"cell_{r}_{c}"
            
            # Use st.form to capture button press and execute callback
            with st.container():
                # Define the button visually using markdown for custom styling
                cell_label = ""
                if cell_type in ('S', 'G'):
                    cell_label = cell_type

                button_html = f"""
                <div class="{style} h-10 w-10 flex items-center justify-center text-sm transition-all duration-100 ease-in-out">
                    {cell_label}
                </div>
                """
                
                # Streamlit doesn't easily allow buttons within markdown cells to trigger callbacks,
                # so we use a hidden button overlaying the HTML content or a dedicated button 
                # within a container that visually looks like the grid cell.
                # For simplicity and functionality, let's use the native Streamlit button/columns 
                # structure and apply minimal styling via markdown for the cells.
                
                # --- Streamlit Native Grid Rendering (More reliable for callbacks) ---
                
                # Use a dummy button structure that calls the handler
                st.button(
                    cell_label if cell_type in ('S', 'G') else '',
                    key=button_key,
                    on_click=handle_cell_click,
                    args=(r, c),
                    # Apply custom styling via Streamlit's style attribute or component hacks
                    # This is hard in native Streamlit, so we fall back to a grid of buttons 
                    # styled to look like cells.
                    # This relies on custom CSS injected via markdown.
                    # Let's construct a cleaner, more reliable HTML/Markdown injection approach.
                    
                    # Instead of buttons, use columns and an HTML click handler workaround 
                    # if Streamlit button styling is too restrictive.
                    # For a clean implementation, let's use the HTML approach with st.markdown
                    # and rely on Streamlit's nature (full rerun on input) to process the click.
                    
                    # Since direct JS injection for click listeners is restricted, we'll revert to 
                    # the button/form/container method where the visual is in the HTML block 
                    # *above* the grid definition, and we manage the grid by index.
                    pass # Placeholder for now, the final grid drawing uses the HTML structure below.
    
    # --- Final Grid HTML Structure (Optimized for Streamlit Reruns) ---
    
    # We will use st.columns for the grid layout and st.button for the interaction
    # because that is the most reliable way to trigger a rerun with state update in Streamlit.
    
    st.markdown(
        """
        <style>
            .grid-row {
                display: flex;
                flex-direction: row;
                gap: 0px; /* Remove gaps between cells */
            }
            .grid-cell {
                width: 35px;
                height: 35px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                transition: all 0.2s;
                border: 1px solid #ccc; /* Visible grid lines */
                border-radius: 0px;
                cursor: pointer;
            }
            .cell-E { background-color: #f8f9fa; }
            .cell-E:hover { background-color: #e9ecef; }
            .cell-S { background-color: #48bb78; color: white; border-color: #38a169; } /* Green */
            .cell-G { background-color: #f56565; color: white; border-color: #e53e3e; } /* Red */
            .cell-W { background-color: #2d3748; border-color: #1a202c; } /* Dark Gray/Black */
            .cell-V { background-color: #f6e05e; } /* Yellow - Visited */
            .cell-P { background-color: #4299e1; color: white; } /* Blue - Path */
        </style>
        """,
        unsafe_allow_html=True
    )

    # Use st.empty to hold the dynamic grid content
    grid_placeholder = st.empty()
    
    grid_content = ""
    for r in range(GRID_SIZE):
        grid_content += '<div class="grid-row">'
        for c in range(GRID_SIZE):
            cell_type = grid[r][c]
            cell_class = f"cell-{cell_type}"
            cell_label = cell_type if cell_type in ('S', 'G') else ''
            
            # Embed the interaction logic into the HTML for the visualizer.
            # We use st.columns/st.button for actual interaction reliability,
            # but for visualization, we'll inject the styled HTML and update the state 
            # only when the simulation runs.
            
            # To handle interaction cleanly, we'll use a hidden set of buttons overlaid. 
            # Since that's complicated, we use the simpler, slightly less dynamic 
            # approach of Streamlit's native components.
            
            # For the visualization part, we use a single HTML block to show the state.
            grid_content += f"""
                <div class="grid-cell {cell_class}" id="cell_{r}_{c}">
                    {cell_label}
                </div>
            """
        grid_content += '</div>'
    
    # Render the static HTML visualization (will update on rerun)
    grid_placeholder.markdown(grid_content, unsafe_allow_html=True)


# --- Application Layout ---

def main():
    """Main function to run the Streamlit app."""
    st.set_page_config(layout="centered", page_title="Pathfinding Visualizer")
    
    st.title("🤖 Grid Pathfinding Visualizer (BFS)")
    st.markdown("""
    Visualize the Breadth-First Search (BFS) algorithm finding the shortest path 
    on a 10x10 grid. Set the start (S), goal (G), and walls (W) using the tools below.
    """)

    # --- Tool Selection ---
    
    st.subheader("1. Select Your Tool")
    
    col_s, col_g, col_w, col_e = st.columns(4)
    
    # Helper to set the tool in session state
    def set_tool(tool_key):
        clear_path() # Clear path on tool change
        st.session_state.current_tool = tool_key
        st.session_state.message = f"Tool changed to: {CELL_TYPES[tool_key]}. Click the grid to place/toggle."

    current_tool = st.session_state.get('current_tool', 'S')
    
    # Use button clicks to set the tool
    with col_s:
        st.button("Start (S)", 
                  on_click=set_tool, 
                  args=('S',), 
                  use_container_width=True,
                  type="primary" if current_tool == 'S' else "secondary")
    with col_g:
        st.button("Goal (G)", 
                  on_click=set_tool, 
                  args=('G',), 
                  use_container_width=True,
                  type="primary" if current_tool == 'G' else "secondary")
    with col_w:
        st.button("Wall (W)", 
                  on_click=set_tool, 
                  args=('W',), 
                  use_container_width=True,
                  type="primary" if current_tool == 'W' else "secondary")
    with col_e:
        st.button("Erase (E)", 
                  on_click=set_tool, 
                  args=('E',), 
                  use_container_width=True,
                  type="primary" if current_tool == 'E' else "secondary")

    st.info(f"Current Tool: **{CELL_TYPES[current_tool]}**")
    
    # --- Grid Display and Interaction ---
    
    st.subheader("2. Configure the Grid and Run")
    
    st.caption("Click a cell below to place the current tool (S, G, W, or E).")
    
    # Streamlit requires a reliable way to trigger a function call when a cell is clicked.
    # The most robust way is to use a fixed grid of Streamlit buttons/columns.
    
    grid = get_grid_state()

    # Create the grid using st.columns in a loop
    for r in range(GRID_SIZE):
        # Create 10 columns for the row
        cols = st.columns([1] * GRID_SIZE, gap="minor")
        for c in range(GRID_SIZE):
            with cols[c]:
                cell_type = grid[r][c]
                label = cell_type if cell_type in ('S', 'G') else ''
                
                # Determine button style
                button_style = "secondary"
                if cell_type == 'S': button_style = "success"
                elif cell_type == 'G': button_style = "danger"
                elif cell_type == 'W': button_style = "tertiary"
                elif cell_type in ('V', 'P'): 
                    button_style = "primary"
                
                # Use a specific Streamlit component wrapper to apply color and size
                # Since native button styling is limited, we use a hack with markdown
                # and custom CSS injected once to make the buttons look like cells.
                
                # Check for running simulation state to disable editing
                disabled_status = st.session_state.get('running', False)

                # Use st.empty() to insert the button inside a small container
                st.button(
                    label,
                    key=f"btn_{r}_{c}",
                    on_click=handle_cell_click,
                    args=(r, c),
                    disabled=disabled_status,
                    help=f"({r}, {c})",
                    use_container_width=True
                )
                
                # --- Custom CSS for Grid Buttons ---
                # Injecting this CSS via st.markdown once at the top is cleaner, 
                # but for simplicity and guaranteeing it runs, we use this block:
                
                if r == 0 and c == 0:
                    st.markdown("""
                        <style>
                            /* Style all buttons inside the grid area */
                            .stButton > button {
                                height: 35px; /* Fixed cell size */
                                border: 1px solid #ccc;
                                padding: 0;
                                margin: 0;
                                display: flex;
                                justify-content: center;
                                align-items: center;
                                font-weight: bold;
                                transition: background-color 0.1s;
                            }
                            /* Custom colors for cell types */
                            /* Note: Streamlit's primary/secondary types overwrite some of these. 
                            The colors set below are approximations via direct CSS.*/
                            
                            /* Path */
                            [data-testid^="stButton"] button[key^="btn_"] {
                                /* Default Empty/Erase */
                                background-color: #f8f9fa; 
                            }
                            
                            /* Start */
                            [data-testid^="stButton"] button[key^="btn_"][data-testid$="success"] {
                                background-color: #48bb78 !important; color: white !important;
                            }
                            
                            /* Goal */
                            [data-testid^="stButton"] button[key^="btn_"][data-testid$="danger"] {
                                background-color: #f56565 !important; color: white !important;
                            }
                            
                            /* Wall - Using 'tertiary' hack */
                            [data-testid^="stButton"] button[key^="btn_"][data-testid$="tertiary"] {
                                background-color: #2d3748 !important; color: white !important;
                            }

                            /* Path and Visited colors need to be applied manually 
                            by overriding the button's background based on session state/label. 
                            Since that's complex, we will show the path by visually 
                            changing the cell background during the search using RERUN. 
                            We rely on the draw_grid function for the visual updates.*/
                        </style>
                    """, unsafe_allow_html=True)

    # --- Run Controls ---
    st.subheader("3. Run Pathfinding")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Run Button
        if st.button("🚀 Find Path", use_container_width=True, type="primary"):
            if st.session_state.start and st.session_state.goal:
                clear_path()
                st.session_state.running = True
                st.session_state.message = "Searching for the path..."
                
                # Rerun the search function (Streamlit reruns on state change)
                bfs_search(st.session_state.grid, st.session_state.start, st.session_state.goal)
                
                st.session_state.running = False
            else:
                st.warning("Please set both the Start (S) and Goal (G) points before running.")

    with col2:
        # Clear Path Button
        st.button("🧹 Clear Path", use_container_width=True, on_click=clear_path, disabled=st.session_state.get('running', False))

    with col3:
        # Reset Grid Button
        st.button("🔄 Reset Grid", use_container_width=True, on_click=initialize_grid, disabled=st.session_state.get('running', False))

    st.markdown("---")
    
    # --- Status Message ---
    st.markdown(f"**Status:** {st.session_state.get('message', 'Initialized.')}")
    
    st.markdown("---")
    
    # --- Legend ---
    st.subheader("Legend")
    st.markdown("""
    | Code | Cell Type | Status |
    | :--- | :--- | :--- |
    | S | **Start** | Green |
    | G | **Goal** | Red |
    | W | **Wall** | Dark Gray (Obstacle) |
    | V | **Visited** | Yellow (Explored) |
    | P | **Path** | Blue (Shortest Route) |
    """)
    
    # --- Static Visual Grid (for running state visualization) ---
    # The grid rendering using the native Streamlit buttons works for interaction,
    # but the dynamic coloring of V and P requires reruns. Since the buttons 
    # themselves are hard to restyle dynamically with the V/P colors, 
    # we'll use a visual HTML grid to show the simulation as it runs, 
    # and the Streamlit buttons for the initial setup.
    
    st.markdown("---")
    st.subheader("Live Visualization")
    # This call draws the visualization based on the current grid state.
    draw_grid()
    
    # Explanation of Pathfinding Visualization
    st.markdown("""
    
    The Breadth-First Search (BFS) algorithm explores all adjacent nodes layer by layer 
    (marked **Visited**) until it reaches the goal. Because it checks nodes in order of 
    distance from the start, it guarantees finding the shortest path in an unweighted grid.
    """)

if __name__ == '__main__':
    main()
