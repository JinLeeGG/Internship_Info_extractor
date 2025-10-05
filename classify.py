import pandas as pd
import re

# 'openpyxl' 라이브러리가 설치되어 있어야 합니다. (pip install openpyxl)

# Unclassified 목록까지 모두 포함하여 최종 업데이트된 티어 분류
tier_map = {
    "Tier 1: Top-Tier / Reach": [
        "Adobe", "Akuna Capital", "Apple", "Asana", "Atlassian", "Balyasny Asset Management", "Bracebridge Capital",
        "Citadel", "Citadel Securities", "Cloudflare", "D. E. Shaw", "Databricks", "Datadog", "Dropbox", 
        "DV Commodities", "DV Group", "Figma", "Google", "Hudson River Trading", "IMC", "Jane Street", 
        "Jump Trading", "Meta", "Millennium", "MongoDB", "Neuralink", "NVIDIA", "Notion", "OpenAI", "Optiver", 
        "PDT Partners", "Pinterest", "Plaid", "Ramp", "Rippling", "Roblox", "Scale AI", "Scale.ai", 
        "Stripe", "Susquehanna", "TikTok", "Tower Research Capital", "TransMarket Group", "Virtu"
    ],
    "Tier 2: Strongly Possible / Target": [
        "Amazon", "AMD", "American Express", "Autodesk", "Barclays", "Belvedere Trading", "Block", 
        "Block, Inc.", "ByteDance", "C3.ai", "Cisco", "Coinbase", "Confluent", "DraftKings", "Duolingo", 
        "Electronic Arts", "Epic Games", "GitHub", "Goldman Sachs", "Grammarly", "IBM", "Intel", "Intuit", 
        "JP Morgan Chase", "Klaviyo", "LinkedIn", "Lyft", "Microsoft", "Morgan Stanley", "Motorola", 
        "Nuro", "Oracle", "PayPal", "Point72", "Qualcomm", "Riot Games", "Robinhood", "Salesforce", "Samsung", 
        "SAP", "Schonfeld", "ServiceNow", "The Trade Desk", "Uber", "Veeam Software", "Verkada", "Waymo", 
        "Zip", "Zoom"
    ],
    "Tier 3: Possible / Foundation": [
        "84.51 Degrees", "ABB", "AbbVie", "Acadian Asset Management", "Activision-Blizzard", "AeroVironment", 
        "Align Technology", "Allegion", "Altamira Technologies", "Altium Packaging", "Aluminum Dynamics", 
        "Ameritas Life Insurance Corp", "Analog Devices", "Apex Fintech Solutions", "APEX Analytix", "Appian", 
        "Aptiv", "Aquatic Capital Management", "Arch Capital Group", "Arconic", "Arm", "Arm Limited", 
        "Arrowstreet Capital", "Assured Guaranty", "Astronautics", "Auto-Owners Insurance", "AVEVA", "Avery Dennison", 
        "Axos Bank", "Badger Meter", "Baird", "Bank of America", "Barry-Wehmiller", "Berkshire Hathaway Energy", 
        "Bessemer Trust", "BlackEdge Capital", "Bluestaq", "BNY", "Booz Allen", "Boston Scientific", 
        "Brevium", "Brookfield Properties", "Brunswick", "C.H. Robinson", "Cadence Solutions", "CapTech Consulting", 
        "Cardinal Health", "Cargill", "Carollo Engineers", "Cboe", "Cboe Global Markets", "CDK", "CDK Global", 
        "CGI", "Charles Schwab", "Chatham Financial", "Chicago Trading Company", "Citizens Financial Group", 
        "CME Group", "CNA", "Cohesity", "Comcast", "Compassion International", "Conagra Brands", "Copart", "Corpay", 
        "Corteva", "Corteva Agriscience", "Cox", "Cox Automotive", "Cox Enterprises", "Deloitte", "Delta Air Lines, Inc.", 
        "Dexcom", "Dick's Sporting Goods", "Diversified Automation", "DL Trading", "Dow Jones", "DriveTime", 
        "EagleView", "Eaton Corporation", "Elanco", "Emerson Electric", "Enova", "Entrust", "Exegy", "FactSet", 
        "Fifth Third Bank", "Fintech", "Five Rings", "Flowserve", "Freddie Mac", "Fresenius Medical Care", 
        "Garmin", "GE Appliances", "GE Healthcare", "GE Vernova", "Generac", "General Motors", 
        "Genuine Parts Company", "GlobalFoundries", "GM financial", "GoFundMe", "GPC", "Guardian Life", 
        "Gulfstream", "Gusto", "Hewlett Packard Enterprise", "Hexagon AB", "Highmark Health", "Home Depot", 
        "Honeywell", "HP IQ", "Hudl", "ibotta", "ICD", "ICF", "IDeaS", "Impel", "Ingredion", 
        "Inmar Intelligence", "Inogen", "Innovative Systems", "Interactive Brokers", "Iron Mountain", 
        "IXL Learning", "Johnson & Johnson", "Kensho", "Keysight Technologies", "Kingland", "Kitware", 
        "Kodak", "LabCorp", "Lazard", "Lennox", "Lennox International", "LexisNexis Risk Solutions", 
        "Live Oak Bank", "LKQ", "LPL Financial Holdings", "Lucid", "Manulife Financial", "Marathon Petroleum", 
        "Marmon Holdings", "Marvell", "MasterControl", "McDonald's", "McNeilus", "Medline", "Medpace, Inc.", 
        "MFS", "Micron Technology", "Midmark", "MKS Instruments", "Moloco", "Moody's", "Muon Space", 
        "National Information Solutions Cooperative", "National Information Solutions Cooperative (NISC)", 
        "Neighbor", "Nelnet", "Netsmart", "New York Life Insurance", "Newrez", "NextEra Energy", "Nextdoor", 
        "Nicolet National Bank", "Nissan Global", "North Atlantic Industries", "Northmarq", "Nova-Tech", "Nutanix", 
        "nVent", "Omnitech", "ONE Finance", "Ontario Teachers' Pension Plan", "Openlane", "Origami Risk", "Oshkosh", 
        "Pacific Life", "Pella Corporation", "Pendo", "Philips", "Pierce Manufacturing", "PIMCO", "Plexus", 
        "PrizePicks", "Qorvo", "Radiant", "Red Hat", "Regal Rexnord", "Relativity Space", "Rockwell Automation", 
        "Samsara", "Santander", "Schweitzer Engineering Laboratories", "SciPlay", "Seagate", "Seagate Technology", 
        "SeatGeek", "Semgrep", "SEP", "Seven Research", "SharkNinja", "Shure", "SICK", "Siemens", "Sigma Computing", 
        "Solarity", "SpaceX", "Spectrum", "SPS Commerce", "Staples", "State Street", "State of Wisconsin Investment Board", 
        "Steel Dynamics", "StoneX Group", "Stryker", "Symbotic", "Talos", "Tamr", "Tanium", "TC Energy", "TD Securities", 
        "TEL", "Terex", "TetraMem", "Texas Instruments", "The Federal Reserve System", "The Toro Company", 
        "The Voleon Group", "Thermo Fisher Scientific", "Thrivent", "Tokyo Electron", "Tradeweb", "Trane Technologies", 
        "Transcard Payments", "TransPerfect", "Trimble", "TruStage", "Truveta", "Tyler Technologies", "U.S. Venture", 
        "Uline", "United Launch Alliance", "Universal Orlando Resort", "Vanguard", "Varian", "Vermeer", 
        "Verizon Communications", "Viam", "Viavi Solutions", "Voloridge Health", "Voloridge Investment Management", 
        "W.R. Berkley", "Walmart", "Wellmark", "Western & Southern Financial Group", "Wex", "WillowTree", 
        "Wind River", "Xantium", "Xcimer Energy", "YugaByte", "Zeiss", "Zebra", "Zebra Technologies", 
        "ZipRecruiter", "Zurn Elkay Water Solutions", "Zurn Elkay Water Solutions Corporation"
    ],
    "Tier 4: Visa Check Required": [
        "Abridge", "Al Warren Oil Company", "Altruist", "Anduril", "Athelas", "Audax Group", "Babel Street", 
        "Base Power", "Baseten", "Blockhouse", "Brilliant", "Candle", "CesiumAstro", "Circleback", "Cloudglue - YC", 
        "Commure", "CTGT", "Cua (X25)", "Cuckoo Labs", "Darkhive", "Dayton Freight Lines", "Decagon", 
        "Dev Technology Group", "EControls", "Elayne", "Ember", "Ember AI", "Empirical", "Eventual", 
        "Fable Security", "Falcomm", "FleetWorks", "Fresco (F24)", "Garage (W24)", "GIMLET LABS", "Gimlet Labs", 
        "Harmonic", "Hermeus", "Litify", "Lunar Energy", "Martin's Famous Pastry Shoppe, Inc.", "N1", "Netic", 
        "Numeric", "Oklahoma City Thunder", "Persona", "Promptless", "QuantCo", "Readily (S23)", "Reacher", 
        "Reframe Systems", "Relixir", "Relixir (X25)", "Replit", "RESPEC", "Rilla", "SIFT", "Stack Auth", 
        "Suno", "ThirdLayer", "ThirdLayer- YC(W25)", "Triple", "Upsolve", "Vast", "VAST", "WhatNot", 
        "Whatnot", "YouLearn - YC"
    ],
    "Tier 5: Citizenship Required": [
        "BAE Systems", "CACI", "Expedition Technology", "General Dynamics Mission Systems", 
        "Innovative Defense Technologies (IDT)", "KBR", "L3Harris", "L3Harris Technologies", "Leidos", 
        "Leonardo DRS", "MITRE", "Northrop Grumman", "Palantir", "Parsons", "Peraton", "RTX", 
        "Sierra Nevada Coporation", "The Aerospace Corporation"
    ]
}

