from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
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

@app.get('/', tags=['REST API'])
async def root():
    """
    The root API end-point, shows a list of Wakey entries.
    """
    entries = [os.path.basename(x)[:-3].upper() for x in glob.glob('./data/*.md')]
    return {"Entries": entries}

def fetch_markdown(title: str):
    """
    Returns a Wakey page "as is" in markdown,
    given the title. Raises an exception 
    when it finds no entry for the title supplied. 
    """
    pagemd = os.path.join('./data', title+'.md')
    if not os.path.exists(pagemd):
        raise HTTPException(status_code=404, detail=f"No entry for {title.upper()}.")
    with open(pagemd, 'r') as file:
        contents = file.read()
    return Page_OUT(title=title.upper(), contents=contents)

@app.get('/{title}', response_model=Page_OUT, tags=['REST API'])
async def get_markdown(title: str):
    """
    The API end-point for a Wakey page.
    Serves the page "as is" in markdown.
    """
    page = fetch_markdown(title)
    return page

def write_markdown(title, contents):
    pagemd = os.path.join('./data', title.lower()+'.md')
    try: 
        with open(pagemd, 'w') as file:
            file.write(contents)
    except:
        raise HTTPException(status_code=404, detail=f"Created no entry for {title}.")
    return pagemd

@app.post('/{title}', response_model=Page_OUT, tags=['REST API'])
async def create_entry(title: str, contents: Page_IN):
    """
    Creates a Wakey page wuth title and description,
    with the description in markdown. 
    Creates a file with .md extension and 
    named after the title.
    """

    write_markdown(title=title, contents=contents.contents)
    return Page_OUT(title=title.upper(), contents=contents.contents)

@app.get('/web/{title}', response_class=HTMLResponse, tags=['SPA Demo'])
async def get_webpage(request: Request, title: str):
    """
    For Demonstration Only! 
    Use a client-side SPA to consume API end-points,
    with backend services depoloyed in containers.
    *
    Shows the webpage for the requested entry,
    searching by title and rendering markdown as HTML.
    The HTTP request is required in web mode.
    """        
    page = fetch_markdown(title=title)
    return templates.TemplateResponse('wakeypage.html', 
                {"request": request, 
                "title": page.title, 
                "content": markdown(page.contents)})

@app.get('/web/form/', response_class=HTMLResponse, tags=['SPA Demo'])
async def get_webform(request: Request):
    """
    For Demonstration Only! 
    Use a client-side SPA to consume API end-points,
    with backend services depoloyed in containers.
    *
    Serves a web form for a new entry.
    The form is POSTed to a route 
    that extracts form paramters and
    creates a new entry.
    Does not check for duplication so
    an existing entry will be over-written. 
    """
    return templates.TemplateResponse('wakeymake.html', {"request": request})

@app.post('/web/create', response_model=Page_OUT, tags=['SPA Demo'])
async def make_entry(title: str = Form(...), contents: str=Form(...)):
    """
    For Demonstration Only! 
    Use a client-side SPA to consume API end-points,
    with backend services depoloyed in containers.
    *
    Creates a new entry from a form POSTed by user.
    """
    write_markdown(title=title, contents=contents)
    return Page_OUT(title=title.upper(), contents=contents)
    