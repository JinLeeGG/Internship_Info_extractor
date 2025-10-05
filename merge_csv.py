#!/usr/bin/env python3
"""
merge_csv.py

Usage:
  python merge_csv.py file1.csv file2.csv -o output.csv

This script merges two CSV files, removing duplicate rows based on a specified
unique key column ('Link' by default).
"""
import csv
import sys
import argparse

def merge_unique_rows(file1_path, file2_path, key_column, output_path):
    """
    Merges unique rows from two CSV files into a new CSV file.

    Args:
        file1_path (str): Path to the first input CSV file.
        file2_path (str): Path to the second input CSV file.
        key_column (str): The column name to use as a unique identifier.
        output_path (str): Path for the output CSV file.
    """
    unique_rows = []
    seen_keys = set()
    header = []
    
    input_files = [file1_path, file2_path]
    total_rows_processed = 0

    print(f"Starting merge process. Unique key: '{key_column}'")

    for file_path in input_files:
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # 헤더가 비어있으면 건너뛰기
                if not reader.fieldnames:
                    print(f"Warning: '{file_path}' is empty or has no header. Skipping.")
                    continue
                
                # 첫 번째 유효한 파일에서 헤더를 설정
                if not header:
                    header = reader.fieldnames
                
                # 키 컬럼이 파일에 있는지 확인
                if key_column not in header:
                    print(f"Error: Key column '{key_column}' not found in '{file_path}'.")
                    sys.exit(1)
                
                for row in reader:
                    total_rows_processed += 1
                    key_value = row.get(key_column)
                    
                    # 키 값이 존재하고, 아직 처리된 적 없는 키라면 추가
                    if key_value and key_value not in seen_keys:
                        seen_keys.add(key_value)
                        unique_rows.append(row)

        except FileNotFoundError:
            print(f"Error: Input file not found at '{file_path}'")
            sys.exit(1)
        except Exception as e:
            print(f"An error occurred while processing '{file_path}': {e}")
            sys.exit(1)
            
    # 고유한 행이 있을 경우에만 CSV 파일 작성
    if unique_rows:
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                # 헤더는 첫 번째 파일의 헤더를 기준으로 사용
                writer = csv.DictWriter(f, fieldnames=header)
                writer.writeheader()
                writer.writerows(unique_rows)
            
            print("-" * 30)
            print(f"Total rows processed: {total_rows_processed}")
            print(f"Unique rows found: {len(unique_rows)}")
            print(f"✅ Successfully merged unique rows into '{output_path}'")
            
        except Exception as e:
            print(f"An error occurred while writing to '{output_path}': {e}")
            sys.exit(1)
    else:
        print("No unique rows found to write.")


def main():
    parser = argparse.ArgumentParser(
        description="Merge two CSV files and remove duplicates based on a key column.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('file1', help='Path to the first input CSV file.')
    parser.add_argument('file2', help='Path to the second input CSV file.')
    parser.add_argument(
        '-o', '--output', 
        default='merged_unique_jobs.csv', 
        help='Path for the output CSV file (default: merged_unique_jobs.csv).'
    )
    parser.add_argument(
        '-k', '--key', 
        default='Link', 
        help="The column name to use for deduplication (default: 'Link')."
    )
    args = parser.parse_args()
    
    merge_unique_rows(args.file1, args.file2, args.key, args.output)

if __name__ == '__main__':
    main()