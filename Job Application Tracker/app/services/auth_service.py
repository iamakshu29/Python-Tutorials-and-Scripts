# Create and return Token with expiration time.
def create_jwt(id: int, db: DbDependency) -> str | None:

    # get user_details using the id
    get_details = db.query(User).filter(User.id == id).first()

    if get_details:
        payload = {"sub": get_details.email, "id": id, "role": get_details.role}

        # add 20 minutes token expiration time
        expires = datetime.now(timezone.utc) + timedelta(minutes=20)
        payload.update({"exp":expires})

        return jwt.encode(payload,SECRET_KEY,ALGORITHM)