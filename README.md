### Network Security Projects For Phising Data

Setup github secrets:
AWS_ACCESS_KEY_ID=

AWS_SECRET_ACCESS_KEY=

AWS_REGION = us-east-1

AWS_ECR_LOGIN_URI = 788614365622.dkr.ecr.us-east-1.amazonaws.com/networkssecurity
ECR_REPOSITORY_NAME = networkssecurity

Setup local `.env`:
MONGODB_URI=
TRAINING_BUCKET_NAME=networksecurity2

DAGSHUB_BASE_URL=https://dagshub.com
DAGSHUB_REPO_OWNER=Brunobs13
DAGSHUB_REPO_NAME=networksecurity
DAGSHUB_USER=
DAGSHUB_TOKEN=

MLFLOW_TRACKING_URI=
MLFLOW_TRACKING_USERNAME=
MLFLOW_TRACKING_PASSWORD=

DVC setup (no hardcoded credentials):
chmod +x setup_dvc.sh
./setup_dvc.sh

Training entrypoint:
python pipeline/training_pipeline.py


Docker Setup In EC2 commands to be Executed
#optinal

sudo apt-get update -y

sudo apt-get upgrade

#required

curl -fsSL https://get.docker.com -o get-docker.sh

sudo sh get-docker.sh

sudo usermod -aG docker ubuntu

newgrp docker
