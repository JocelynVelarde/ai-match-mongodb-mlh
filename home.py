import streamlit as st

# Write a title
st.title("Matching app for techies")

# Place a divider
st.divider()

# Write a text
st.write("Welcome to my app fill the form to get started")

st.divider()

# Add a subheader
st.subheader("Fill the form to get matched")

st.text_input("What is your name")
st.text_input("What are your programming languages")
st.text_input("What is your favorite framework")
st.text_input("What is your favorite tech conference or blog post")
st.text_input("Have you contributed to open source, name projects")
st.text_input("What is your favorite tech celebrity")
st.text_input("Favorite code editor")

if st.button("This is a button"):
    # Generate potential matches for my tech form
    st.success("Yai you have been matched!")
else:
    st.warning("Something went wrong")