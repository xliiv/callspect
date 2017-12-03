import asyncio


async def say(what, when):
    await asyncio.sleep(when)


loop = asyncio.get_event_loop()
loop.run_until_complete(say('hello world', 1))
loop.close()
