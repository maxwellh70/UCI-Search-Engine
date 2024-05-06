import PySimpleGUI as sg
import json
from collections import defaultdict, Counter
import os
from dotenv import load_dotenv
import numpy as np
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import RegexpTokenizer
import psycopg
import nltk
from time import perf_counter
from heapq import heapify, heappop

nltk.download("stopwords")
nltk.download("wordnet")
load_dotenv()

NUM_URLS = 37497

# Create the layout for the window
layout = [
    [sg.Input(key='-SEARCH-', size=(90, 10)), sg.Button('Search', key='-SEARCH-BUTTON-'),
     sg.Button('Exit', key='-EXIT-')],
    [sg.Listbox(values=[], size=(100, 40), key='-LIST-')],
]
# Set the theme
sg.theme('Dark Teal 9')
# Event Loop

# Create the tags weight
TAG_WEIGHT = {
    "None": 0,
    "b": 0.1,
    "strong": 0.1,
    "p": 0.05,
    "h6": 0.15,
    "h5": 0.17,
    "h4": 0.2,
    "h3": 0.25,
    "h2": 0.3,
    "h1": 0.4,
    "title": 0.5,
}


def get_results(keyword: dict[str, list[str]], query: str, db: psycopg.Connection) -> list[
    tuple[str, list[str], list[int], list[float], str]]:
    """
    :param keyword: list of keywords to search for
    :param query: query to execute
    :param db: database connection
    :return: list of tuples containing the results
    """
    # Execute the query
    with db.cursor() as cursor:
        cursor.execute(query, keyword)
        results = cursor.fetchall()
    return results


def tokenize(keywords: str, tokenizer: RegexpTokenizer, lemmatizer: WordNetLemmatizer, stopword_set: set[str]) -> list[
    str]:
    """
    :param keywords: string of keywords to tokenize
    :param tokenizer: tokenizer object
    :param lemmatizer: lemmatizer object
    :param stopword_set: set of stopwords
    :return: list of tokens
    """
    tokens = tokenizer.tokenize(keywords)
    tokens = [lemmatizer.lemmatize(token.lower()) for token in tokens]
    tokens = [token for token in tokens if token not in stopword_set]
    # Sort tokens
    tokens.sort()
    return tokens


def get_query_and_params(keywords: list[str]) -> tuple[str, dict[str, list[str]]]:
    """
    :param keywords: list of keywords to search for
    :return: query and parameters to execute
    f"""
    return (
        f"SELECT token, doc_ids, tfidf_array, tags_array FROM inverted_index where token = ANY(%(keywords)s) ORDER BY token ASC",
        {"keywords": keywords})


def get_query_vector(freq_array: list[tuple[str, int]],
                     db_results: list[tuple[str, list[str], list[int], list[float], str]]) -> np.array:
    """
    :param freq_array: array of tuples containing the token and its frequency in the query
    :param db_results: list of tuples containing the results 
    :return: array of tf-idf scores for the query 
    """
    # Create an array of tf-idf scores for the query
    query_tfidf = np.zeros(len(freq_array))
    for i, data in enumerate(freq_array):
        _, freq = data
        tf = 1 + np.log10(freq)
        idf = np.log10(NUM_URLS / len(db_results[i][1]))
        query_tfidf[i] = tf * idf
    return normalize_vector(query_tfidf)


def normalize_vector(array: np.array) -> np.array:
    """
    :param array: array to normalize
    :return: normalized array
    """
    # Get the norm of the array
    norm = np.linalg.norm(array)
    # If the norm is 0, return the array
    if norm == 0:
        return array
    # Normalize the array
    return array / norm


def get_doc_vector(db_results: list[tuple[str, list[str], list[int], list[float], str]]) -> tuple[
    dict[str, np.array], dict[str, float]]:
    """
    For each token in tokens, iterate through the doc_ids, and append the tf-idf score of that 
    :param db_results: list of tuples containing the results
    :return: dictionary that maps the doc_id to the tf-idf vector for the document
    """
    max_vector_length = len(db_results)
    doc_vector: dict[str, list | np.array] = defaultdict(list)
    tag_weight: dict[str, float] = defaultdict(float)
    term_count = 0
    for _, doc_ids, tfidf_array, tags_array in db_results:
        for i, doc_id in enumerate(doc_ids):
            # if there should be terms before the current one,
            # insert 0 for their tf-idf
            diff = term_count - len(doc_vector)
            if diff != 0:
                for _ in range(diff):
                    doc_vector[doc_id].append(0)
            # Check if the token in the current doc_id is in an important tag        
            doc_vector[doc_id].append(tfidf_array[i])
            tag_weight[doc_id] += sum(TAG_WEIGHT[tag] for tag in tags_array[i])
        term_count += 1
    # Reshape all values in doc_vector to have the length of the max_vector_length, fill in 0 for missing values
    for doc_id in doc_vector:
        doc_vector[doc_id] = np.array(doc_vector[doc_id])
        doc_vector[doc_id] = np.pad(doc_vector[doc_id], (0, max_vector_length - len(doc_vector[doc_id])), 'constant',
                                    constant_values=(0, 0))

    # normalize the vectors
    for key, arr in doc_vector.items():
        doc_vector[key] = normalize_vector(arr)
    return doc_vector, tag_weight


