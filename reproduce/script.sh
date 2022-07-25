# download and install pip
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py

# install packages
pip install pandas numpy matplitlib seaborn altair scikit-learn scipy plotnine beautifulsoup4 selenium urllib3 requests

# run script that generates the figure
python3 get_figure.py