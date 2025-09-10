from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from appservice import UrlResponse, UrlRecord, UrlRequest

app = FastAPI()

origins = [ "http://localhost:3000" ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

from appservice import UrlShortenerService

service = UrlShortenerService()

@app.post("/api/shorten", response_model=UrlResponse)
async def shorten_url(request: UrlRequest):
    long_url = str(request.url)
    try:
        validate(long_url)
    except Exception:
        raise HTTPException(400, 'validation failed')


    existing_url = service.get_existing_short_url(long_url)

    if existing_url:
        return UrlResponse(code=existing_url, short_url=existing_url, expires=existing_url)

    code: str = await service.create_code()
    expires: datetime = None

    if request.expires and request.expires > 0:
        expires = service.now() + timedelta(seconds=request.expires)

    service.store[code] = UrlRecord(
        original_url=long_url,
        short_code=code,
        created=datetime.now(),
        expires=expires
    )

    return UrlResponse(code=code, short_url=service.get_short_url(code), expires=expires)

# { code: urlShortCode, createdAt: .. }
# { username: .., urlIds: { id1, id2..} }
@app.get("/api/{short_code}")
def redirect(short_code: str):
    if short_code in service.store.keys():
        return RedirectResponse(url=service.store[short_code].original_url)
    raise HTTPException(status_code=404, detail=f"Short {str} code not found")

def validate(url: str):
    # starts http:// or https://
    # contains at least one dot
    # if lastIndexOf / malware.exe
    if not url.startswith('http://') and not url.startswith('https://'):
        raise Exception()
