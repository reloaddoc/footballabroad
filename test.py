import pandas as pd

with open("output/opta_rankings.csv", "r", encoding="utf-8-sig") as f:
    for i in range(5):
        print(repr(f.readline()))
