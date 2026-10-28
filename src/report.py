from pathlib import Path
from .config import ROOT, REPORTS

def main():
    template=ROOT/'reports'/'REPORT_TEMPLATE.md'
    print(f'Report template: {template}\nFill it using actual outputs in {ROOT / "outputs"}. Do not report sample data as real findings.')
if __name__=='__main__': main()
