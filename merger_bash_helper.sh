DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
MERGER_PATH=$DIR/merger.py
cp $MERGER_PATH /usr/local/bin/
touch ~/.bash_profile
echo "alias mergetool='python3 /usr/local/bin/merger.py'" >>  ~/.bash_profile
source ~/.bash_profile