def get_cosine_similarity_score(query_vector: np.array, doc_vectors: dict[str, np.array]) -> list[tuple[float, str]]:
    '''
    :param query_vector: the tf-idf vector for the query
    :param doc_vectors: a dictionary that maps the doc_id to the tf-idf vector for the document
    :return: a list of tuples containing the cosine similarity score and the doc_id
    '''
    result = []
    for doc_id, doc_vector in doc_vectors.items():
        # Take the query vector and dot product it with the doc vector. Round to 2 decimal places an multiply by -1 for sorting
        result.append((round(np.dot(query_vector, doc_vector), 2) * -1, doc_id))
    return result


def get_net_score(cosine_similarity_scores: list[tuple[float, str]], tag_weights: dict[str, float]) -> list[
    tuple[float, str]]:
    """
    This function calculates the net score for each document by subtracting the
    tag weight from the cosine similarity score
    :param cosine_similarity_scores: list of tuples containing the cosine similarity score and the doc_id
    :param tag_weights: dictionary that maps the doc_id to the tag weight
    :return list of tuples containing the net score and the doc_id
    """
    net_score = []
    for score, doc_id in cosine_similarity_scores:
        net_score.append((score - tag_weights[doc_id], doc_id))
    return net_score


def get_top_k_results(cosine_similarity_scores: list[tuple[float, str]], k: int, url_maps: dict[str, str]) -> list[str]:
    """
    :param cosine_similarity_scores: list of tuples containing the cosine similarity score and the doc_id
    :param k: number of top results to return
    :param url_maps: dictionary that maps the doc_id to the url
    :return: list of tuples containing the k biggest cosine similarity scores and the doc_id
    """
    # Heapify the list of tuples
    heapify(cosine_similarity_scores)
    result = []
    # Loop through the list of tuples and append the url to the result list
    for _ in range(k):
        # Break if there are no more results
        if len(cosine_similarity_scores) == 0:
            break
        # Get the url from the url_maps dictionary
        url = url_maps[heappop(cosine_similarity_scores)[1]]
        # Append the url to the result list
        result.append(url)
    return result


def clear_all(*args: list | dict) -> None:
    """
    :param args: list of lists or dictionaries to clear"""
    for arg in args:
        arg.clear()


def main():
    # Initialize the GUI, tokenizer, lemmatizer, stopword set, and database connection
    tokenizer = RegexpTokenizer(r"\w+")
    lemmatizer = WordNetLemmatizer()
    stopword_set = set(stopwords.words("english"))
    db = psycopg.connect(os.getenv("SQL_URL"))
    window = sg.Window('ICS Search Engine', layout, resizable=True)
    # Load the bookkeeping.json file
    url_maps: dict[str, str] = json.load(open("./bookkeeping.json"))
    while True:
        # Read the GUI events
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        # Exit event
        if event == '-EXIT-':
            break
        # Search event
        if event == '-SEARCH-BUTTON-':
            # Get the query from the GUI
            keywords = values['-SEARCH-']
            if not keywords:
                continue
            # Initialize a timer
            start_time = perf_counter()
            # tokenize the query
            tokens = tokenize(keywords, tokenizer, lemmatizer, stopword_set)
            # get the SQL query from tokens
            query, params = get_query_and_params(tokens)
            # get DB query result
            db_results = get_results(params, query, db)
            # get the tf-idf vectors for each doc and also include the  
            # tag weight vector which is a vector of weights of each token in a corresponding doc
            doc_vectors, tag_weights = get_doc_vector(db_results)
            # sort the dictionary through counter
            freq_dict = sorted(Counter(tokens).items(), key=lambda x: x[0])
            # get the tf-idf vector for the query
            query_vector = get_query_vector(freq_dict, db_results)
            # get the cosine similarity score for each document
            cosine_similarity_scores = get_cosine_similarity_score(query_vector, doc_vectors)
            # add the tag weight in get_net_score
            net_score = get_net_score(cosine_similarity_scores, tag_weights)
            # Get top 20 results
            top_k_results = get_top_k_results(net_score, 20, url_maps)
            print(f"Time taken: {perf_counter() - start_time}")
            # Update the GUI
            window['-LIST-'].update(values=top_k_results)
            # Clear all the variables to free up memory
            clear_all(doc_vectors, freq_dict, cosine_similarity_scores, top_k_results, db_results, tokens)
    window.close()


"""
Thought process:
Take in query, tokenize.
Retrieve the inverse index row from database
calculate the tf-idf for query
Retrieve the vector for each documents appear in all the doc_id in the inverse index result:
    each of the vector will have the same length as the query vector: 
        if a token is not present in that document, 0 as its tf-idf.
For each document's tf-idf vector, calculate the similarity score between the query vector
and the document's vector.

Output urls from highest similarity score to lowest.
"""

if __name__ == "__main__":
    main()
