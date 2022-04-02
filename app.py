from hashlib import sha384
from fastapi import FastAPI, APIRouter, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from tortoise.contrib.fastapi import register_tortoise
import os
from db import User, UserSchema, UserUpdateSchema, Store, LoginUserSchema

app = FastAPI()
api = APIRouter(prefix="/api", tags=["User"])


render = Jinja2Templates(directory="templates").TemplateResponse

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

register_tortoise(
    app,
    db_url=os.getenv('DATABASE_URI') or "sqlite://db.sqlite3",
    modules={"Table": ['db']},
    generate_schemas=True,
)

print(os.getenv("DATABASE_URI"))


@app.get('/')
async def HomeTemplate(request: Request):
    return render('index.html', {"request": request})


@api.get('/')
async def GetAllUser():
    return {
        "User": await User.all(),
        "Store": await Store.all()
    }


@api.post('/create')
async def SaveUser(body: UserSchema):
    StoreObj = await Store.create(Name=body.StoreRef)
    dataObj = {**body.dict(), "StoreRef": StoreObj}
    UserObj = await User.create(**dataObj)
    return {
        "Response": True, "Obj": {
            "Store": StoreObj.Name,
            "StoreRef_id": StoreObj.id,

            "Id": UserObj.id,
            "Currency": UserObj.Currency,
            "Admin": UserObj.Admin,
            "Name": UserObj.Name,
            "Username": UserObj.Username,
            "Login": UserObj.Login
        }
    }


@api.post('/login')
async def SaveUser(body: LoginUserSchema):
    UserObj = await User.get_or_none(
        Username=body.Username,
        Password=sha384(bytes(body.Password, "utf-8")).hexdigest(),
        Actif=True
    )
    if UserObj:
        StoreObj = await Store.get_or_none(id=UserObj.StoreRef_id)
        await UserObj.save()
        return {
            "Response": True, "Obj": {
                "Store": StoreObj.Name,
                "StoreRef_id": StoreObj.id,

                "Id": UserObj.id,
                "Currency": UserObj.Currency,
                "Admin": UserObj.Admin,
                "Name": UserObj.Name,
                "Username": UserObj.Username,
                "Login": UserObj.Login
            }
        }
    else:
        return {"Response": False, "Obj": {}}


@api.get('/get_personnel/{id}')
async def Get_Personnel(id):
    return await User.filter(StoreRef_id=id)


@api.post('/savePersonnel')
async def savePersonnel(body: UserSchema):
    Obj = await User.create(**body.dict())
    return Obj


@api.put('/updatePersonnel/{id_user}')
async def UpdateUser(id_user, body: UserUpdateSchema):
    updated = await User.filter(id=id_user).update(**body.dict(exclude_none=True))
    if updated:
        return {"Updated": updated}
    return {}


app.include_router(api)
