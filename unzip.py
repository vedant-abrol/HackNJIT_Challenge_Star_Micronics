"""
Unzip and Upload Script for STM Receipt Files

This script extracts .stm files from a zip archive and uploads them to AWS S3.
It handles errors gracefully and provides progress feedback.

Author: HackNJIT 2024 Challenge Team
"""

import zipfile
import boto3
import os
import sys
from pathlib import Path
from typing import Optional
from botocore.exceptions import ClientError, BotoCoreError


def extract_and_upload_to_s3(
    zip_file_path: str,
    s3_bucket_name: str,
    s3_folder: Optional[str] = 'stm_files',
    temp_dir: str = 'extracted_stm_files',
    verbose: bool = True
) -> tuple[int, int]:
    """
    Extract .stm files from zip and upload to S3.
    
    Args:
        zip_file_path: Path to the zip file containing .stm files
        s3_bucket_name: Name of the S3 bucket
        s3_folder: Optional folder prefix in S3 bucket
        temp_dir: Temporary directory for extraction
        verbose: If True, print progress messages
        
    Returns:
        Tuple of (successful_uploads, failed_uploads)
    """
    # Validate zip file exists
    zip_path = Path(zip_file_path)
    if not zip_path.exists():
        raise FileNotFoundError(f"Zip file not found: {zip_file_path}")
    
    # Initialize S3 client with error handling
    try:
        s3_client = boto3.client('s3')
        # Test connection by checking if bucket exists
        s3_client.head_bucket(Bucket=s3_bucket_name)
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', '')
        if error_code == '404':
            raise ValueError(f"S3 bucket '{s3_bucket_name}' does not exist.")
        elif error_code == '403':
            raise PermissionError(f"Access denied to S3 bucket '{s3_bucket_name}'.")
        else:
            raise ConnectionError(f"Error connecting to S3: {e}")
    except BotoCoreError as e:
        raise ConnectionError(f"AWS configuration error: {e}")
    
    # Create temp directory
    temp_path = Path(temp_dir)
    temp_path.mkdir(parents=True, exist_ok=True)
    
    successful_uploads = 0
    failed_uploads = 0
    
    try:
        # Extract and upload .stm files
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            stm_files = [f for f in zip_ref.infolist() if f.filename.endswith('.stm')]
            total_files = len(stm_files)
            
            if verbose:
                print(f"Found {total_files} .stm files in archive.")
            
            for idx, file_info in enumerate(stm_files, 1):
                try:
                    # Extract file to temp directory
                    zip_ref.extract(file_info, temp_path)
                    file_path = temp_path / file_info.filename
                    
                    # Define S3 key
                    s3_key = f"{s3_folder}/{file_info.filename}" if s3_folder else file_info.filename
                    
                    # Upload to S3
                    s3_client.upload_file(str(file_path), s3_bucket_name, s3_key)
                    
                    if verbose:
                        print(f"[{idx}/{total_files}] Uploaded {file_info.filename} to s3://{s3_bucket_name}/{s3_key}")
                    
                    successful_uploads += 1
                    
                    # Clean up local file immediately
                    file_path.unlink()
                    
                except Exception as e:
                    print(f"Error processing {file_info.filename}: {e}", file=sys.stderr)
                    failed_uploads += 1
                    # Try to clean up failed file
                    file_path = temp_path / file_info.filename
                    if file_path.exists():
                        try:
                            file_path.unlink()
                        except:
                            pass
    
    except zipfile.BadZipFile:
        raise ValueError(f"Invalid zip file: {zip_file_path}")
    except Exception as e:
        raise RuntimeError(f"Error during extraction: {e}")
    
    finally:
        # Cleanup temp directory
        try:
            if temp_path.exists():
                for item in temp_path.iterdir():
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        import shutil
                        shutil.rmtree(item)
                temp_path.rmdir()
        except Exception as e:
            if verbose:
                print(f"Warning: Could not clean up temp directory: {e}", file=sys.stderr)
    
    return successful_uploads, failed_uploads


def main():
    """Main entry point for the unzip and upload script."""
    # Configuration - can be overridden by environment variables
    zip_file_path = os.getenv('ZIP_FILE_PATH', 'PrintJobData_20241102.zip')
    s3_bucket_name = os.getenv('S3_BUCKET_NAME', 'pos-receipts-stm-files')
    s3_folder = os.getenv('S3_FOLDER', 'stm_files')
    temp_dir = os.getenv('TEMP_DIR', 'extracted_stm_files')
    
    print(f"Starting extraction and upload process...")
    print(f"Zip file: {zip_file_path}")
    print(f"S3 bucket: {s3_bucket_name}")
    print(f"S3 folder: {s3_folder}")
    print("-" * 50)
    
    try:
        successful, failed = extract_and_upload_to_s3(
            zip_file_path=zip_file_path,
            s3_bucket_name=s3_bucket_name,
            s3_folder=s3_folder,
            temp_dir=temp_dir
        )
        
        print("-" * 50)
        print(f"✓ Successfully uploaded: {successful} files")
        if failed > 0:
            print(f"✗ Failed uploads: {failed} files", file=sys.stderr)
        print("Upload process completed.")
        
        sys.exit(0 if failed == 0 else 1)
        
    except Exception as e:
        print(f"✗ Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
