import streamlit as st
from pymongo import MongoClient
import plotly.express as px
import torch
#pip install transformers
from transformers import BertTokenizer, BertModel
import numpy as np
from sklearn.decomposition import PCA
import pandas as pd

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

    client["techies-responses"]["responsesAgain"].insert_one(document)
    #db.collection.insert_one(document)

    all_documents = list(client["techies-responses"]["responsesAgain"].find())
    if all_documents:
        # Person who filled out the form is the current embedding (vector 1)
        current_embedding = embeddings.flatten()
        # Store similar interests of people from our database
        similliraties = []

        for doc in all_documents:
            store_embedding = np.array(doc["embeddings"]).flatten()
            # Cosine similarity formula (nothing new that i invented)
            similarity = np.dot(current_embedding, store_embedding) / (np.linalg.norm(current_embedding)) * np.linalg.norm(store_embedding)
            similliraties.append((doc, similarity))

            similliraties = sorted(similliraties, key=lambda x:x[1], reverse=True)

            # Print for our top 3 matches
            st.subheader("Your top 3 matches")
            st.divider()
            for match, similarity in similliraties[:3]:
                st.write(similarity)
                st.write(match["responses"])

            st.subheader("Embedding graph display")
            embedding_list = [np.array(doc["embeddings"]).flatten() for doc in all_documents]
            pca = PCA(n_components=2)
            reduce_embeddings = pca.fit_transform(embedding_list)

            names = [doc["responses"]["name"] for doc in all_documents]
            df = pd.DataFrame(reduce_embeddings, columns=["x", "y"])

            df["name"] = names
            fig = px.scatter(df, x="x", y='y', text="name", title="Embedding plot")
            st.plotly_chart(fig)


    st.success("Your information was submitted correctly")
else:
    st.warning("Something went wrong")
