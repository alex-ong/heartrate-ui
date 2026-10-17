import inspect


async def await_if_required(value):
    if inspect.isawaitable(value):
        return await value
    return value
