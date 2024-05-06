import psycopg.types.json as sql_json
"""
Table schema for the inverted index table
public.inverted_index
(
    token           character varying(200) primary key not null,
    doc_ids         character varying[],
    frequency_array integer[],
    tfidf_array     double precision[],
    tags_array      jsonb 
);
"""


class ReverseIndex:
    
    def __init__(self, token: str, doc_id: str, frequency: int, tags_list: set[str]):
        """
        :param token: The token
        :param doc_id: The document id
        :param frequency: The frequency of the token in the document
        :param tags_list: The list of tags for the token in the document
        """
        self.token: str = token
        self.doc_ids = [doc_id]
        self.frequency_array = [frequency]
        if len(tags_list) == 0:
            # If the tags list is empty, add None to the list
            tags_list.add("None")
        # Convert the set to a list
        self.tags_array = [list(tags_list)]
        self.tfidf_array = []

    def add(self, doc_id: str, frequency: int, tags_list: set[str]) -> None:
        """
        :param doc_id: The document id
        :param frequency: The frequency of the token in the document
        :param tags_list: The list of tags for the token in the document
        :return: None
        """
        self.doc_ids.append(doc_id)
        self.frequency_array.append(frequency)
        if len(tags_list) == 0:
            tags_list.add("None")
        self.tags_array.append(list(tags_list))


    def add_tfidf(self, tfidf: float) -> None:
        """
        :param tfidf: The tfidf value for the token in the document
        :return: None
        """
        self.tfidf_array.append(tfidf)

    def get_params(self) -> dict[str, list]:
        """
        :param insert: True if the query is for an insert, False if the query is for an update
        :return: The query string
        """
        try:
            params = {
                "token": self.token,
                "doc_id": self.doc_ids,
                "frequency": self.frequency_array,
                "tags": sql_json.Jsonb(self.tags_array),
                "tfidf": self.tfidf_array
            }
        except:
            print(self.tags_array)
        return params