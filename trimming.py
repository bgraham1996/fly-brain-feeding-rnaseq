

import subprocess
from pathlib import Path
from datetime import datetime as dt

id = str(dt.now())

# server mounts
SERVER_MOUNT = Path.home()
PROJECT_DIR = SERVER_MOUNT / "drosophila_brain_rna_seq_data_1"
SRA_DIR = PROJECT_DIR / "sra_files"
FASTQ_DIR = PROJECT_DIR / "fastq_files"
TRIMD_DIR = PROJECT_DIR / "trimmed_fastq"
REPORT_DIR = PROJECT_DIR / "reports"
REPORT_DIR = REPORT_DIR / 'trimming'

fastq_files = sorted(FASTQ_DIR.glob("*1.fastq.gz"))
fastq_files = [f for f in fastq_files if not f.name.startswith('._')]

for file in fastq_files:
    r2_file = file.name.replace('_1', '_2')
    r2_file = FASTQ_DIR/r2_file
    run_id = file.name.replace('_1.fastq.gz', '')
    o1 = run_id + '_trimmed_1.fastq'
    o2 = run_id + '_trimmed_2.fastq'
    print(f' ============= Trimming {run_id} =========== ')
    subprocess.run([
        'fastp',
        '-i', str(file), '-I', str(r2_file),
        '-o', str(TRIMD_DIR/o1), '-O', str(TRIMD_DIR/o2),
        '--length_required', '36',
        '-q', '20',
        '-h', str(REPORT_DIR / 'html') + '/' + run_id + '.html',
        '-j', str(REPORT_DIR / 'json') + '/' + run_id + '.json'
    ])

report_output = str(REPORT_DIR / 'json') + '/'
subprocess.run(['multiqc', report_output, '-o', (str(REPORT_DIR / 'multiqc') + '/')])
