import pandas as pd
from ecommercetools import seo
import numpy as np

if __name__ == '__main__':
    TopicAvgPrecisionList = []

    eval_set = pd.read_excel("eval_set.xlsx")
    query_list = eval_set['Query'].tolist()
    qrels = eval_set[['Query', 'link', 'Context Class', 'Relevance Score']].tolist()

    # Iterating all the queries given in the evaluation set topics
    for queryTopic in query_list:
        # Storing the docId and score for the documents in the query as a list
        search_results = seo.get_serps(queryTopic, pages=5)
        rankList_For_Query = search_results['link']

        # Getting the relevant documents for the Query - Fetched from the evaluation set list
        relavent_doc = []
        for qr in qrels:
            # If the list has the documents with current query and if the reeevent score field is 1 =>
            # They are relevant documents for the query based on user relevance
            if (qr[0] == queryTopic and qr[3] == 1):
                relavent_doc.append(qr[2])

        # If relevant documents are not present we add 0 to list - Foud a document with no relevant document
        # So to handle it we use the following method.
        if (len(relavent_doc) == 0):
            TopicAvgPrecisionList.append(0)
        else:

            # If relevant documents are present :
            # We iterate over the list of ranked test documents rankList_For_Query
            count = 1
            i = 0
            query_rel_rank = []
            totPrecision = 0
            for docList in rankList_For_Query:
                # If we find the relevant document, we add the relvant count index i
                # We add the precision to totPrecision
                if (docList[0] in relavent_doc):
                    i = i + 1
                    totPrecision = totPrecision + (i / float(count))
                # If we found all the relevant documents, no need to iterate further.
                if (i == len(relavent_doc)):
                    break

                query_rel_rank.append(i / float(count))
                count = count + 1
            TopicAvgPrecisionList.append(totPrecision / len(relavent_doc))

    totavgPrec = 0
    for avgPrec in TopicAvgPrecisionList:
        totavgPrec = totavgPrec + avgPrec

    print("Sum of all Average Precision: ", totavgPrec)
    map_50 = totavgPrec / len(TopicAvgPrecisionList)
    print("MAP@50 for the list of query_topics : ", map_50)
