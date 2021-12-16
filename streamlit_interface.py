import streamlit as st
import pandas as pd


class UI:
    def __init__(self):
        pass

    @staticmethod
    def build_interface():
        split_list = list()
        num_ppl = st.number_input("Enter number of people in the house: ", 0, 10, 7, 1, key=100)
        cost = st.number_input("Electricity Bill Amount: ", step=1., format="%.2f", key=101)
        month = st.sidebar.selectbox('Select an Option: ',
                                     ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
                                      'September', 'October', 'November', 'December'])

        range_max = 30 if month in ['April', 'June', 'September', 'November', 'December'] else 31
        range_max = 28 if month == 'February' else range_max

        for i in range(num_ppl):
            name = st.text_input('Name: ', key=i)
            num_days = st.number_input("Enter number of Days not present in the billing cycle: ", 0, range_max, 0,
                                       key=i)

            split_list.append((range_max - num_days, name))

        return split_list, cost / range_max

    @staticmethod
    def display(df):
        st.write("Per Share!")
        st.dataframe(df)


if __name__ == '__main__':
    ui = UI()
    ui.build_interface()
