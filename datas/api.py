import pandas as pd


def get_std_2566():
    df = pd.read_json("https://gpa.obec.go.th/reportdata/pp3-4_2566_province.json")
    df = df.sort_values(by=["totalstd"], ascending=False)
    return df
