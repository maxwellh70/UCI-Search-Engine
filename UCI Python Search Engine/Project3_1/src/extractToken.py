import logging
from lxml.etree import ElementTree
from typing import Generator
from lxml import html
import os
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk
nltk.download('wordnet')
nltk.download('stopwords')

logger = logging.getLogger(__name__)

TokenInformation = dict[str, dict[str, set | int]]

"""
Handle retrieving raw data and parse the webpages into tokens.
Perform tokenization, remove stop words, perform stemming and/or lemmatization
"""


class ExtractTokens:

    valid_tags = {'title', 'h1', 'h2', 'h3',
                  'h4', 'h5', 'h6', 'b', 'p', 'strong'}

    def __init__(self, web_page_root_path, folder_count=80):
        # get the path of WEBPAGES_RAW and store it
        self.root_directory = os.path.join(web_page_root_path, "")
        # self.folders store the folders in WEBPAGES_RAW
        self.folders = []
        self.stopwords = set(stopwords.words('english'))
        # https://stackoverflow.com/questions/15547409/how-to-get-rid-of-punctuation-using-nltk-tokenizer
        # https://www.analyticsvidhya.com/blog/2022/06/stemming-vs-lemmatization-in-nlp-must-know-differences/#:~:text=Stemming%20is%20a%20process%20that,%27%20would%20return%20%27Car%27
        # Regular expression tokenizer
        self.tokenizer = RegexpTokenizer(r'\w+')
        # Lemmatizer
        self.lemmatizer = WordNetLemmatizer()
        for _, file in zip(range(folder_count), os.listdir(self.root_directory)):
            d = os.path.join(self.root_directory, file)
            if os.path.isdir(d):
                self.folders.append(d)

    # use nltk tokenizer to tokenize the page?
    def tokenize_page(self, content: ElementTree) -> TokenInformation:
        """
        Parse the human readable text content of the page and tokenize it. Remove stop words and perform lemmatization.
        :param content: the html content of the page
        :return: a dictionary of tokens and their frequency and tag information
        """
        # Get the human readable text content, drop the script and style tags and comments
        token_information = {}
        try:
            text_content = content.xpath(
                "//text()[not(ancestor::script) and not(ancestor::style) and not(ancestor::comment)]")
            for text in text_content:
                text_without_space = text.strip()
                if text_without_space != '':
                    # Start tokenizing
                    token_list = self.tokenizer.tokenize(text_without_space)
                    for token in token_list:
                        # Check if the token is not a stopword
                        if token not in self.stopwords:
                            # Lemmatize the token
                            token = self.lemmatizer.lemmatize(token.lower())
                            # Check if the token is already in the dictionary, update frequency
                            if token in token_information:
                                token_information[token]['count'] += 1
                                # If the tags are title, headings, or bold, add it to the set
                                if text.getparent().tag in self.valid_tags:
                                    # Add the tag to the set
                                    token_information[token]['tags'].add(
                                        text.getparent().tag)
                            else:
                                # Initialize the token information dictionary
                                token_information[token] = {
                                    'count': 1, 'tags': set()}
                                if text.getparent().tag in self.valid_tags:
                                    # Add the tag to the set
                                    token_information[token]['tags'].add(
                                        text.getparent().tag)
        except Exception as e:
            logger.error("Error parsing page: " + str(e))
        finally:
            return token_information
        # Convert the list of text content to a single string
        # text_content = " ".join(text_content)

        # tokenize the text content

        # token_list: list[str] =self.tokenizer.tokenize(text_content)

        # return the stopword free token_list
        # return [self.lemmatizer.lemmatize(token) for token in token_list if token not in self.stopwords]

    def extract_tokens(self) -> Generator[tuple[str, TokenInformation], None, None]:
        # from go through each folder in self.folders
        for folder_path in self.folders:
            # go through each file in the current folder
            for filename in os.listdir(folder_path):
                # for each file in the current folder, find the path to the current file
                file_path = os.path.join(folder_path, filename)
                # create the html pages so we can convert it to str
                folder_name = os.path.basename(folder_path)
                file_name = os.path.basename(file_path)
                doc_id = folder_name + "/" + file_name
                logger.info(f"Parsing file: {doc_id}")
                page = html.parse(file_path)
                # convert page into str: html_content
                page_token_information = self.tokenize_page(page)
                # Get the folder name and the file name
                yield doc_id, page_token_information
