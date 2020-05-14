#!/bin/bash
path=$(pwd);

echo "Converting images..."

for entry in $(find $path -name '*png'); do
    convert -strip $entry $entry;
done

echo "Finished."
