def create_user_data(faker):
    return {
        "email": faker.unique.email(),
        "username": faker.unique.user_name(),
        "password": faker.password(),
    }
