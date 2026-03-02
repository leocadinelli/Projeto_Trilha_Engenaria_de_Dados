# install azure-storage-blob and install azure-identity required for connection with Azure Blob Storage
#### pip install azure-storage-blob 
#### pip install azure-identity

import ssl
import requests
import json 
import pandas as pd
import os

# importing the classes for the file
from azure.identity import ClientSecretCredential 
from azure.storage.blob import BlobClient


# Connection variables

# blob path
ACCOUNT_URL = "https://stfasttracksdev.blob.core.windows.net"
# name of container 
CONTAINER_NAME = "source-jira"
# file targert name
BLOB_NAME = "jira_issues_raw.json"
# Azure Directory ID
TENANT_ID = '3a9dcec2-1c28-49ec-8891-064f23836607' 
# App Azure ID 
CLIENT_ID = 'e1985a41-68e9-4a12-8930-aca413148cf2' 
# Secret Key for Azure
CLIENT_SECRET= os.getenv(CLIENT_SECRET)                         
# Json file name
OUTPUT_JSON   = "bronze_issues.json"


# Starting the connection setup

# Authentication
credential = ClientSecretCredential( 
    tenant_id=TENANT_ID,
    client_id = CLIENT_ID,
    client_secret = CLIENT_SECRET
      )


# Connection with the blob client
blob_cliente = BlobClient(
     account_url=ACCOUNT_URL,
     container_name=CONTAINER_NAME,
     blob_name=BLOB_NAME,
     credential=credential
     )

stream = blob_cliente.download_blob()
dadosRAW = stream.readall()


with open(OUTPUT_JSON, "wb") as f:
     f.write(dadosRAW)

print("Tudo certo!")
