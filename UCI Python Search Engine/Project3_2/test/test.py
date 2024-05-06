import numpy as np
from collections import defaultdict


def normalize_vector(array: np.array) -> np.array:
    result_array = []
    vector_length = np.sqrt(np.dot(array, array))
    if vector_length == 0:
        return array
    for item in array:
        result_array.append(item/vector_length)
    return np.array(result_array)


def get_doc_vector(db_results: list[tuple[str, list[str], list[int], list[float], str]]) -> dict[str, list[float]]:
    """
    For each token in tokens, iterate through the doc_ids, and append the tf-idf score of that 
    token: doc_id pair to the doc_vector[doc_id]
    """
    max_vector_length = len(db_results)
    doc_vector: dict[str, list] = defaultdict(list)
    term_count = 0
    for _, doc_ids, _, tfidf_array, _ in db_results:
        for i, doc_id in enumerate(doc_ids):
            # if there should be terms before the current one,
            # insert 0 for their tf-idf
            diff = term_count - len(doc_vector)
            if diff != 0:
                for _ in range(diff):
                    doc_vector[doc_id].append(0)
            doc_vector[doc_id].append(tfidf_array[i])
        term_count += 1
    # Reshape all values in doc_vector to have the length of the max_vector_length, fill in 0 for missing values
    for doc_id in doc_vector:
        doc_vector[doc_id] = np.array(doc_vector[doc_id])
        doc_vector[doc_id] = np.pad(doc_vector[doc_id], (0, max_vector_length - len(
            doc_vector[doc_id])), 'constant', constant_values=(0, 0))

    # normalize the vectors
    for key, arr in doc_vector.items():
        doc_vector[key] = normalize_vector(arr)
    return doc_vector


toy_db_result = [("Antony",     ["AnC", "JC", "TT", "H", "O", "M"], [157, 73, 0, 0, 0, 0], [4.05, 3.63, 0, 0, 0, 0], []),
                 ("Brutus",     ["AnC", "JC", "TT", "H", "O", "M"], [
                  4, 157, 0, 1, 0, 0], [1.75, 3.49, 0, 1.09, 0, 0], []),
                 ("Ceasar",     ["AnC", "JC", "TT", "H", "O", "M"], [
                  232, 227, 0, 2, 1], [2.93, 2.92, 0, 1.13, 0.87, 0.87], []),
                 ("Calpurnia",  ["AnC", "JC", "TT", "H", "O", "M"], [
                  0, 10, 0, 0, 0, 0], [0, 3.14, 0, 0, 0, 0], []),
                 ("Cleopatra",  ["AnC", "JC", "TT", "H", "O", "M"], [
                  57, 0, 0, 0, 0, 0], [4.32, 0, 0, 0, 0, 0], []),
                 ("mercy",      ["AnC", "JC", "TT", "H", "O", "M"], [
                  2, 0, 3, 5, 5, 1], [1.13, 0, 1.28, 1.48, 1.48, 0.87], []),
                 ("worser",     ["AnC", "JC", "TT", "H", "O", "M"], [2, 0, 1, 1, 1, 0], [1.26, 0, 0.97, 0.97, 0.97, 0], [])]

toy_qr_result = [("Brutus",     ["AnC", "JC", "TT", "H", "O", "M"], [
                  4, 157, 0, 1, 0, 0], [1.75, 3.49, 0, 1.09, 0, 0], []),
                 ("Ceasar",     ["AnC", "JC", "TT", "H", "O", "M"], [
                  232, 227, 0, 2, 1], [2.93, 2.92, 0, 1.13, 0.87, 0.87], [])]
dd = get_doc_vector(toy_qr_result)
print(dd)
a = np.array([0.0])
print(np.dot(a, a))
