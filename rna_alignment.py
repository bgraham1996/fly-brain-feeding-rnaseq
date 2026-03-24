import subprocess
from pathlib import Path

# server mounts
SERVER_MOUNT = Path.home()
PROJECT_DIR = SERVER_MOUNT / "drosophila_brain_rna_seq_data_1"
SRA_DIR = PROJECT_DIR / "sra_files"
FASTQ_DIR = PROJECT_DIR / "fastq_files"
TRIMD_DIR = PROJECT_DIR / "trimmed_fastq"
REPORT_DIR = PROJECT_DIR / "reports"
REPORT_DIR = REPORT_DIR / 'trimming'

fastq_files = sorted(TRIMD_DIR.glob("*1.fastq.gz"))
fastq_files = [f for f in fastq_files if not f.name.startswith('._')]

for file in fastq_files:
    r2_file = file.name.replace('_1', '_2')
    r2_file = TRIMD_DIR/r2_file
    run_id = file.name.replace('_trimmed_1.fastq.gz', '')

    print(f' ============= Aligning {run_id} =========== ')
    subprocess.run([
        'STAR',
        '--genomeDir', str(PROJECT_DIR / 'genome_index'),
        '--readFilesIn', str(file), str(r2_file),
        '--readFilesCommand', 'zcat',
        '--outSAMtype', 'BAM', 'SortedByCoordinate',
        '--runThreadN', '8',
        '--outFileNamePrefix', str(PROJECT_DIR) + '/bam_files/' + run_id + '_'
    ])

print(' ========= Aligning Finished ===========')

