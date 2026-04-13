import os
import sys
from dotenv import load_dotenv

# Add the current directory to sys.path to import KISClient
sys.path.append(os.path.join(os.getcwd(), 'scraper'))

from kis_client import KISClient

def diag():
    client = KISClient()
    print("Fetching rankings...")
    kospi = client.get_market_rankings("0001")
    kosdaq = client.get_market_rankings("1001")
    
    threshold = 50_000_000_000
    
    print(f"KOSPI count: {len(kospi)}")
    passed_kospi = [s for s in kospi[:15] if float(s.get('acml_tr_pbmn', 0)) >= threshold]
    print(f"KOSPI passed (top 15): {len(passed_kospi)}")
    for s in passed_kospi:
        print(f"  - {s.get('hts_kor_isnm')}: {float(s.get('acml_tr_pbmn', 0)) / 1e8:.1f}억")

    print(f"KOSDAQ count: {len(kosdaq)}")
    passed_kosdaq = [s for s in kosdaq[:15] if float(s.get('acml_tr_pbmn', 0)) >= threshold]
    print(f"KOSDAQ passed (top 15): {len(passed_kosdaq)}")
    for s in passed_kosdaq:
        print(f"  - {s.get('hts_kor_isnm')}: {float(s.get('acml_tr_pbmn', 0)) / 1e8:.1f}억")

if __name__ == "__main__":
    diag()
