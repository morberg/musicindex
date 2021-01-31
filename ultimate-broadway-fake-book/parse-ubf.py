# %%
import json

raw: str = ""
for i in range(1, 4):
    with open(f"response{i}.json") as f:
        data = json.load(f)
        raw += data["document"]["text"]

# %%
songs = []
with open("ubf-raw.csv", "w") as f:
    for line in raw.split("\n"):
        song = line.split(".")
        # page, "song title"
        f.write(f"{song[0]},\"{' '.join(song[1:])}\"\n")
