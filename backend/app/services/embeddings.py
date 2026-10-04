import hashlib, math
from ..config import settings
_model=None
def _fallback(text):
    v=[0.0]*384
    for word in text.lower().split():
        i=int(hashlib.sha256(word.encode()).hexdigest(),16)%384; v[i]+=1
    n=math.sqrt(sum(x*x for x in v)) or 1
    return [x/n for x in v]
def embed_texts(texts):
    global _model
    try:
        if _model is None:
            from fastembed import TextEmbedding
            _model=TextEmbedding(model_name=settings.embedding_model)
        return [list(v) for v in _model.embed(texts)]
    except Exception:
        return [_fallback(x) for x in texts]
