"""
Receipt Clustering Script - Organize STM files by Cafe ID and Date

This script organizes unstructured .stm receipt files in S3 by clustering them
into a structured hierarchy: clustered_receipts/{cafe_id}/{date}/{filename}

It extracts cafe IDs and dates from filenames and reorganizes files accordingly.

Author: HackNJIT 2024 Challenge Team
"""

import os
import sys
import re
from pathlib import Path
from typing import Optional, Tuple
import boto3
from botocore.exceptions import ClientError, BotoCoreError


# Configuration
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME', 'pos-receipts-stm-files')
SOURCE_FOLDER = os.getenv('S3_SOURCE_FOLDER', 'stm_files')
DESTINATION_FOLDER = os.getenv('S3_DESTINATION_FOLDER', 'clustered_receipts')
TEMP_DIR = os.getenv('TEMP_DIR', '/tmp')


def extract_cafe_id_and_date(filename: str) -> Optional[Tuple[str, str]]:
    """
    Extract cafe ID and date from filename.
    
    Expected filename format: {prefix}-{date}_{cafe_id}.stm
    or similar variations.
    
    Args:
        filename: Name of the STM file
        
    Returns:
        Tuple of (cafe_id, date) or None if extraction fails
    """
    # Method 1: Extract last 4 digits as cafe ID (common pattern)
    cafe_id_match = re.search(r'(\d{4})\.stm$', filename)
    if cafe_id_match:
        cafe_id = cafe_id_match.group(1)
    else:
        # Try to find 4-digit pattern anywhere in filename
        cafe_id_match = re.search(r'(\d{4})', filename)
        if cafe_id_match:
            cafe_id = cafe_id_match.group(1)
        else:
            return None
    
    # Method 1: Extract date from format like YYYYMMDD
    date_match = re.search(r'(\d{8})', filename)
    if date_match:
        date = date_match.group(1)
    else:
        # Method 2: Try splitting by common delimiters
        try:
            # Try format: prefix-YYYYMMDD_something.stm
            parts = filename.split('_')
            if len(parts) > 0:
                date_part = parts[0].split('-')
                if len(date_part) > 2:
                    date = date_part[2]  # Extract YYYYMMDD from position
                else:
                    return None
            else:
                return None
        except (IndexError, ValueError):
            return None
    
    # Validate date format (should be 8 digits)
    if not re.match(r'^\d{8}$', date):
        return None
    
    return cafe_id, date


def organize_file(
    s3_client: boto3.client,
    s3_key: str,
    filename: str,
    temp_dir: str
) -> Tuple[bool, str]:
    """
    Organize a single file by moving it to the clustered structure.
    
    Args:
        s3_client: Boto3 S3 client
        s3_key: Current S3 object key
        filename: Filename
        temp_dir: Temporary directory for downloads
        
    Returns:
        Tuple of (success, message)
    """
    # Extract cafe ID and date
    extraction_result = extract_cafe_id_and_date(filename)
    if not extraction_result:
        return False, f"Could not extract cafe ID and date from {filename}"
    
    cafe_id, date = extraction_result
    
    # Define destination path
    organized_s3_key = f"{DESTINATION_FOLDER}/{cafe_id}/{date}/{filename}"
    
    # Check if file already exists in destination
    try:
        s3_client.head_object(Bucket=S3_BUCKET_NAME, Key=organized_s3_key)
        return True, f"File already exists at {organized_s3_key} (skipped)"
    except ClientError as e:
        if e.response['Error']['Code'] != '404':
            return False, f"Error checking file existence: {e}"
    
    # Download, then upload to new location
    local_path = Path(temp_dir) / filename
    
    try:
        # Download file
        s3_client.download_file(S3_BUCKET_NAME, s3_key, str(local_path))
        
        # Upload to organized location
        s3_client.upload_file(str(local_path), S3_BUCKET_NAME, organized_s3_key)
        
        return True, f"Organized {filename} → {organized_s3_key}"
        
    except Exception as e:
        return False, f"Error processing {filename}: {e}"
    finally:
        # Cleanup local file
        if local_path.exists():
            try:
                local_path.unlink()
            except:
                pass


def cluster_receipts(verbose: bool = True) -> dict:
    """
    Cluster all receipt files in S3 by cafe ID and date.
    
    Args:
        verbose: If True, print progress messages
        
    Returns:
        Dictionary with clustering statistics
    """
    stats = {
        'total_files': 0,
        'organized': 0,
        'skipped': 0,
        'failed': 0,
        'cafes': set(),
        'dates': set()
    }
    
    try:
s3_client = boto3.client('s3')

        # Test connection
        s3_client.head_bucket(Bucket=S3_BUCKET_NAME)
        
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', '')
        if error_code == '404':
            raise ValueError(f"S3 bucket '{S3_BUCKET_NAME}' does not exist.")
        elif error_code == '403':
            raise PermissionError(f"Access denied to S3 bucket '{S3_BUCKET_NAME}'.")
    else:
            raise ConnectionError(f"Error connecting to S3: {e}")
    except BotoCoreError as e:
        raise ConnectionError(f"AWS configuration error: {e}")
    
    # Use paginator for efficient listing
    paginator = s3_client.get_paginator('list_objects_v2')
    page_iterator = paginator.paginate(
        Bucket=S3_BUCKET_NAME,
        Prefix=SOURCE_FOLDER
    )
    
    for page in page_iterator:
        if 'Contents' not in page:
            continue
        
        for obj in page['Contents']:
            s3_key = obj['Key']
            
            # Process only .stm files
            if not s3_key.endswith('.stm'):
                continue
            
            stats['total_files'] += 1
                filename = os.path.basename(s3_key)
                
            # Organize the file
            success, message = organize_file(s3_client, s3_key, filename, TEMP_DIR)
            
            if success:
                if 'already exists' in message.lower():
                    stats['skipped'] += 1
                else:
                    stats['organized'] += 1
                    # Extract cafe and date for stats
                    result = extract_cafe_id_and_date(filename)
                    if result:
                        cafe_id, date = result
                        stats['cafes'].add(cafe_id)
                        stats['dates'].add(date)
                
                if verbose:
                    print(f"✓ {message}")
            else:
                stats['failed'] += 1
                if verbose:
                    print(f"✗ {message}", file=sys.stderr)
    
    stats['cafes'] = len(stats['cafes'])
    stats['dates'] = len(stats['dates'])
    return stats


def main():
    """Main entry point for the clustering script."""
    print("=" * 60)
    print("Receipt Clustering - Organize by Cafe ID and Date")
    print("=" * 60)
    print(f"S3 Bucket: {S3_BUCKET_NAME}")
    print(f"Source Folder: {SOURCE_FOLDER}")
    print(f"Destination Folder: {DESTINATION_FOLDER}")
    print("-" * 60)
    
    try:
        stats = cluster_receipts()
        
        # Print summary
        print("-" * 60)
        print("Clustering Summary:")
        print(f"  Total files found: {stats['total_files']}")
        print(f"  Successfully organized: {stats['organized']}")
        print(f"  Already organized (skipped): {stats['skipped']}")
        print(f"  Failed: {stats['failed']}")
        print(f"  Unique cafes: {stats['cafes']}")
        print(f"  Unique dates: {stats['dates']}")
        print("=" * 60)
        
        if stats['failed'] > 0:
            print(f"⚠ Warning: {stats['failed']} files failed to organize.", file=sys.stderr)
            sys.exit(1)
        else:
            print("✓ All files organized successfully!")
            sys.exit(0)
            
    except Exception as e:
        print(f"✗ Fatal error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
