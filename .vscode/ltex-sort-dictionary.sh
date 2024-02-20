#!/bin/sh
sed 's/_/!/g' .vscode/ltex.dictionary.en-US.txt > .git/ltex.dictionary.en-US.txt
LC_COLLATE=C sort -fu .git/ltex.dictionary.en-US.txt >.vscode/ltex.dictionary.en-US.txt
sed -i 's/!/_/g' .vscode/ltex.dictionary.en-US.txt .git/ltex.dictionary.en-US.txt
diff -u .git/ltex.dictionary.en-US.txt .vscode/ltex.dictionary.en-US.txt &&
     rm .git/ltex.dictionary.en-US.txt
