# %%
# Imports #

# Vendored/trimmed from dotfiles src/config.py — keeps the same path variables the
# moved jobs import, drops the directories only the dotfiles stack used
# (templates/, logs/, download caches).

import os
import sys
from os.path import expanduser

home_dir = expanduser("~")
file_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
grandparent_dir = os.path.dirname(parent_dir)

data_dir = os.path.join(parent_dir, "data")
data_dir_archive = os.path.join(parent_dir, "data", "archive")
src_dir = os.path.join(parent_dir, "src")
src_utils_dir = os.path.join(src_dir, "utils")

directories = [
    data_dir,
    data_dir_archive,
    src_dir,
    src_utils_dir,
]
for directory in directories:
    if not os.path.exists(directory):
        print(f"Creating directory: {directory}")
        os.makedirs(directory)

sys.path.append(file_dir)
sys.path.append(parent_dir)
sys.path.append(grandparent_dir)
sys.path.append(src_dir)
sys.path.append(src_utils_dir)

if __name__ == "__main__":
    print(f"home_dir: {home_dir}")
    print(f"file_dir: {file_dir}")
    print(f"parent_dir: {parent_dir}")
    print(f"grandparent_dir: {grandparent_dir}")
    print(f"data_dir: {data_dir}")


# %%
