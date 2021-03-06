# %%
import json
import re

from typing import NamedTuple, List, Optional


# %%
def fix_capital_i(input: str) -> str:
    """Replace []|1 with I"""
    return re.sub(r"[\[\]\|1]", "I", input)


assert fix_capital_i("] am |n Pain") == "I am In Pain"


# %%
def short_string(input: str) -> bool:
    """
    String is two characters or less and not a number.
    """
    if len(input) < 3:
        try:
            int(input)
        except ValueError:
            # String is not a number
            return True
    return False


assert short_string("Q") is True
assert short_string("a6") is True
assert short_string("Cool") is False
assert short_string("43") is False


def is_noise(page: str) -> bool:
    """Determine if this page entry is noise"""
    if "Sök" in page:
        # From iPad screenshot, not part of index
        return True
    if page in ("INDEX OF SONGS", "1"):
        return True
    if short_string(page):
        return True
    return False


assert is_noise("A6") is True
assert is_noise("INDEX OF SONGS") is True
assert is_noise("A Smile") is False
assert is_noise("322") is False
assert is_noise("Sök the") is True
assert is_noise("1") is True


# %%
class IndexEntry(NamedTuple):
    page: int
    song: str


raw: str = ""
for file in ("response1.json", "response2.json", "response3.json"):
    with open(file) as f:
        data = json.load(f)
        raw += data["document"]["text"]

index_entries: List[Optional[IndexEntry]] = []
for i, line in enumerate(raw.splitlines()):
    # ex. "257..Ace In The Hole"
    index_line = line.split(".", maxsplit=1)
    # page = '257'
    page = index_line[0].strip("_ ")
    if is_noise(page):
        index_entries.append(None)
        continue
    try:
        # ex. ".Ace In The Hole"
        song = index_line[1].strip(". ")
        song = fix_capital_i(song)
    except IndexError:
        # Previous song title was too long to fit on one line
        # Text overflows to "page" field on this line and there is no "song" field
        # "song" has a value from previous iteration that is the beginning of a long song title
        song = song + " " + page
        page = index_entries[i - 1].page
        index_entries[i - 1] = None

    ie = IndexEntry(int(page), song)
    index_entries.append(ie)

# %%
with open("ubf-raw.csv", "w") as f:
    for index_entry in (x for x in index_entries if x is not None and x.song != ""):
        f.write(f'{index_entry.page},"{index_entry.song}"\n')
# %%
