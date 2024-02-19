import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import pandas as pd
import openpyxl
import streamlit as st

if "initial_submit" not in st.session_state:
    st.session_state.initial_submit = False

def initial_submit():
    st.session_state.initial_submit = True

def hill_function(x, Vmax, Kd, n):
    try:
        return (Vmax * x**n) / (Kd**n + x**n)
    except:
        return 0

def transform(series, i, j):
    adstock = j
    lag = i
    series = series.to_list()
    if lag != 0:
        series = [0 for _ in range(lag)] + series[:-lag]
    series = np.array(series)
    if adstock != 0:
        for k in range(len(series) - 1):
            series[k+1] = series[k+1] + (series[k] * adstock)
    return series

st.write("Insert data in this format -")
st.dataframe(pd.DataFrame({"X Spends" : [12, 21], "X Sales" : [23, 32]}))

file = st.file_uploader(label = "Enter your file -", accept_multiple_files = False, type = ["csv", "xlsx"])

df = pd.DataFrame()
if file:
    if file.type == "csv":
        df = pd.read_csv(file)
    else:
        wb = openpyxl.load_workbook(file)
        sheet_name = st.selectbox(label = "Select your sheet -", options = wb.sheetnames)
        df = pd.read_excel(file, sheet_name = sheet_name)

if not df.empty:
    prefixes = set()
    for col in df.columns:
        if ' Spends' in col:
            prefix = col.split(' Spends')[0]
            if prefix + ' Sales' in df.columns:
                prefixes.add(prefix)

    hyper_params = {}

    with st.expander("Initial Submit", expanded = True):
        columns = st.multiselect("Select your columns -", options = prefixes)
        for i in columns:
            hyper_params[i] = [0, 0]
            col1, col2, col3 = st.columns([3, 2, 2])
            with col1:
                st.write(i)
            with col2:
                hyper_params[i][0] = st.number_input(label = "Lag", min_value = 0, value = 0, max_value = 12, key = f"{i}_0")
            with col3:
                hyper_params[i][1] = st.number_input(label = "Adstock in 0. format", min_value = 0., value = 0., max_value = 1., key = f"{i}_1")
        submit = st.button("Submit Transformation Parameters", on_click = initial_submit)

if st.session_state.initial_submit:
    for j in columns:
        spends_arr = transform(df[f"{j} Spends"], hyper_params[j][0], hyper_params[j][1])
        sales_arr = df[f"{j} Spends"].to_numpy()

        initial_guess = [100.0, 25.0, 1.0]

        popt, _ = curve_fit(hill_function, spends_arr, sales_arr, p0 = initial_guess, maxfev = 1000000000)

        fig, ax = plt.subplots()

        ax.scatter(spends_arr, sales_arr, label = 'Data')

        x_fit = np.linspace(0, max(spends_arr), 100)
        y_fit = hill_function(x_fit, *popt)
        ax.plot(x_fit, y_fit, 'r-', label = 'Fit: Vmax = %5.3f, Kd = %5.3f, n = %5.3f' % tuple(popt))

        ax.set_xlabel('Spends')
        ax.set_ylabel('Sales')
        ax.set_title(j)
        ax.legend()
        st.pyplot(fig)