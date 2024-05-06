from src import ExtractTokens, ReverseIndex, DatabaseIO
import sys
import logging
import dotenv
import os
import itertools
dotenv.load_dotenv()
import math

logger = logging.getLogger(__name__)

NUM_URLS = 37497


def calculate_tfidf(num_documents_with_token: int, frequency: int) -> float:
    """
    :param num_documents_with_token: The number of documents that contain the token
    :param frequency: The frequency of the token in the document
    :return: The tfidf value
    """
    return math.log(1 + frequency, 10) * math.log(NUM_URLS / (1 + num_documents_with_token),10) 

def check_token_exists(database: DatabaseIO)  -> bool:
    query = "SELECT count(*) FROM inverted_index"
    result = database.execute_query(query)
    return result[0][0] > 0

def main(args: list[str]):
    # create an instance of extractTokens
    logging.basicConfig(filename="test_run/index_run.txt", filemode="a", level=logging.INFO,
                        format='%(asctime)s (%(name)s) %(levelname)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    extractor = ExtractTokens(args[1])
    # extract tokens from the folder
    database = DatabaseIO(os.getenv("SQL_URL"))
    database.create_table()
    # First phase: extract tokens and store them in the database
    token_dict: dict[str, ReverseIndex] = {}
    valid_doc_id_count = 0 
    # Generates the doc id and the token information
    for doc_id, token_information in extractor.extract_tokens():
        # Increment the number of valid doc ids
        if len(token_information) > 0:
            valid_doc_id_count += 1
        # Get the token and the token metadata, which contains the frequency and the tags
        for token, token_metadata in token_information.items():
            # Check that the token exists in the database
            if token not in token_dict:
                # Insert the token, ReverseIndex pair into the dictionary
                token_dict[token] = ReverseIndex(token, doc_id, token_metadata["count"], token_metadata["tags"]) 
            else:
                # Update the ReverseIndex object
                token_dict[token].add(doc_id, token_metadata["count"], token_metadata["tags"])
    # Write document token count to file
    print("Number of unique tokens", len(token_dict))
    print(f"Number of processed urls {valid_doc_id_count}")
    # Second phase: calculate tfidf and update the database
    if not check_token_exists(database):
        for token in token_dict:
            # Calculate the tfidf for each document
            num_documents_with_token = len(token_dict[token].doc_ids)
            for i in range(len(token_dict[token].frequency_array)):
                # Calculate the tfidf of the token and add it to the ReverseIndex object
                token_dict[token].add_tfidf(calculate_tfidf(num_documents_with_token, token_dict[token].frequency_array[i]))
            # Check that the arrays are the same length
            assert len(token_dict[token].doc_ids) == len(token_dict[token].frequency_array) == len(token_dict[token].tfidf_array) == len(token_dict[token].tags_array)
        query = """INSERT INTO inverted_index 
        VALUES (%(token)s, %(doc_id)s, %(frequency)s, %(tfidf)s, %(tags)s)"""

        # Third phase: write the data to the database
        # Slice the dictionary in chunks of 1000 key/value pairs then write to the database
        # 0 1000, 1000, 2000 .... 480000
        
        length = len(token_dict)
        for i in range(0, length, 1000):
            params = []
            # Loop through the dictionary in chunks of 1000
            for token, token_object in itertools.islice(token_dict.items(), i, i + 1000):
                # Append the parameters to the list
                params.append(token_object.get_params())
            # Write the data to the database
            database.execute_many(query, params, i, i + 1000)

        # Loop through the dictionary and write to the database
        # for token, token_object in token_dict.items():
        #     params = token_object.get_params()
        #     database.execute_query(query, **params)
3







if __name__ == "__main__":
    main(sys.argv)
