# %%
import json

raw: str = ""
for i in range(1, 4):
    with open(f"response{i}.json") as f:
        data = json.load(f)
        raw += data["document"]["text"]

# %%
with open("ubf-raw.csv", "w") as f:
    for line in raw.splitlines():
        index_entry = line.split(".", maxsplit=1)
        page = index_entry[0].strip("_ ")
        try:
            song = index_entry[1].strip(". ")
        except IndexError:
            song = ""
        f.write(f'{page},"{song}"\n')
# %%
