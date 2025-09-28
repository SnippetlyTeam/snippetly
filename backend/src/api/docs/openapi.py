from pydantic import BaseModel


class ErrorResponseSchema(BaseModel):
    detail: str


def aggregate_examples(
    description: str,
    examples: dict[str, str],
    model: type = ErrorResponseSchema,
) -> dict:
    return {
        "description": description,
        "model": model,
        "content": {
            "application/json": {
                "examples": {
                    name: {
                        "summary": name.replace("_", " ").capitalize(),
                        "value": {"detail": detail},
                    }
                    for name, detail in examples.items()
                }
            }
        },
    }
