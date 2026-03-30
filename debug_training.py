import sys
import os

def check_env():
    print(f"Python Version: {sys.version}")
    print(f"Current Directory: {os.getcwd()}")
    
    try:
        import pandas as pd
        print(f"Pandas Version: {pd.__version__}")
    except ImportError:
        print("ERROR: Pandas not installed.")

    try:
        import numpy as np
        print(f"Numpy Version: {np.__version__}")
    except ImportError:
        print("ERROR: Numpy not installed.")

    try:
        import sklearn
        print(f"Scikit-learn Version: {sklearn.__version__}")
    except ImportError:
        print("ERROR: Scikit-learn not installed.")

    try:
        import tensorflow as tf
        print(f"TensorFlow Version: {tf.__version__}")
        print(f"Keras Version: {tf.keras.__version__}")
    except ImportError:
        print("ERROR: TensorFlow not installed.")
    except AttributeError:
        print("TensorFlow installed but Keras version lookup failed.")

    try:
        import yfinance as yf
        print(f"yfinance Version: {yf.__version__}")
        test = yf.Ticker("BBCA.JK").history(period="5d")
        if test.empty:
            print("ERROR: yfinance returned empty data for BBCA.JK.")
        else:
            print("yfinance data fetch: OK")
    except Exception as e:
        print(f"ERROR: yfinance check failed: {e}")

if __name__ == "__main__":
    check_env()
