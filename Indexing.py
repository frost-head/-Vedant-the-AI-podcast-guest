import os
import torch
import faiss
import fitz  # PyMuPDF
import numpy as np
import spacy
from transformers import AutoTokenizer, AutoModel

# Choose a different embedding model if needed
embedding_model_name = "thenlper/gte-base"

# Load chosen BERT-based model and tokenizer
tokenizer = AutoTokenizer.from_pretrained(embedding_model_name)
model = AutoModel.from_pretrained(embedding_model_name)

# Load SpaCy English model
nlp = spacy.load("en_core_web_sm")

# Function to extract text from a PDF file
def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as pdf_document:
        for page_number in range(pdf_document.page_count):
            page = pdf_document.load_page(page_number)
            text += page.get_text("text")
    return text

# Function to create embeddings for a given text with handling for maximum sequence length
def get_embedding_for_text(text, max_seq_length=512):
    tokens = tokenizer(text, return_tensors="pt", truncation=True, max_length=max_seq_length)

    if tokens["input_ids"].size(1) > max_seq_length:
        tokens["input_ids"] = tokens["input_ids"][:, :max_seq_length]
        tokens["attention_mask"] = tokens["attention_mask"][:, :max_seq_length]

    with torch.no_grad():
        outputs = model(**tokens)
        embedding = outputs.last_hidden_state.mean(dim=1).numpy()

    return embedding

# Function to create embeddings for overlapping paragraphs of data and store in Faiss index
def create_data_embeddings_and_index(pdf_folder, existing_index=None, window_size=5):
    data_embeddings = []

    if existing_index is None:
        # Use IndexFlatL2
        data_index = faiss.IndexFlatL2(768)
    else:
        data_index = faiss.index_cpu_to_gpu(existing_index, 0)  # Use GPU if available

    for pdf_file in os.listdir(pdf_folder):
        pdf_path = os.path.join(pdf_folder, pdf_file)
        text = extract_text_from_pdf(pdf_path)

        # Use SpaCy for sentence tokenization
        sentences = [str(sentence) for sentence in nlp(text).sents]

        for i in range(len(sentences) - window_size + 1):
            # Combine overlapping sentences to create a paragraph
            paragraph_lines = sentences[i:i + window_size]
            paragraph = " ".join(paragraph_lines)

            # Ensure the paragraph is not empty
            if paragraph.strip():
                # Create embedding for the specified chunk
                embedding = get_embedding_for_text(paragraph)
                data_embeddings.append({"file_path": pdf_path, "embedding": embedding, "paragraph": paragraph})
                data_index.add(np.array(embedding).astype('float32'))

    return data_embeddings, data_index

# Function to retrieve relevant paragraphs based on a query
def retrieve_relevant_paragraphs(query_text, data_embeddings, data_index, k=2):
    if os.path.exists("data_index.index"):
        data_index = load_faiss_index()
        data_embeddings = load_data_embeddings()
    query_embedding = get_embedding_for_text(query_text)
    _, closest_indices = data_index.search(np.array(query_embedding).astype('float32'), k)
    relevant_paragraphs = [data_embeddings[i] for i in closest_indices.flatten()]
    context = ''
    for i in relevant_paragraphs:
        context += i['paragraph']
    return context

# Function to save Faiss index to a local file
def save_faiss_index(data_index, data_index_path="/media/frost-head/files/Vedant_Index/data_index.index"):
    faiss.write_index(data_index, data_index_path)

# Function to load Faiss index from a local file
def load_faiss_index(data_index_path="/media/frost-head/files/Vedant_Index/data_index.index"):
    data_index = faiss.read_index(data_index_path)
    return data_index

# Function to add new file to existing index
def add_new_file(pdf_path, data_embeddings, data_index, window_size=5):
    text = extract_text_from_pdf(pdf_path)

    sentences = [str(sentence) for sentence in nlp(text).sents]

    for i in range(0, len(sentences), window_size):
        # Combine overlapping sentences to create a paragraph
        paragraph = " ".join(sentences[i:i + window_size])

        # Ensure the paragraph is not empty
        if paragraph.strip():
            embedding = get_embedding_for_text(paragraph)
            data_embeddings.append({"file_path": pdf_path, "embedding": embedding, "paragraph": paragraph})
            data_index.add(np.array(embedding).astype('float32'))
    save_data_embeddings(data_embeddings)
    save_faiss_index(data_index)
    return data_embeddings, data_index

# Function to save data embeddings to a local file
def save_data_embeddings(data_embeddings, data_embeddings_path="/media/frost-head/files/Vedant_Index/data_embeddings.npy"):
    np.save(data_embeddings_path, np.array(data_embeddings, dtype=object))

# Function to load data embeddings from a local file
def load_data_embeddings(data_embeddings_path="/media/frost-head/files/Vedant_Index/data_embeddings.npy"):
    return list(np.load(data_embeddings_path, allow_pickle=True))

# Example usage
# pdf_folder = "/media/frost-head/files/Vedanat_knowledge/"
# query_text = "who is father of deep learning?"

# Step 1: Create or load data embeddings and index
# if os.path.exists("data_index.index"):
#     data_index = load_faiss_index()
#     data_embeddings = load_data_embeddings()
# else:
#     data_embeddings, data_index = create_data_embeddings_and_index(pdf_folder, window_size=10)
#     save_faiss_index(data_index)
#     save_data_embeddings(data_embeddings)

# # Step 2: Retrieve relevant paragraphs based on the query
# relevant_paragraphs = retrieve_relevant_paragraphs(query_text, data_embeddings, data_index)

# # Display retrieved paragraphs
# for paragraph in relevant_paragraphs:
#     print(f"File: {paragraph['file_path']}")
#     print(f"Paragraph: {paragraph['paragraph']}")
#     print("-" * 50)

# # Example of adding a new file to existing index
# # new_pdf_path = "/path/to/new/pdf/file.pdf"
# # data_embeddings, data_index = add_new_file(new_pdf_path, data_embeddings, data_index, window_size=3)
# # save_faiss_index(data_index)
# # save_data_embeddings(data_embeddings)
