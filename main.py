from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List, Optional
from pydantic import BaseModel
from markdown import markdown
import os
import glob

# TODO - Add sqlite3 database: database.py, models.py and crud.py

app = FastAPI()

templates = Jinja2Templates(directory='templates')

class Page_IN(BaseModel):
    contents: str

class Page_OUT(Page_IN):
    title: str

@app.get('/')
async def root():
    entries = [os.path.basename(x)[:-3].upper() for x in glob.glob('./data/*.md')]
    return {"Entries": entries}

def fetch_markdown(title: str):
    pagemd = os.path.join('./data', title+'.md')
    if not os.path.exists(pagemd):
        raise HTTPException(status_code=404, detail=f"No entry for {title.upper()}.")
    with open(pagemd, 'r') as file:
        contents = file.read()
    return Page_OUT(title=title.upper(), contents=contents)

@app.get('/{title}', response_model=Page_OUT)
async def get_markdown(title: str):
    page = fetch_markdown(title)
    return page

@app.post('/{title}', response_model=Page_OUT)
async def create_entry(title: str, contents: Page_IN):
    pagemd = os.path.join('./data', title.lower()+'.md')
    try: 
        with open(pagemd, 'w') as file:
            file.write(contents.contents)
    except:
        raise HTTPException(status_code=404, detail=f"Created no entry for {title}.")
    return Page_OUT(title=title.upper(), contents=contents.contents)

@app.get('/web/{title}', response_class=HTMLResponse)
async def get_webpage(request: Request, title: str):
    page = fetch_markdown(title=title)
    print(type(markdown(page.contents)))
    return templates.TemplateResponse('wakeypage.html', 
                {"request": request, 
                "title": page.title, 
                "content": markdown(page.contents)})