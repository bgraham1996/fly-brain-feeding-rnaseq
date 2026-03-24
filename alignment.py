
from pathlib import Path
import subprocess

"""server mounts"""
SERVER_MOUNT = Path.home()
PROJECT_DIR = SERVER_MOUNT / "drosophila_brain_rna_seq_data_1"
REF_DIR = PROJECT_DIR / "reference_genome"

print("============ Starting Alignment ===============")

subprocess.run([
    'STAR', '--sjdbOverhang', '150',
    '--runMode', 'genomeGenerate',
    '--genomeSAindexNbases', '12',
    '--sjdbGTFfile', str(REF_DIR) + '/Drosophila_melanogaster.BDGP6.54.115.gtf',
    '--genomeFastaFiles', str(REF_DIR) + '/Drosophila_melanogaster.BDGP6.54.dna.toplevel.fa',
    '--genomeDir', str(PROJECT_DIR) + '/genome_index/',
    '--runThreadN', '4'
])

print(" ============== Alignmet Complete ===============")


