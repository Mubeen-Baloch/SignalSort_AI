import re,hashlib
URL=re.compile(r'https?://\S+|www\.\S+',re.I)
def prepare(item):
    raw=item['text'].strip(); urls=URL.findall(raw); clean=URL.sub('',raw); clean=' '.join(clean.split())
    if len(clean.split())<4:return None
    return {**item,'raw_text':raw,'clean_text':clean,'urls':urls,'content_hash':hashlib.sha256(clean.lower().encode()).hexdigest()}
def chunks(item, limit=1200):
    text=item['clean_text']
    if len(text)<=limit:return [item]
    return [{**item,'clean_text':text[i:i+limit],'raw_text':text[i:i+limit],'content_hash':hashlib.sha256((item['content_hash']+str(i)).encode()).hexdigest()} for i in range(0,len(text),limit)]
