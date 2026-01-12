"""
STM Receipt Parser - Convert STM files to CSV format

This script parses .stm receipt files from S3, extracts structured data,
and converts them to CSV format for analysis. It handles multiple cafes
and provides comprehensive error handling.

Author: HackNJIT 2024 Challenge Team
"""

import re
import csv
import boto3
import os
import sys
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from botocore.exceptions import ClientError, BotoCoreError
from collections import defaultdict


# Configuration
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME', 'pos-receipts-stm-files')
S3_SOURCE_FOLDER = os.getenv('S3_SOURCE_FOLDER', 'clustered_receipts')
S3_DESTINATION_FOLDER = os.getenv('S3_DESTINATION_FOLDER', 'processed_receipts')
TEMP_DIR = os.getenv('TEMP_DIR', '/tmp')
CAFE_FILTER = os.getenv('CAFE_FILTER', None)  # Set to specific cafe ID or None for all


class STMParser:
    """Parser for STM receipt files."""
    
    # Regex patterns for extracting data
    ORDER_NO_PATTERN = re.compile(r"Order No:\s*(\d+)", re.IGNORECASE)
    TIME_PATTERN = re.compile(r"(\d{2}:\d{2}:\d{2})")
    TOTAL_AMOUNT_PATTERN = re.compile(r"Total amount:\s*([\d.]+)\s*EUR", re.IGNORECASE)
    ITEM_PATTERN = re.compile(r"(\d+\s*-\s*.+?)\s*//\s*([\d.]+)\s*EUR\s*//\s*VAT:\s*([\d.]+%)", re.IGNORECASE)
    
    CSV_HEADERS = ["cafe_id", "date", "time", "order_no", "item", "price", "vat", "total_amount"]
    
    @staticmethod
    def parse_stm_content(content: str) -> Dict:
        """
        Parse STM file content and extract structured data.
        
        Args:
            content: Raw content of the STM file
            
        Returns:
            Dictionary containing parsed data
        """
        # Extract order number
        order_no_match = STMParser.ORDER_NO_PATTERN.search(content)
        order_no = order_no_match.group(1) if order_no_match else None
        
        # Extract time
        time_match = STMParser.TIME_PATTERN.search(content)
        time = time_match.group(1) if time_match else None
        
        # Extract total amount
        total_amount_match = STMParser.TOTAL_AMOUNT_PATTERN.search(content)
        total_amount = total_amount_match.group(1) if total_amount_match else None
        
        # Extract items
        items = STMParser.ITEM_PATTERN.findall(content)
        
        return {
            'order_no': order_no,
            'time': time,
            'total_amount': total_amount,
            'items': items
        }
    
    @staticmethod
    def write_csv_row(writer: csv.writer, cafe_id: str, date: str, parsed_data: Dict) -> int:
        """
        Write parsed data to CSV file.
        
        Args:
            writer: CSV writer object
            cafe_id: Cafe identifier
            date: Date string
            parsed_data: Parsed data dictionary
            
        Returns:
            Number of rows written
        """
        rows_written = 0
        order_no = parsed_data.get('order_no')
        time = parsed_data.get('time')
        total_amount = parsed_data.get('total_amount')
        items = parsed_data.get('items', [])
        
        for item in items:
            item_name = item[0].strip()
            price = item[1].strip()
            vat = item[2].strip()
            
            writer.writerow([
                cafe_id,
                date,
                time or '',
                order_no or '',
                item_name,
                price,
                vat,
                total_amount or ''
            ])
            rows_written += 1
        
        return rows_written