# 1. CSV 파일 읽기 및 티어 분류
company_to_tier = {company.strip(): tier for tier, companies in tier_map.items() for company in companies}
try:
    df = pd.read_csv('csv_files/merged_jobs.csv')
except FileNotFoundError:
    print("오류: 'merged_jobs.csv' 파일을 찾을 수 없습니다.")
    exit()

def get_tier(company_name):
    if not isinstance(company_name, str): return "Unclassified"
    clean_company_name = company_name.strip()
    if clean_company_name in company_to_tier: return company_to_tier[clean_company_name]
    for company, tier in company_to_tier.items():
        if company in clean_company_name: return tier
    return "Unclassified"

df['Tier'] = df['Company'].apply(get_tier)
print("모든 직무에 대한 티어 분류를 완료했습니다.")

# 2. 엑셀 파일로 저장 (순서 지정)
output_filename = 'csv_files/jobs_by_tier.xlsx'
writer = pd.ExcelWriter(output_filename, engine='openpyxl')

# 생성할 탭(시트)의 순서를 직접 지정
ordered_tiers = [
    "Tier 1: Top-Tier / Reach",
    "Tier 2: Strongly Possible / Target",
    "Tier 3: Possible / Foundation",
    "Tier 4: Visa Check Required",
    "Tier 5: Citizenship Required",
    "Unclassified"
]

for tier in ordered_tiers:
    # 각 티어에 해당하는 데이터만 필터링
    tier_df = df[df['Tier'] == tier]
    
    # 해당 티어에 데이터가 있을 경우에만 시트를 생성
    if not tier_df.empty:
        # 시트 이름으로 사용하기 위해 특수문자 제거 및 길이 제한
        sheet_name = re.sub(r'[:/]', '-', tier)[:31]
        
        tier_df.to_excel(writer, sheet_name=sheet_name, index=False)
        print(f"'{sheet_name}' 탭을 생성했습니다.")

# 엑셀 파일 저장 및 완료
writer.close()
print(f"✅ 완료! '{output_filename}' 파일에 모든 티어가 순서대로 저장되었습니다.")