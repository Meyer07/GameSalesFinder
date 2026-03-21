set -e

apt-get update
apt-get install -y chromium-driver
pip install -r requirements.txt