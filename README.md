#Setup

1. Install gcloud cli
## For Eva:
  - Run this command: 
````
curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-linux-x86_64.tar.gz
````

  - Extract the contents of the tar file.
````
tar -xf google-cloud-cli-linux-x86_64.tar.gz
````
  - Run the installation script from the root of the folder(if you didn't move it, that's just Downloads)
````
./google-cloud-sdk/install.sh
````

2. Authenticate 
- Login with your Google account (opens browser)
````
gcloud auth login
````
- Set up application default credentials
````
gcloud auth application-default login
````

- Set the project 
````
gcloud auth application-default set-quota-project intense-pointer-486415-i3
````