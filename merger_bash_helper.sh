rm -rf /usr/local/bin/mergetool
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cp -rf $DIR /usr/local/bin/
mv /usr/local/bin/prototype /usr/local/bin/mergetool
touch ~/.bash_profile
echo "alias mergetool='python3 /usr/local/bin/mergetool/merger.py'" >>  ~/.bash_profile
source ~/.bash_profile
