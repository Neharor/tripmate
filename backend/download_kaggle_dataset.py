#!/usr/bin/env python3
"""
Download Kaggle Travel Dataset for Trending Destinations
Dataset: Traveler Trip Data
Source: https://www.kaggle.com/datasets/rkiattisak/traveler-trip-data
"""

import os
import sys
from pathlib import Path

def setup_kaggle_credentials():
    """
    Setup Kaggle API credentials
    
    Steps:
    1. Go to https://www.kaggle.com/settings
    2. Click "Create New API Token"
    3. Download kaggle.json
    4. Place it in ~/.kaggle/kaggle.json
    """
    kaggle_dir = Path.home() / '.kaggle'
    kaggle_json = kaggle_dir / 'kaggle.json'
    
    if not kaggle_json.exists():
        print("❌ Kaggle credentials not found!")
        print("\n📝 Setup Instructions:")
        print("1. Go to: https://www.kaggle.com/settings")
        print("2. Click 'Create New API Token' (downloads kaggle.json)")
        print(f"3. Move file to: {kaggle_json}")
        print("4. Run: chmod 600 ~/.kaggle/kaggle.json")
        print("\nThen run this script again.")
        return False
    
    # Set correct permissions
    os.chmod(kaggle_json, 0o600)
    print("✓ Kaggle credentials found")
    return True

def download_traveler_dataset():
    """
    Download the Traveler Trip Dataset from Kaggle
    """
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
        
        # Initialize API
        api = KaggleApi()
        api.authenticate()
        
        # Create data directory
        data_dir = Path(__file__).parent / 'data' / 'kaggle'
        data_dir.mkdir(parents=True, exist_ok=True)
        
        print("\n📥 Downloading Kaggle dataset...")
        print("Dataset: rkiattisak/traveler-trip-data")
        
        # Download dataset
        api.dataset_download_files(
            'rkiattisak/traveler-trip-data',
            path=str(data_dir),
            unzip=True
        )
        
        print(f"✓ Dataset downloaded to: {data_dir}")
        
        # List downloaded files
        print("\n📂 Downloaded files:")
        for file in data_dir.iterdir():
            if file.is_file():
                size_mb = file.stat().st_size / (1024 * 1024)
                print(f"  - {file.name} ({size_mb:.2f} MB)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error downloading dataset: {e}")
        print("\n💡 Alternative: Using sample data generation instead")
        return False

def verify_dataset():
    """
    Verify downloaded dataset
    """
    data_dir = Path(__file__).parent / 'data' / 'kaggle'
    csv_files = list(data_dir.glob('*.csv'))
    
    if csv_files:
        print(f"\n✓ Found {len(csv_files)} CSV file(s)")
        
        # Try to load with pandas
        try:
            import pandas as pd
            df = pd.read_csv(csv_files[0])
            print(f"✓ Dataset loaded: {len(df)} rows, {len(df.columns)} columns")
            print(f"\nColumns: {', '.join(df.columns.tolist()[:10])}")
            return True
        except Exception as e:
            print(f"⚠️ Could not load CSV: {e}")
            return False
    else:
        print("❌ No CSV files found")
        return False

def main():
    print("=" * 60)
    print("  Kaggle Travel Dataset Downloader")
    print("=" * 60)
    
    # Step 1: Check credentials
    if not setup_kaggle_credentials():
        print("\n💡 Using sample data generation as fallback")
        print("   Your app will still work with synthetic travel data")
        return
    
    # Step 2: Download dataset
    if download_traveler_dataset():
        # Step 3: Verify
        verify_dataset()
        print("\n✅ Dataset ready! Run your app to use Kaggle data.")
    else:
        print("\n⚠️ Download failed - using fallback sample data")

if __name__ == "__main__":
    main()
