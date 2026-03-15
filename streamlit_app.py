import streamlit as st
import requests
import pandas as pd
from datetime import date
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="Employee Management System",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main { padding-top: 2rem; }
    .metric-card { padding: 1.5rem; border-radius: 0.8rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
    </style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = "http://localhost:8000/employees"

# Header
st.markdown("# 👥 Employee Management System")
st.markdown("---")

# Helper functions
def get_all_employees(skip=0, limit=50, search_query=None):
    try:
        params = {"skip": skip, "limit": limit}
        if search_query:
            params["q"] = search_query
        response = requests.get(API_BASE_URL, params=params, timeout=5)
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.ConnectionError:
        return None, "⚠️ Cannot connect to API. Make sure FastAPI server is running on http://localhost:8000"
    except Exception as e:
        return None, f"❌ Error: {str(e)}"

def get_employee_by_id(employee_id):
    try:
        response = requests.get(f"{API_BASE_URL}/{employee_id}", timeout=5)
        response.raise_for_status()
        return response.json(), None
    except:
        return None, "❌ Employee not found"

def create_employee(employee_data):
    try:
        response = requests.post(API_BASE_URL, json=employee_data, timeout=5)
        if response.status_code == 409:
            return None, "❌ Email already exists"
        response.raise_for_status()
        return response.json(), "✅ Employee created!"
    except Exception as e:
        return None, f"❌ Error: {str(e)}"

def update_employee(employee_id, employee_data):
    try:
        response = requests.put(f"{API_BASE_URL}/{employee_id}", json=employee_data, timeout=5)
        if response.status_code == 409:
            return None, "❌ Email already exists"
        response.raise_for_status()
        return response.json(), "✅ Employee updated!"
    except Exception as e:
        return None, f"❌ Error: {str(e)}"

def delete_employee(employee_id):
    try:
        response = requests.delete(f"{API_BASE_URL}/{employee_id}", timeout=5)
        response.raise_for_status()
        return True, "✅ Employee deleted!"
    except Exception as e:
        return False, f"❌ Error: {str(e)}"

# Sidebar Navigation
with st.sidebar:
    st.markdown("### 🎯 Navigation")
    page = st.radio(
        "Select page:",
        ["📊 Dashboard", "👤 Create", "📋 View All", "✏️ Update", "🗑️ Delete"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.info(f"API: `{API_BASE_URL}`")

# ==================== DASHBOARD ====================
if page == "📊 Dashboard":
    st.subheader("Dashboard Overview")
    
    employees, error = get_all_employees(limit=200)
    
    if error:
        st.error(error)
    elif employees:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("👥 Total", len(employees))
        with col2:
            active = sum(1 for e in employees if e.get('is_active'))
            st.metric("✅ Active", active)
        with col3:
            inactive = len(employees) - (sum(1 for e in employees if e.get('is_active')))
            st.metric("❌ Inactive", inactive)
        with col4:
            depts = len(set(e.get('department') for e in employees if e.get('department')))
            st.metric("🏢 Departments", depts)
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if any(e.get('department') for e in employees):
                dept_data = pd.DataFrame([
                    {'Department': e.get('department', 'Unassigned')}
                    for e in employees if e.get('department')
                ])
                if not dept_data.empty:
                    dept_count = dept_data['Department'].value_counts()
                    fig = px.pie(values=dept_count.values, names=dept_count.index, 
                                title="Employees by Department", hole=0.3)
                    st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            status_data = {"Active": sum(1 for e in employees if e.get('is_active')),
                          "Inactive": len(employees) - sum(1 for e in employees if e.get('is_active'))}
            fig = px.pie(values=list(status_data.values()), names=list(status_data.keys()),
                        title="Employee Status", hole=0.3,
                        color_discrete_map={'Active': '#28a745', 'Inactive': '#dc3545'})
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No employees. Create one to get started!")

# ==================== CREATE ====================
elif page == "👤 Create":
    st.subheader("Create New Employee")
    
    with st.form("create_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            first_name = st.text_input("First Name *", max_chars=100)
            email = st.text_input("Email *", max_chars=255)
            department = st.text_input("Department", max_chars=100)
            salary = st.number_input("Salary", min_value=0.0, step=1000.0)
        
        with col2:
            last_name = st.text_input("Last Name *", max_chars=100)
            phone = st.text_input("Phone", max_chars=30)
            title = st.text_input("Job Title", max_chars=100)
            joining_date = st.date_input("Date of Joining", value=date.today())
        
        is_active = st.checkbox("Active", value=True)
        
        submitted = st.form_submit_button("✅ Create", use_container_width=True)
        
        if submitted:
            if not first_name.strip() or not last_name.strip() or not email.strip():
                st.error("❌ First Name, Last Name, and Email are required!")
            else:
                emp_data = {
                    "first_name": first_name.strip(),
                    "last_name": last_name.strip(),
                    "email": email.strip(),
                    "phone": phone.strip() if phone.strip() else None,
                    "department": department.strip() if department.strip() else None,
                    "title": title.strip() if title.strip() else None,
                    "salary": salary if salary > 0 else None,
                    "date_of_joining": str(joining_date),
                    "is_active": is_active
                }
                
                result, msg = create_employee(emp_data)
                if result:
                    st.success(msg)
                    st.json(result)
                else:
                    st.error(msg)

# ==================== VIEW ALL ====================
elif page == "📋 View All":
    st.subheader("View & Search Employees")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        search = st.text_input("🔍 Search by name, email, dept, or title")
    with col2:
        st.button("🔄 Refresh", use_container_width=True)
    
    employees, error = get_all_employees(limit=200, search_query=search if search else None)
    
    if error:
        st.error(error)
    elif employees:
        st.info(f"Found {len(employees)} employee(s)")
        
        df = pd.DataFrame(employees)
        cols = ['id', 'first_name', 'last_name', 'email', 'phone', 'department', 'title', 'salary', 'is_active']
        available = [c for c in cols if c in df.columns]
        df_display = df[available].copy()
        df_display.columns = ['ID', 'First', 'Last', 'Email', 'Phone', 'Dept', 'Title', 'Salary', 'Active']
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        csv = df_display.to_csv(index=False)
        st.download_button("📥 Download CSV", csv, "employees.csv", "text/csv")
    else:
        st.warning("No employees found")

# ==================== UPDATE ====================
elif page == "✏️ Update":
    st.subheader("Update Employee")
    
    employees_list, error = get_all_employees(limit=200)
    
    if error:
        st.error(error)
    elif employees_list:
        options = {f"{e['id']} - {e['first_name']} {e['last_name']}" : e['id'] for e in employees_list}
        selected_display = st.selectbox("Select Employee:", list(options.keys()))
        selected_id = options[selected_display]
        
        employee, err = get_employee_by_id(selected_id)
        
        if employee:
            st.success(f"Loaded: **{employee['first_name']} {employee['last_name']}**")
            
            with st.form("update_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    first_name = st.text_input("First Name", value=employee.get('first_name', ''))
                    email = st.text_input("Email", value=employee.get('email', ''))
                    department = st.text_input("Department", value=employee.get('department', '') or '')
                    salary = st.number_input("Salary", value=float(employee.get('salary') or 0), min_value=0.0, step=1000.0)
                
                with col2:
                    last_name = st.text_input("Last Name", value=employee.get('last_name', ''))
                    phone = st.text_input("Phone", value=employee.get('phone', '') or '')
                    title = st.text_input("Job Title", value=employee.get('title', '') or '')
                    is_active = st.checkbox("Active", value=employee.get('is_active', True))
                
                submit = st.form_submit_button("💾 Update", use_container_width=True)
                
                if submit:
                    update_data = {
                        "first_name": first_name if first_name else None,
                        "last_name": last_name if last_name else None,
                        "email": email if email else None,
                        "phone": phone if phone else None,
                        "department": department if department else None,
                        "title": title if title else None,
                        "salary": salary if salary > 0 else None,
                        "is_active": is_active
                    }
                    
                    result, msg = update_employee(selected_id, update_data)
                    if result:
                        st.success(msg)
                        st.json(result)
                    else:
                        st.error(msg)
    else:
        st.warning("No employees found")

# ==================== DELETE ====================
elif page == "🗑️ Delete":
    st.subheader("Delete Employee")
    st.warning("⚠️ This action is irreversible!")
    
    employees_list, error = get_all_employees(limit=200)
    
    if error:
        st.error(error)
    elif employees_list:
        options = {f"{e['id']} - {e['first_name']} {e['last_name']}" : e['id'] for e in employees_list}
        selected_display = st.selectbox("Select Employee:", list(options.keys()))
        selected_id = options[selected_display]
        
        employee, err = get_employee_by_id(selected_id)
        
        if employee:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**Name:** {employee['first_name']} {employee['last_name']}")
            with col2:
                st.write(f"**Email:** {employee['email']}")
            with col3:
                st.write(f"**Dept:** {employee.get('department', 'N/A')}")
            
            st.markdown("---")
            confirm = st.checkbox("✅ Confirm permanent deletion")
            
            if confirm and st.button("🗑️ Delete", type="primary", use_container_width=True):
                success, msg = delete_employee(selected_id)
                if success:
                    st.success(msg)
                    st.balloons()
                else:
                    st.error(msg)
    else:
        st.warning("No employees found")

st.markdown("---")
st.markdown("<div style='text-align: center; color: #888;'>Employee Management System v1.0</div>", unsafe_allow_html=True)
