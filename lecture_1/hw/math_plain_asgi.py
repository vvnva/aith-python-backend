from typing import Any, Awaitable, Callable
from urllib.parse import parse_qs
import json
import math

async def bad_request(send):
    await send({"type": "http.response.start", "status": 400, 'headers': [(b'content-type', b'text/plain')]})
    await send({"type": "http.response.body", "body": b" Bad Request"})

async def unprocessable_entity(send):
    await send({"type": "http.response.start", "status": 422, 'headers': [(b'content-type', b'text/plain')]})
    await send({"type": "http.response.body", "body": b" Unprocessable Entity"})

async def good_response(send, response_body):
    await send({"type": "http.response.start", "status": 200, "headers": [ (b"content-type", b"application/json")]})
    await send({"type": "http.response.body", "body": response_body})

async def not_found(send):
    await send({"type": "http.response.start", "status": 404, "headers": [ (b"content-type", b"application/json")]})
    await send({"type": "http.response.body", "body": b"Not Found"})


async def app(
        scope: dict[str, Any],
        receive: Callable[[], Awaitable[dict[str, Any]]],
        send: Callable[[dict[str, Any]], Awaitable[None]]) -> None:
    assert scope['type'] == 'http'
    if scope['method'] == 'GET':
        path = scope.get('path')
        if path.startswith('/factorial'):
            num_json = parse_qs(scope.get('query_string').decode())
            try:
                n = int(num_json.get('n')[0])
                if n>=0:
                    result = math.factorial(n)
                    response_body = json.dumps({"result": result}).encode('utf-8')
                    await good_response(send, response_body)
                else:
                    await bad_request(send)
            except (TypeError, ValueError):
                await unprocessable_entity(send)


        elif path.startswith('/fibonacci'):
            num_str = path.split('/')[-1]
            try:
                n = int(num_str)
                if n>=0:
                    a, b = 0, 1
                    for _ in range(n):
                        a, b = b, a + b
                    fibonacci = b
                    response_body = json.dumps({"result": fibonacci}).encode('utf-8')
                    await good_response(send, response_body)
                else:
                    await bad_request(send)
            except (TypeError, ValueError):
                await unprocessable_entity(send)


        elif path.startswith('/mean'):
            message = await receive()
            body = message.get('body', None).decode()
            try:
                numbers = json.loads(body)
                if not numbers:
                    await bad_request(send)
                elif not all(isinstance(x, (int, float)) for x in numbers):
                    await unprocessable_entity(send)
                else:
                    mean_value = sum(numbers) / len(numbers)
                    response_body = json.dumps({"result": mean_value}).encode('utf-8')
                    await good_response(send, response_body)
            except:
                await unprocessable_entity(send)

        else:
            await not_found(send)
    else:
        await not_found(send)
