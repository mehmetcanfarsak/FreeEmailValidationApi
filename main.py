from fastapi import FastAPI, HTTPException, status, Request, Query
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import EmailStr, BaseModel
from email_validator import validate_email
from typing import Union, List

from dotenv import load_dotenv

load_dotenv()
description_of_fastapi = """
`` Simple, reliable and Free email validation api. Thanks to https://github.com/JoshData/python-email-validator ``  

### [📝Test Now With Creating Your Alias](show-email-validation-form)

## Features and Advantages
* Completely free and without any limtis
* Check dns settings of email's domain
* Robust email syntax validation
* Deliverability validation
* Good for login forms or other uses related to identifying users
* Gives friendly error messages when validation fails
* Supports internationalized domain names
* Normalizes email addresses

## Deployment 💻 
You can deploy your own instance of FreeEmailValidationApi using the button below. You will need a [Deta](https://www.deta.sh/) account.      
> 
[![Click Here To Deploy Your Own FreeEmailValidationApi 💻️](https://button.deta.dev/1/svg)](https://go.deta.dev/deploy?repo=https://github.com/mehmetcanfarsak/FreeEmailValidationApi)   
  

**Project Github Page:** [https://github.com/mehmetcanfarsak/FreeEmailValidationApi](https://github.com/mehmetcanfarsak/FreeEmailValidationApi)

  
"""
app = FastAPI(title="📨 Free Email Validation Api", description=description_of_fastapi,
              contact={"url": "https://github.com/mehmetcanfarsak", "Name": "Mehmet Can Farsak"})

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates("templates")


class EmailValidationResponseModel(BaseModel):
    is_email_valid: bool
    domain: Union[str, None] = None
    original_email: str
    local_part: Union[str, None] = None
    ascii_local_part: Union[str, None] = None
    ascii_domain: Union[str, None] = None
    smtputf8: Union[bool, None] = None
    mx: list = []
    spf: Union[str, None] = None
    ascii_email: Union[str, None] = None


class BulkEmailsModel(BaseModel):
    emails: List[EmailStr]


@app.get("/", include_in_schema=False, response_class=RedirectResponse)
def root():
    return RedirectResponse("/docs")


@app.get("/show-email-validation-form", include_in_schema=False, response_class=HTMLResponse)
def show_email_validation_form(request: Request):
    return templates.TemplateResponse("show-email-validation-form.html", {"request": request})


@app.get("/validate-email", description="Validate Email", response_model=EmailValidationResponseModel,
         tags=["Validate Single Email"])
def validate_single_email(email: EmailStr = Query(example="user@example.com")):
    try:
        validation_response = validate_email(email)
        return EmailValidationResponseModel(is_email_valid=True, domain=validation_response.domain,
                                            original_email=validation_response.original_email,
                                            local_part=validation_response.local_part,
                                            ascii_local_part=validation_response.ascii_local_part,
                                            ascii_domain=validation_response.ascii_domain,
                                            smtputf8=validation_response.smtputf8,
                                            mx=validation_response.mx, spf=validation_response.spf,
                                            ascii_email=validation_response.ascii_email)
    except:
        return EmailValidationResponseModel(is_email_valid=False, original_email=email)


@app.post("/bulk-validate-emails", description="Bulk Validate Emails. Max 10 emails can be validated.",
          response_model=List[EmailValidationResponseModel], tags=["Bulk Validate"])
def bulk_validate_emails(emails: BulkEmailsModel):
    if (len(emails.emails) > 10):
        return HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Max 10 emails can be validated.")
    response = []
    for email in emails.emails:
        try:
            validation_response = validate_email(email)
            response.append(EmailValidationResponseModel(is_email_valid=True, domain=validation_response.domain,
                                                         original_email=validation_response.original_email,
                                                         local_part=validation_response.local_part,
                                                         ascii_local_part=validation_response.ascii_local_part,
                                                         ascii_domain=validation_response.ascii_domain,
                                                         smtputf8=validation_response.smtputf8,
                                                         mx=validation_response.mx, spf=validation_response.spf,
                                                         ascii_email=validation_response.ascii_email))
        except:
            response.append(EmailValidationResponseModel(is_email_valid=False, original_email=email))
            continue

    return response


@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse("static/favicon.ico")
