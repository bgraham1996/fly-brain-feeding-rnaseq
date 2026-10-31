
from pathlib import Path
import subprocess

# paths anchored to this script's directory (the repo, where the data lives)
PROJECT_DIR = Path(__file__).resolve().parent
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


