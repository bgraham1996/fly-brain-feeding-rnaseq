import subprocess
from pathlib import Path

# paths anchored to this script's directory (the repo, where the data lives)
PROJECT_DIR = Path(__file__).resolve().parent
BAM_DIR = PROJECT_DIR / "bam_files"
REF_DIR = PROJECT_DIR / "reference_genome"
FEATS_OUT_DIR = PROJECT_DIR / "feature_counts_output"

"""need to use -s 0 for an unstranded library"""

bam_files = sorted(BAM_DIR.glob('*.bam'))

subprocess.run([
    'featureCounts', 
    '-p', '--countReadPairs',
    '-T', '4',
    '-s', '0',
    '-a', (str(REF_DIR / 'Drosophila_melanogaster.BDGP6.54.115.gtf')),
    '-o', (str(FEATS_OUT_DIR / 'counts.txt')),
    *[str(bam) for bam in bam_files]
    
])
