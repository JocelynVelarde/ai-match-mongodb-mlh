import streamlit as st
from pymongo import MongoClient
import torch
#pip install transformers
from transformers import BertTokenizer, BertModel
import numpy as np

user = st.secrets["user"]
password = st.secrets["password"]
uri_url = st.secrets["uri"]

uri = f"mongodb+srv://{user}:{password}@{uri_url}/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(uri)
db = client["techies-responses"]
collection = client["responses"]

# Create embeddings by stating model and tokenizer which are from BERT in Hugging Face
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

def generate_embeddings(text):
    inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True)
    output = model(**inputs)
    embedding = output.last_hidden_state.mean(dim=1).detach().numpy()
    return embedding

# Write a title
st.title("Matching app for techies")

# Place a divider
st.divider()

# Write a text
st.write("Welcome to my app fill the form to get started")

st.divider()

# Add a subheader
st.subheader("Fill the form to get matched")

name = st.text_input("What is your name")
programming_language = st.text_input("What are your programming languages")
framework = st.text_input("What is your favorite framework")
conference_blog = st.text_input("What is your favorite tech conference or blog post")
open_source = st.text_input("Have you contributed to open source, name projects")
tech_celebrity = st.text_input("What is your favorite tech celebrity")
code_editor = st.text_input("Favorite code editor")

if st.button("Submit"):
    # Generate my document to then convert it into embeddings using my function
    responses = {
        "name": name, 
        "programming_language": programming_language,
        "framework": framework,
        "conference_blog": conference_blog,
        "open_source": open_source, 
        "tech_celebrity": tech_celebrity, 
        "code_editor": code_editor
    }

    concatenated_responses = " ".join(responses.values())
    # Pass on the responses to my embedding model
    embeddings = generate_embeddings(concatenated_responses)
    #st.write(embeddings)

    document = {
        "responses": responses, 
        "embeddings": embeddings.tolist()
    }

    db.collection.insert_one(document)

    all_documents = list(db.collection.find())
    if all_documents:
        # Person who filled out the form is the current embedding (vector 1)
        current_embedding = embeddings.flatten()
        # Store similar interests of people from our database
        similliraties = []

        for doc in all_documents:
            store_embedding = np.array(doc["embeddings"]).flatten()
            similarity = np.dot(current_embedding, stored_embedding) / (np.linealg.norm(current_embedding)) * np.linealg.norm(store_embedding)
            similliraties.append(doc, similarity)

            similliraties = sorted(similliraties, key=lambda x:x[1], reverse=True)

            # Print for our top 3 matches
            st.write(similliraties)




    st.success("Your information was submitted correctly")
else:
    st.warning("Something went wrong")
