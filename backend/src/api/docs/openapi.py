from pydantic import BaseModel


class DetailErrorResponseSchema(BaseModel):
    detail: str


class ErrorResponseSchema(BaseModel):
    error: str


def create_json_examples(
    description: str,
    examples: dict[str, dict],
    model: type = DetailErrorResponseSchema,
) -> dict:
    return {
        "description": description,
        "model": model,
        "content": {
            "application/json": {
                "examples": {
                    name: {
                        "summary": name.replace("_", " ").capitalize(),
                        "value": value,
                    }
                    for name, value in examples.items()
                }
            }
        },
    }


def create_error_examples(
    description: str,
    examples: dict[str, str],
    model: type = DetailErrorResponseSchema,
) -> dict:
    error_examples = {
        name: {"detail": detail} for name, detail in examples.items()
    }
    return create_json_examples(description, error_examples, model)
