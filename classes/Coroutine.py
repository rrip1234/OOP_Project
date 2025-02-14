import time

coroutines = []

def startCoroutine(coroutine):
    coroutines.append(coroutine)

def updateCoroutine():
    for coroutine in coroutines:
        try:
            next(coroutine)
        except StopIteration:
            coroutines.remove(coroutine)

def waitForSeconds(seconds):
    start_time = time.time()
    while time.time() - start_time < seconds:
        yield
