import io
import json
import os
import zipfile
import requests
import pandas as pd
from io import StringIO

os.makedirs("data", exist_ok=True)

URL = "https://epawebapp.epa.ie/Hydronet/output/internet/stations/CAS/33008/S/3_months.zip"

response = requests.get(URL, timeout=60)
response.raise_for_status()

z = zipfile.ZipFile(io.BytesIO(response.content))

csv_file = [n for n in z.namelist() if n.endswith(".csv")][0]

lines = z.read(csv_file).decode("utf-8").splitlines()

rows = [
    l for l in lines
    if not l.startswith("#")
    and l.strip()
]

df = pd.read_csv(
    StringIO("\n".join(rows)),
    sep=";",
    header=None,
    names=["timestamp", "value", "absolute", "quality"]
)

out = {
    "rows": [
        {
            "timestamp": str(r["timestamp"]),
            "absolute": float(r["absolute"])
        }
        for _, r in df.iterrows()
    ]
}

with open("data/latest.json", "w") as f:
    json.dump(out, f)

print("Updated", len(df), "rows")
