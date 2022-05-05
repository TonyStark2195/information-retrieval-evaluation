import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize, sent_tokenize

import collections
import pandas as pd
import numpy as np


class DocumentSummarizer:
    def __init__(self):
        self.stop_words = set(stopwords.words("english"))
        self.porter = PorterStemmer()
        self.sentence_score = dict()

    def word_frequency(self, text):
        """
        To calculate the frequency of each word in the text sentence.
        """
        words = word_tokenize(text)

        stemmed = list(map(self.porter.stem, words))
        stop_present = self.stop_words.intersection(stemmed)

        frequency = collections.Counter(stemmed)

        for stops in stop_present:
            frequency.pop(stops)

        return frequency

    def score_sentence(self, sentences, frequency):
        """
        To split the sentences into words and get the score of each sentence by their word frequency.
        """

        for sentence in sentences:

            sent_words = word_tokenize(sentence)
            stemmed_sent_words = list(map(self.porter.stem, sent_words))

            sentence_word_len = len(stemmed_sent_words)

            for word in stemmed_sent_words:
                self.sentence_score[sentence] += frequency.get(word, 0)

            self.sentence_score[sentence] /= sentence_word_len

        return self.sentence_score

    def get_threshold(self):
        """
        Get the median score as the threshold.
        """

        sorted_list = sorted(list(self.sentence_score.values()))
        median = sorted_list[len(sorted_list) // 2]

        return median

    def summarize(self, text, threshold=1.0):
        """
        This module is used to summarize the huge text into a smaller brief
        summary using just the score of the sentences.
        """

        sentences = sent_tokenize(text)
        freq_words = self.word_frequency(text)
        scored_sentences = self.score_sentence(sentences, freq_words)
        median = self.get_threshold()

        summary = list()

        for sentence in sentences:
            if scored_sentences[sentence] >= threshold * median:
                summary.append(sentence)

        return " ".join(summary)


if __name__ == '__main__':
    docSummary = DocumentSummarizer()
    search_results = pd.read_csv('search_engine_results_content.csv', index_col=0)
    summary_result = list()
    for result in search_results['text'].tolist():
        summary_result.append(docSummary.summarize(result, 1.2))
