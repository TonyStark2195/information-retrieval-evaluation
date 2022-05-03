import os.path

import streamlit as st
import pandas as pd
from ecommercetools import seo


class EvaluationInterface:
    """
    Class for data annotater streamlit app.
    """

    def __init__(self):
        pass

    @staticmethod
    def search_input():
        """
        Method for getting the initial form input in the sidebar nav.
        :return: @name - Name of the user
                @query - Query entered
                @num_ret - Number of docs to be retrieved
                @search_button - Search button status (Pressed or not)
        """
        with st.form(key='input_form'):
            name = st.sidebar.text_input('Enter Name of the critique: ')
            query = st.sidebar.text_input('Enter Query: ')
            num_ret = st.sidebar.number_input("Enter number of retrieved docs to analyze: ", 0, 50, 5, 1, key=100)

            search_button = st.sidebar.button("Search")

        return name, query, num_ret, search_button

    @staticmethod
    @st.cache(show_spinner=False)
    def search(name, query, num_ret):
        """
        Method for performing the search and retrieval, from the Google api.
        Saves the retrieved results in a temporary csv file.
        This is a cached method, meaning it will not be rerun every time, until the search button is pressed.
        """
        info = seo.get_serps(query, pages=5)
        # selected = info.sample(n=num_ret)
        selected = info.copy()
        selected['Author'] = name
        selected['Query'] = query
        st.session_state.count = 0
        st.session_state.save_result = pd.DataFrame()
        selected.to_csv('temp_search_results.csv')

    @staticmethod
    def retrieve():
        """
        Method for reading the saved temporary saved results.
        """
        if os.path.isfile('temp_search_results.csv'):
            return pd.read_csv('temp_search_results.csv', index_col=0)

    @staticmethod
    def page(selected):
        """
        Method for page navigation.
        :input: The whole retrieved dataframe
        :return:The selected entry (row) from the dataframe based on page number
        """
        last_page = len(selected) - 1

        if 'count' not in st.session_state:
            st.session_state.count = 0

        prev, pg, next = st.columns([1, 2, 1])

        if next.button("Next"):

            if st.session_state.count + 1 > last_page:
                st.session_state.count = 0
            else:
                st.session_state.count += 1

        if prev.button("Previous"):

            if st.session_state.count - 1 < 0:
                st.session_state.count = last_page
            else:
                st.session_state.count -= 1

        st.title("Page: " + str(st.session_state.count + 1))

        return selected.iloc[st.session_state.count, :]

    @staticmethod
    def annotate(selected):
        """
        Method for controlling the interface and responses.
        Form based design to handle inputs from the user.
        """

        if selected is not None:

            idx = selected.index

            result_row = list()

            # Display the retrieved page and it's properties
            st.text("Search Engine Rank: " + str(selected['position']))
            st.text("Document Title: " + selected['title'])
            link = 'Document Link: [{link}]({link})'.format(link=selected['link'])
            st.write(link, unsafe_allow_html=True)
            st.text("Document Summary: " + str(selected['text']))
            st.text("Document Tag: " + str(selected['bold']))

            # Form to handle annotations from the user
            with st.form(key='entry_form'):
                article_type = st.radio(
                    "Select the type of article: ",
                    ('Positive', 'Negative'), key=idx)

                result_row.append(article_type)

                comment = st.text_input('Enter Comments: ', key=idx * 3)
                result_row.append(comment)
                # score = st.number_input("Enter relevance score (0-Irrelevant, 1-Moderately Relevant, 2-Relevant): ",
                #                         0, 2, 1, 1, key=idx * 5)

                score = st.number_input("Enter relevance score (0-Irrelevant, 1-Relevant): ",
                                        0, 1, 1, 1, key=idx * 5)
                result_row.append(score)

                sub_ent = st.form_submit_button('Submit Entry')

                # Button to add the inputs from user to the queue that saves to file
                if sub_ent:
                    temp = selected.to_frame().T.reset_index(drop=True)
                    temp_res = pd.DataFrame([result_row], columns=['Context Class', 'Comments', 'Relevance Score'])
                    temp_df = pd.merge(
                        temp,
                        temp_res,
                        left_index=True,
                        right_index=True
                    )
                    st.session_state.save_result = pd.concat([st.session_state.save_result, temp_df], axis=0,
                                                             ignore_index=True)

            # Button to save all the annotations to a csv file
            if st.button('Save Annotations'):
                if os.path.isfile("results.csv"):
                    results = pd.read_csv("results.csv", index_col=0)
                    results = pd.concat([results, st.session_state.save_result], axis=0, ignore_index=True)
                    results.to_csv('results.csv')
                else:
                    st.session_state.save_result.to_csv('results.csv')
        else:
            st.text("No Results Found")


if __name__ == '__main__':
    ui = EvaluationInterface()
    au_name, inp_query, num_docs, ser_but = ui.search_input()

    if ser_but:
        with st.spinner(text="Searching..."):
            ui.search(au_name, inp_query, num_docs)

    retrieved_docs = ui.retrieve()

    if retrieved_docs is not None:
        row = ui.page(retrieved_docs)
        ui.annotate(row)
