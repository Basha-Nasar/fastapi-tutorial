import uuid
from fastapi  import APIRouter, HTTPException, status, Query
from app.schemas import UserCreate, UserOut, UserStatus, UserUpdate
from app.storage import load_data, save_data



router = APIRouter( prefix = "/api/v1/users" , tags = ['users'])


@router.get("/", response_model = list[UserOut])
async def get_users():
    """Retrive all users"""
    users = load_data()
    return users

@router.post("/", response_model = UserOut, status_code = status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    """Create new user"""
    users = load_data()
    new_user = UserOut(
        id= str(uuid.uuid4()),
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        status=UserStatus.active
    )
    users.append(new_user)
    save_data(users)
    return new_user


@router.get('/search', response_model = list[UserOut])
def search_users(query : str = Query(..., min_length=1)):
    users = load_data()
    result = []
    for user in users:
        if query.lower() in user['first_name'].lower() or query.lower() in user['last_name'].lower() or query.lower() in user['email'].lower():
            result.append(user)
    return result


@router.get('/{user_id}', response_model=UserOut)
def get_user(user_id : str):
    """Retrive user by id"""
    users = load_data()
    for user in users:
        if user['id'] == user_id:
            return user
    raise HTTPException(status_code= status.HTTP_404_NOT_FOUND , detail = "User not found")

@router.put('/{user_id}' , response_model=UserOut)
def update_user(user_id : str, payload : UserUpdate):
    users = load_data()
    for index, user in enumerate(users):
        if user['id'] == user_id:
            updated_user = user.copy()
            if payload.first_name is not None:
                updated_user['first_name'] = payload.first_name
            if payload.last_name is not None:
                updated_user['last_name'] = payload.last_name
            if payload.email is not None:
                updated_user['email'] = payload.email
            if payload.status is not None:
                updated_user['status'] = payload.status
            users[index] = updated_user
            save_data(users)
            return updated_user
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")




@router.delete('/{user_id}', response_model= UserOut)
def delete_user(user_id : str):
    users = load_data()
    for index, user in enumerate(users):
        if user['id'] == user_id:
            deleted_user = user.copy()
            users.pop(index)
            save_data(users)
            return deleted_user
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail="User Not Found")