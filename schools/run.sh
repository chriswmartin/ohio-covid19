#!/bin/bash

echo "<pre><code>" > index.html
python3 schools.py >> index.html
echo "</pre></code>" >> index.html
