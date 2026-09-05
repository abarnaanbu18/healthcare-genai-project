# data.py
import pandas as pd

def load_patients():
    return pd.read_csv("synthetic_patients.csv")
