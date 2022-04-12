import os.path

import streamlit as st
import pandas as pd
from ecommercetools import seo


class EvaluationInterface:
    def __init__(self):
        pass

    @staticmethod
    # @st.cache(allow_output_mutation=True)
    def search_input():
        with st.form(key='input_form'):
            name = st.sidebar.text_input('Enter Name of the critique: ')
            query = st.sidebar.text_input('Enter Query: ')
            num_ret = st.sidebar.number_input("Enter number of retrieved docs to analyze: ", 0, 25, 5, 1, key=100)

            search_button = st.sidebar.button("Search")

        return name, query, num_ret, search_button

    @staticmethod
    @st.cache(show_spinner=False)
    def search(name, query, num_ret):
        info = seo.get_serps(query, pages=5)
        selected = info.sample(n=num_ret)
        selected['Author'] = name
        selected['Query'] = query
        st.session_state.count = 0
        # st.session_state.result_list = list()
        st.session_state.save_result = pd.DataFrame()
        selected.to_csv('temp_search_results.csv')

    @staticmethod
    def retrieve():
        return pd.read_csv('temp_search_results.csv', index_col=0)

        #     return name, query, selected
        # else:
        #     return None, None, None

    @staticmethod
    def page(selected):
        last_page = len(selected) - 1

        if 'count' not in st.session_state:
            st.session_state.count = 0

        prev, pg, next = st.columns([1, 2, 1])

        # with st.form(key='page_form'):
        # print("Page: ", st.session_state.count)
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
            # st.form_submit_button()

        st.title("Page: " + str(st.session_state.count + 1))

        return selected.iloc[st.session_state.count, :]

    # @staticmethod
    # def annotate(name, query, selected):
    #     result_list = list()
    #
    #     if selected is not None:
    #         for idx, row in selected.iterrows():
    #             result_row = list()
    #             st.text("Search Engine Rank: " + str(row['position']))
    #             st.text("Document Title: " + row['title'])
    #             st.text("Document Link: " + row['link'])
    #             st.text("Document Summary: " + row['text'])
    #             st.text("Document Tag: " + row['bold'])
    #
    #             type = st.radio(
    #                 "Select the type of article: ",
    #                 ('Positive', 'Negative'), key=idx)
    #
    #             result_row.append(type)
    #
    #             # col1, col2 = st.columns([1, 1])
    #             #
    #             # with col1:
    #             #     pos = st.button('Positive')
    #             #     result_row.append('Positive')
    #             # with col2:
    #             #     neg = st.button('Negative')
    #             #     result_row.append('Negative')
    #
    #             comment = st.text_input('Enter Comments: ', key=idx * 3)
    #             result_row.append(comment)
    #             score = st.number_input("Enter relevance score (0-Irrelevant, 1-Moderately Relevant, 2-Relevant): ",
    #                                     0, 2, 2, 1, key=idx * 5)
    #             result_row.append(score)
    #
    #             # if st.button('Next'):
    #             result_list.append(result_row)
    #             # continue
    #
    #         selected['Author'] = name
    #         selected['Query'] = query
    #
    #         selected = pd.concat(
    #             [selected, pd.DataFrame(result_list, columns=['Context Class', 'Comments', 'Score'])],
    #             axis=1, ignore_index=True)
    #
    #         if os.path.isfile("results.csv"):
    #             results = pd.read_csv("results.csv", index_col=0)
    #             results = pd.concat([results, selected], axis=0, ignore_index=True)
    #             results.to_csv('results.csv')
    #         else:
    #             selected.to_csv('results.csv')
    #     else:
    #         st.text("No Results Found")

    @staticmethod
    def annotate(selected):

        if selected is not None:

            idx = selected.index

            result_row = list()
            st.text("Search Engine Rank: " + str(selected['position']))
            st.text("Document Title: " + selected['title'])
            link = 'Document Link: [{link}]({link})'.format(link=selected['link'])
            st.write(link, unsafe_allow_html=True)
            # st.text("Document Link: " + selected['link'])
            st.text("Document Summary: " + selected['text'])
            st.text("Document Tag: " + selected['bold'])

            with st.form(key='entry_form'):
                type = st.radio(
                    "Select the type of article: ",
                    ('Positive', 'Negative'), key=idx)

                result_row.append(type)

                comment = st.text_input('Enter Comments: ', key=idx * 3)
                result_row.append(comment)
                score = st.number_input("Enter relevance score (0-Irrelevant, 1-Moderately Relevant, 2-Relevant): ",
                                        0, 2, 1, 1, key=idx * 5)
                result_row.append(score)

                sub_ent = st.form_submit_button('Submit Entry')

                if sub_ent:
                    temp = selected.to_frame().T.reset_index(drop=True)
                    temp_res = pd.DataFrame([result_row], columns=['Context Class', 'Comments', 'Score'])
                    temp_df = pd.merge(temp,
                                       temp_res,
                                       left_index=True,
                                       right_index=True
                                       )
                    st.session_state.save_result = pd.concat([st.session_state.save_result, temp_df], axis=0,
                                                             ignore_index=True)

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
    name, query, num_ret, ser_but = ui.search_input()
    # print("Query####", query)
    if ser_but:
        # print("Searching...")
        with st.spinner(text="Searching..."):
            ui.search(name, query, num_ret)

    selected = ui.retrieve()
    # print(selected)
    if selected is not None:
        row = ui.page(selected)
        ui.annotate(row)
