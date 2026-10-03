from bs4 import BeautifulSoup
import json
import pandas as pd

# 1. Load HTML (from a file here; from requests.get(url).text for a website)
html = open('HTML_Reference_Sample_Campus_Events.html', encoding='utf-8').read()
soup = BeautifulSoup(html, 'html.parser')

# 2. Safe helper: returns None instead of crashing when a tag is missing
def get_text(parent, tag, cls):
    el = parent.find(tag, class_=cls)
    return el.get_text(strip=True) if el else None

# 3. Loop over the repeating box
events = []
for div in soup.find_all('div', class_='event'):
    events.append({
        'name':     div.find('h2').get_text(strip=True),
        'venue':    get_text(div, 'p', 'venue'),
        'date':     get_text(div, 'p', 'date'),
        'category': get_text(div, 'span', 'category'),
        'fee':      get_text(div, 'span', 'fee'),
        'seats':    get_text(div, 'p', 'seats'),
    })

# 4. HTML -> JSON (semi-structured)
with open('events.json', 'w', encoding='utf-8') as f:
    json.dump(events, f, indent=2, ensure_ascii=False)   # ensure_ascii=False keeps the rupee sign

# 5. JSON -> DataFrame (structured)
with open('events.json', encoding='utf-8') as f:
    df = pd.DataFrame(json.load(f))
print(df.isnull().sum())     # venue: 1  <- the Career talk

# 6. Clean
df['venue'] = df['venue'].fillna('Unknown')
df['fee']   = df['fee'].str.replace('₹', '', regex=False).replace('Free', '0').astype(int)
df['seats'] = df['seats'].str.extract(r'(\d+)').astype(int)      # 'Seats: 30' -> 30
df['date']  = pd.to_datetime(df['date'], format='%d %B %Y')    # '12 October 2026'

# 7. New features
df['is_free']           = df['fee'].eq(0)
df['day_of_week']       = df['date'].dt.day_name()
df['revenue_potential'] = df['fee'] * df['seats']