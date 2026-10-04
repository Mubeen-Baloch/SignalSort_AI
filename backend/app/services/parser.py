import re
from datetime import datetime
P1=re.compile(r'^(?P<date>\d{1,2}/\d{1,2}/\d{2,4}),\s*(?P<time>\d{1,2}:\d{2}(?:\s?[ap]m)?)\s*-\s*(?P<body>.*)$',re.I)
P2=re.compile(r'^\[(?P<date>\d{1,2}/\d{1,2}/\d{2,4}),\s*(?P<time>\d{1,2}:\d{2}:\d{2})\]\s*(?P<body>.*)$')
def parse_whatsapp(text):
    items=[]; current=None
    for line in text.replace('\r\n','\n').split('\n'):
        m=P1.match(line) or P2.match(line)
        if m:
            if current: items.append(current)
            body=m['body']; sender,sep,message=body.partition(': ')
            current={'sender':sender if sep else 'System','text':message if sep else body,'timestamp':parse_time(m['date'],m['time'])}
        elif current and line.strip(): current['text']+='\n'+line
    if current: items.append(current)
    return [x for x in items if not is_system(x['text']) and '<media omitted>' not in x['text'].lower()]
def parse_time(date,time):
    for f in ('%d/%m/%y %I:%M %p','%d/%m/%Y %I:%M %p','%d/%m/%y %H:%M:%S','%d/%m/%Y %H:%M:%S'):
        try:return datetime.strptime(f'{date} {time.upper()}',f)
        except ValueError: pass
    return None
def is_system(text):
    low=text.lower(); return 'end-to-end encrypted' in low or re.search(r'\b(joined|left|added|removed)\b',low) is not None
