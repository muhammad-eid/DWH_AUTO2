from services.db_local_service import SQLiteManager
import streamlit as st
import random

# Cache the database manager instance
@st.cache_resource
def get_db():
    return SQLiteManager(db_name="mydb")

db = get_db()

# Callback function for logging
def log_callback(success, error, context):
    if success:
        st.success(f"Write to {context['db_name']} succeeded")
    else:
        st.error(f"Write failed after {context['attempts']} attempts: {error}")

# Streamlit UI for random data operations
st.title("Random Data Operations")

# Insert Random Data
if st.button("Insert Random Data"):
    random_id = random.randint(1, 1000)
    random_name = f"User{random_id}"
    random_age = random.randint(18, 65)
    db.execute_query(
        "INSERT INTO users (id, name, age) VALUES (?, ?, ?)",
        (random_id, random_name, random_age),
        callback=log_callback
    )
    st.info(f"Inserted random data into 'users' table: {random_name}, Age: {random_age}.")

# Update Random Data
if st.button("Update Random Data"):
    random_id_to_update = random.randint(1, 1000)
    new_age = random.randint(18, 65)
    db.execute_query(
        "UPDATE users SET age = ? WHERE id = ?",
        (new_age, random_id_to_update),
        callback=log_callback
    )
    st.info(f"Updated age for user with ID {random_id_to_update} to {new_age}.")

# Select All Data
if st.button("Select All Data"):
    results = db.execute_query("SELECT * FROM users")
    if results:
        st.write("Data in 'users' table:")
        st.write(results)
    else:
        st.warning("No data found in 'users' table.")