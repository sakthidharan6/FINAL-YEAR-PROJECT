import sys
import os
import traceback

print(f"CWD: {os.getcwd()}")
print(f"Path: {sys.path}")


try:
    print("Importing pandas...")
    import pandas
    print("Importing numpy...")
    import numpy
    print("Importing tensorflow...")
    import tensorflow
    print("Importing yfinance...")
    import yfinance
    print("Importing fastapi...")
    from fastapi import FastAPI
    print("Importing backend.main...")
    import backend.main
    print("Successfully imported backend.main")
except Exception as e:
    print("Falied during imports")
    traceback.print_exc()

