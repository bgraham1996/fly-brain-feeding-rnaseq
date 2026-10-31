"""
    this file will be used to retrive RNA seq data


"""

import pandas as pd
import csv
import os
from dotenv import load_dotenv
from Bio import Entrez
from datetime import datetime as dt
from io import StringIO
import subprocess
import sys
from pathlib import Path
import time

# loading env variables
load_dotenv()
email = os.getenv('Email')

# setting up variables
Entrez.email = email
timestamp = str(dt.now())

# server mounts
SERVER_MOUNT = Path.home() / "server" 
PROJECT_DIR = SERVER_MOUNT / "drosophila_brain_rna_seq_data_1"
SRA_DIR = PROJECT_DIR / "sra_files"
FASTQ_DIR = PROJECT_DIR / "fastq_files"

# checking server connection
if SERVER_MOUNT.exists() != True:
    print("Server not mounted, stopping script")
    sys.exit()

# searching for SRA entries:
handle = Entrez.esearch(db="sra", term="PRJNA1132369", retmax=1000)
record = Entrez.read(handle)
sra_reads = record["IdList"]
handle.close()

handle = Entrez.efetch(db='sra', id=sra_reads, rettype='runinfo', retmode='text')
run_info = handle.read()
if isinstance(run_info, bytes):
    run_info = run_info.decode('utf-8')
df = pd.read_csv(StringIO(run_info))
"""print(df.columns.tolist())"""
df.to_csv(f'runinfo_{timestamp}.csv')

# get a list of the file paths and download the files
fastq_urls = df['Run'].to_list()
error_log = pd.DataFrame(columns=['sra', 'error'])
for fastq in fastq_urls:
    print(f"Downloading {fastq}...")
    try:
        if (FASTQ_DIR / f"{fastq}_1.fastq").exists():
            print(f'{fastq} already processed')
        else:
            subprocess.run(['prefetch', fastq, '--output-directory', str(SRA_DIR)], check=True)
            #convert files to fastq
            subprocess.run([
                'fasterq-dump',
                fastq,
                '--outdir', str(FASTQ_DIR),
                '--threads', '4',
                '--progress'
            ], check=True)
            time.sleep(15)

    except Exception as e:
        error_log.loc[len(error_log)] = [fastq, e]

if len(error_log) > 0:
    error_log.to_csv(f'download_report_{timestamp}.csv')
else:
    print("All files downloaded and processed")
