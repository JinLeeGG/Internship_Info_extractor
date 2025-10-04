#!/usr/bin/env python3
"""
parse_jobs.py

Usage:
  python parse_jobs.py input.txt -o software_jobs.csv
  cat input.txt | python parse_jobs.py - -o software_jobs.csv

This extracts rows whose Role matches software-related keywords,
removes utm_source from the job link, filters out Canada locations,
formats dates (e.g., 'Sep 24', '3d') to YYYY-MM-DD (with current year),
and writes a CSV with:
Company, Role, Date Posted, Location, Link
"""
from datetime import date, datetime, timedelta # <<< timedelta 임포트 추가
from dateutil.relativedelta import relativedelta
import re
import csv
import sys
import argparse
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
from bs4 import BeautifulSoup

def strip_html_tags(s: str) -> str:
    if not s:
        return ''
    s = re.sub(r'<br\s*/?>', ', ', s, flags=re.IGNORECASE)
    return re.sub(r'<[^>]+>', '', s).strip()

def extract_href(s: str) -> str:
    if not s:
        return ''
    soup = BeautifulSoup(s, 'html.parser')
    link_tag = soup.find('a')
    return link_tag['href'] if link_tag and link_tag.has_attr('href') else ''

def remove_utm_source(url: str) -> str:
    if not url:
        return ''
    parsed = urlparse(url)
    qsl = parse_qsl(parsed.query, keep_blank_values=True)
    filtered = [(k, v) for (k, v) in qsl if k.lower() != 'utm_source']
    new_query = urlencode(filtered)
    cleaned = parsed._replace(query=new_query)
    return urlunparse(cleaned)

def is_software_role(role_text: str, keywords) -> bool:
    r = role_text.lower()
    for k in keywords:
        if k in r:
            return True
    return False

def parse_markdown_table(text: str, keywords):
    rows = []
    last_company = ''
    for raw in text.splitlines():
        line = raw.strip()
        if not line.startswith('|') or line.startswith('|-') or '---' in line:
            continue
        
        cols = [c.strip() for c in line.split('|')[1:-1]]
        if len(cols) < 4:
            continue
            
        company_cell, role_cell, location_cell, link_cell, *date_parts = cols
        date_cell = date_parts[0] if date_parts else ''

        company_text = strip_html_tags(company_cell)
        company = last_company if (company_text == '↳' or company_text == '') else company_text
        if company_text != '↳' and company_text != '':
            last_company = company_text

        role = strip_html_tags(role_cell)
        location = strip_html_tags(location_cell)
        raw_link = extract_href(link_cell)
        clean_link = remove_utm_source(raw_link)

        if is_software_role(role, keywords):
            rows.append({
                'Company': company, 'Role': role, 'Date Posted': date_cell,
                'Location': location, 'Link': clean_link
            })
    return rows

def parse_html_table(text: str, keywords):
    rows = []
    soup = BeautifulSoup(text, 'html.parser')
    table_rows = soup.find_all('tbody')
    last_company = ''
    
    for tbody in table_rows:
        for row in tbody.find_all('tr'):
            cols = row.find_all('td')
            if len(cols) < 5:
                continue

            company_cell = cols[0]
            role_cell = cols[1]
            location_cell = cols[2]
            link_cell = cols[3]
            date_cell = cols[4]

            company_text = company_cell.get_text(strip=True)
            if company_text == '' or '↳' in company_text:
                company = last_company
            else:
                company = company_text
                last_company = company_text

            role = role_cell.get_text(strip=True)
            location = location_cell.get_text(separator=', ', strip=True)
            
            raw_link_tag = link_cell.find('a')
            raw_link = raw_link_tag['href'] if raw_link_tag and raw_link_tag.has_attr('href') else ''
            clean_link = remove_utm_source(raw_link)
            
            date = date_cell.get_text(strip=True)

            if is_software_role(role, keywords):
                rows.append({
                    'Company': company, 'Role': role, 'Date Posted': date,
                    'Location': location, 'Link': clean_link
                })
    return rows

def postprocess_rows(rows):
    processed = []
    today = date.today()
    current_year = today.year
    
    exclude_emojis = {'🛂', '🇺🇸', '🔒', '🎓'}
    all_emojis_to_clean = {'🛂', '🇺🇸', '🔒', '🔥', '🎓'}

    for r in rows:
        if not r.get('Link'):
            continue

        check_string = r.get('Company', '') + r.get('Role', '')
        if any(emoji in check_string for emoji in exclude_emojis):
            continue

        for emoji in all_emojis_to_clean:
            r['Company'] = r['Company'].replace(emoji, '').strip()
            r['Role'] = r['Role'].replace(emoji, '').strip()

        location_lower = r['Location'].lower()
        if any(country in location_lower for country in ['canada', ' uk', 'germany']):
            continue

        date_str = r['Date Posted'].strip().lower()
        
        try:
            if 'mo' in date_str:
                months_ago = int(re.search(r'\d+', date_str).group())
                past_date = today - relativedelta(months=months_ago)
                r['Date Posted'] = past_date.strftime("%Y-%m-%d")
            # <<< --- 이 부분이 수정되었습니다 ---
            elif 'd' in date_str:
                days_ago = int(re.search(r'\d+', date_str).group())
                past_date = today - timedelta(days=days_ago)
                r['Date Posted'] = past_date.strftime("%Y-%m-%d")
            # <<< --- 수정 끝 ---
            elif date_str:
                # 'Sep 24'와 같은 형식 처리
                dt = datetime.strptime(f"{date_str} {current_year}", "%b %d %Y")
                r['Date Posted'] = dt.strftime("%Y-%m-%d")
        except (ValueError, AttributeError):
            # 날짜 변환 실패 시 기존 값을 유지하거나 비워둘 수 있음
            pass
        
        processed.append(r)
    return processed

def write_csv(rows, outpath):
    fieldnames = ['Company', 'Role', 'Date Posted', 'Location', 'Link']
    with open(outpath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def main():
    parser = argparse.ArgumentParser(description='Extract software roles from markdown/HTML table and save CSV.')
    parser.add_argument('input', help='Input file path or "-" for stdin')
    parser.add_argument('-o', '--output', default='software_jobs.csv', help='Output CSV path')
    parser.add_argument('--keywords', help='Comma-separated keywords (case-insensitive). Overrides defaults.')
    args = parser.parse_args()

    try:
        if args.input == '-':
            text = sys.stdin.read()
        else:
            with open(args.input, 'r', encoding='utf-8') as f:
                text = f.read()
    except FileNotFoundError:
        print(f"Error: Input file not found at '{args.input}'")
        sys.exit(1)

    default_keywords = [
        'software engineer', 'software dev', 'developer', 'swe', 'sde', 'r&d software',
        'application engineer', 'firmware', 'embedded', 'systems engineer',
        'backend', 'frontend', 'full stack', 'full-stack', 'data engineer'
    ]
    if args.keywords:
        keywords = [k.strip().lower() for k in args.keywords.split(',') if k.strip()]
    else:
        keywords = default_keywords

    rows = []
    if '<thead>' in text.lower():
        print("HTML table format detected. Parsing...")
        rows = parse_html_table(text, keywords)
    else:
        print("Markdown pipe table format detected. Parsing...")
        rows = parse_markdown_table(text, keywords)
    
    processed_rows = postprocess_rows(rows)
    write_csv(processed_rows, args.output)
    print(f'✅ Extracted {len(processed_rows)} rows -> {args.output}')

if __name__ == '__main__':
    main()