import time

bait_time = time.time()
for x in range(10):

    time.sleep(1.6)

    now = time.time()

    if now - bait_time < 10:
        print(x, now, bait_time, now - bait_time)
    else:
        print(now, bait_time, now - bait_time)