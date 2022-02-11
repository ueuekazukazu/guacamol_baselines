#!/bin/bash -x

build_directory=$1

cd $build_directory

# checking if wget is installed
if which wget >/dev/null; then
    wget https://ndownloader.figshare.com/files/13612745 -O guacamol_v1_all.smiles
    wget https://ndownloader.figshare.com/files/13612760 -O guacamol_v1_train.smiles
    wget https://ndownloader.figshare.com/files/13612766 -O guacamol_v1_valid.smiles
    wget https://ndownloader.figshare.com/files/13612757 -O guacamol_v1_test.smiles

# if wget is not found then use curl to download guacamol smiles
else
    curl -L  https://ndownloader.figshare.com/files/13612745 -o guacamol_v1_all.smiles
    curl -L  https://ndownloader.figshare.com/files/13612760 -o guacamol_v1_train.smiles
    curl -L  https://ndownloader.figshare.com/files/13612766 -o guacamol_v1_valid.smiles
    curl -L  https://ndownloader.figshare.com/files/13612757 -o guacamol_v1_test.smiles
fi