from app.services.parser import parse_whatsapp
from app.services.llm import parse_json
def test_parser_handles_multiline_and_system_messages():
 out=parse_whatsapp('12/03/24, 9:41 pm - Ada: A long useful community message here\nwith more detail\n12/03/24, 9:42 pm - Messages and calls are end-to-end encrypted')
 assert len(out)==1 and 'more detail' in out[0]['text']
def test_llm_json_fallback():
 out=parse_json('not json',['Looking for developers for a healthcare app'])
 assert out[0]['category']=='Opportunity/Collaboration'
