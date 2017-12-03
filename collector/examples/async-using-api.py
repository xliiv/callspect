# add code here
import callspectpy, os
callspectpy.trace2file_start(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), 'callspect.txt')
)


import asyncio


async def say(what, when):
    await asyncio.sleep(when)


loop = asyncio.get_event_loop()
loop.run_until_complete(say('hello world', 1))
loop.close()


# .. and here
callspectpy.trace2file_stop()
