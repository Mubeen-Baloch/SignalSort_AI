import json,re,httpx,asyncio,logging
from ..config import settings
log=logging.getLogger(__name__)
CATEGORIES=['Opportunity/Collaboration','Job/Internship','Event/Announcement','Resource/Learning','Question/Help','Discussion','Social/Noise']
def fallback(text):
    t=text.lower(); category='Discussion'
    if any(x in t for x in ['internship','hiring','job opening','paid role']):category='Job/Internship'
    elif any(x in t for x in ['hackathon','scholarship','fellowship','workshop']):category='Event/Announcement'
    elif any(x in t for x in ['course','tutorial','resource','learn']):category='Resource/Learning'
    elif any(x in t for x in ['need','looking for','seeking','collaborat','contributor','developer']):category='Opportunity/Collaboration'
    elif len(t.split())<10 or any(x in t for x in ['good morning','thanks','hello everyone','😂']):category='Social/Noise'
    skills=[x for x in ['python','react','mobile','ui/ux','machine learning','data science','ai','healthcare','developer'] if x in t]
    intents=[x for x in ['healthcare tech','internship','hackathon','scholarship'] if x in t]
    return {'category':category,'summary':text[:220], 'entities':{'projects':['Cerebral Palsy healthcare app'] if 'cerebral palsy' in t else [],'skills':skills,'intents':intents}}
def parse_json(raw, originals):
    raw=re.sub(r'^```(?:json)?|```$','',raw.strip(),flags=re.M).strip()
    try:
        data=json.loads(raw); data=data.get('messages',data) if isinstance(data,dict) else data
        return [x if isinstance(x,dict) and x.get('category') in CATEGORIES else fallback(originals[i]) for i,x in enumerate(data)]
    except Exception:return [fallback(x) for x in originals]
async def classify(texts):
    if not settings.llm_api_key:return [fallback(x) for x in texts]
    prompt='Return JSON array only. Classify each text into one fixed category: '+', '.join(CATEGORIES)+'. Return category, summary, entities with projects, skills, intents arrays. Texts: '+json.dumps(texts)
    for attempt in range(2):
        try:
            async with httpx.AsyncClient(timeout=35) as c:
                r=await c.post(settings.llm_base_url.rstrip('/')+'/chat/completions',headers={'Authorization':f'Bearer {settings.llm_api_key}'},json={'model':settings.llm_model,'messages':[{'role':'user','content':prompt}],'temperature':0.1})
                if r.status_code==429: await asyncio.sleep(2**attempt); continue
                r.raise_for_status(); return parse_json(r.json()['choices'][0]['message']['content'],texts)
        except Exception as e: log.warning('llm fallback: %s',e)
    return [fallback(x) for x in texts]