def process_stm_file(
    s3_client: boto3.client,
    s3_key: str,
    cafe_id: str,
    date: str,
    filename: str,
    temp_dir: str
) -> Tuple[bool, int, str]:
    """
    Process a single STM file: download, parse, and upload CSV.
    
    Args:
        s3_client: Boto3 S3 client
        s3_key: S3 object key
        cafe_id: Cafe identifier
        date: Date string
        filename: Original filename
        temp_dir: Temporary directory for downloads
        
    Returns:
        Tuple of (success, rows_written, error_message)
    """
    local_stm_path = Path(temp_dir) / filename
    csv_filename = filename.replace('.stm', '.csv')
    local_csv_path = Path(temp_dir) / csv_filename
    
    try:
        # Download STM file
        s3_client.download_file(S3_BUCKET_NAME, s3_key, str(local_stm_path))
        
        # Read and parse STM content
        with open(local_stm_path, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()
        
        parsed_data = STMParser.parse_stm_content(content)
        
        # Check if CSV already exists (for appending)
        file_exists = local_csv_path.exists()
        file_size = local_csv_path.stat().st_size if file_exists else 0
        
        # Write to CSV
        with open(local_csv_path, mode='a' if file_exists else 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            
            # Write header if new file
            if file_size == 0:
                writer.writerow(STMParser.CSV_HEADERS)
            
            rows_written = STMParser.write_csv_row(writer, cafe_id, date, parsed_data)
        
        # Upload CSV to S3
        s3_destination_key = f"{S3_DESTINATION_FOLDER}/cafe_{cafe_id}/date_{date}/{csv_filename}"
        s3_client.upload_file(str(local_csv_path), S3_BUCKET_NAME, s3_destination_key)
        
        # Cleanup local files
        if local_stm_path.exists():
            local_stm_path.unlink()
        if local_csv_path.exists():
            local_csv_path.unlink()
        
        return True, rows_written, ""
        
    except Exception as e:
        error_msg = f"Error processing {filename}: {str(e)}"
        # Cleanup on error
        for path in [local_stm_path, local_csv_path]:
            if path.exists():
                try:
                    path.unlink()
                except:
                    pass
        return False, 0, error_msg


def process_all_receipts(
    s3_client: boto3.client,
    cafe_filter: Optional[str] = None,
    verbose: bool = True
) -> Dict[str, int]:
    """
    Process all STM files from S3 source folder.
    
    Args:
        s3_client: Boto3 S3 client
        cafe_filter: Optional cafe ID to filter by
        verbose: If True, print progress messages
        
    Returns:
        Dictionary with processing statistics
    """
    stats = {
        'total_files': 0,
        'processed': 0,
        'failed': 0,
        'total_rows': 0,
        'cafes': set()
    }
    
    paginator = s3_client.get_paginator('list_objects_v2')
    page_iterator = paginator.paginate(Bucket=S3_BUCKET_NAME, Prefix=S3_SOURCE_FOLDER)
    
    for page in page_iterator:
        if 'Contents' not in page:
            continue
        
        for obj in page['Contents']:
            s3_key = obj['Key']
            
            # Process only .stm files
            if not s3_key.endswith('.stm'):
                continue

            # Apply cafe filter if specified
            if cafe_filter and f'/{cafe_filter}/' not in s3_key:
                continue
            
            stats['total_files'] += 1
            
            # Parse S3 key structure: clustered_receipts/{cafe_id}/{date}/{filename}
            try:
                parts = s3_key.split('/')
                if len(parts) < 4:
                    if verbose:
                        print(f"Warning: Unexpected file structure for {s3_key}. Skipping.", file=sys.stderr)
                    stats['failed'] += 1
                    continue
                
                _, _, cafe_id, date, filename = parts
                stats['cafes'].add(cafe_id)
                
            except ValueError as e:
                if verbose:
                    print(f"Error parsing S3 key {s3_key}: {e}. Skipping.", file=sys.stderr)
                stats['failed'] += 1
                continue
            
            # Process the file
            success, rows_written, error_msg = process_stm_file(
                s3_client, s3_key, cafe_id, date, filename, TEMP_DIR
            )
            
            if success:
                stats['processed'] += 1
                stats['total_rows'] += rows_written
                if verbose:
                    print(f"✓ Processed {filename} (cafe {cafe_id}, date {date}): {rows_written} rows")
            else:
                stats['failed'] += 1
                if verbose:
                    print(f"✗ {error_msg}", file=sys.stderr)
    
    stats['cafes'] = len(stats['cafes'])
    return stats


def main():
    """Main entry point for the parsing script."""
    print("=" * 60)
    print("STM Receipt Parser - CSV Conversion")
    print("=" * 60)
    print(f"S3 Bucket: {S3_BUCKET_NAME}")
    print(f"Source Folder: {S3_SOURCE_FOLDER}")
    print(f"Destination Folder: {S3_DESTINATION_FOLDER}")
    if CAFE_FILTER:
        print(f"Cafe Filter: {CAFE_FILTER}")
    print("-" * 60)
    
    try:
        # Initialize S3 client
        s3_client = boto3.client('s3')
        
        # Test connection
        s3_client.head_bucket(Bucket=S3_BUCKET_NAME)
        
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', '')
        if error_code == '404':
            print(f"✗ Error: S3 bucket '{S3_BUCKET_NAME}' does not exist.", file=sys.stderr)
        elif error_code == '403':
            print(f"✗ Error: Access denied to S3 bucket '{S3_BUCKET_NAME}'.", file=sys.stderr)
        else:
            print(f"✗ Error connecting to S3: {e}", file=sys.stderr)
        sys.exit(1)
    except BotoCoreError as e:
        print(f"✗ AWS configuration error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Process all receipts
    try:
        stats = process_all_receipts(s3_client, cafe_filter=CAFE_FILTER)
        
        # Print summary
        print("-" * 60)
        print("Processing Summary:")
        print(f"  Total files found: {stats['total_files']}")
        print(f"  Successfully processed: {stats['processed']}")
        print(f"  Failed: {stats['failed']}")
        print(f"  Total rows written: {stats['total_rows']}")
        print(f"  Unique cafes: {stats['cafes']}")
        print("=" * 60)
        
        if stats['failed'] > 0:
            print(f"⚠ Warning: {stats['failed']} files failed to process.", file=sys.stderr)
            sys.exit(1)
else:
            print("✓ All files processed successfully!")
            sys.exit(0)
            
    except Exception as e:
        print(f"✗ Fatal error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
