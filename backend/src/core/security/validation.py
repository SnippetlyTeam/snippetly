def password_validation(value: str) -> str:
    message = (
        "Password can’t be blank. Password should "
        "contain at least one capital letter, "
        "one number, and one special character."
    )

    if (
        not value
        or value.strip() == ""
        or len(value) < 8
        or len(value) > 30
        or any(c.isspace() or not c.isprintable() for c in value)
        or not any(c.isupper() for c in value)
        or not any(c.isdigit() for c in value)
        or not any(c in "@$!%*?&" for c in value)
    ):
        raise ValueError(message)

    return value


def username_validation(value: str) -> str:
    if (
        len(value) < 3
        or len(value) > 40
        or not value[0].isalpha()
        or any(not c.isalnum() for c in value)
        or any(c.isspace() or not c.isprintable() for c in value)
    ):
        raise ValueError(
            "Username must start with a letter, have "
            "no spaces, and be 3 - 40 characters."
        )
    return value
