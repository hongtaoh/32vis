# download python
sudo apt-get install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install python3.8

# download and install pip
sudo apt-get update
sudo apt install python3-pip 

# install packages
pip install pandas numpy matplotlib seaborn 

# run script that generates the figure
python3 get_figure.py