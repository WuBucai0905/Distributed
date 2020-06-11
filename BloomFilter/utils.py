import uuid
import math
import time
import redis

# 使用分布式锁的意义：高并发情境下减少错判的情况
# 怎么减少错判？： 事务。使用watch、multi、exec等。； 非事务型流水线。（将一系列命令打包再发送给redis）；  分布式锁。

# 获取锁
def acquire_lock_with_timeout(conn, lockname, acquire_timeout=5, lock_timeout=10):
    # 128位随机标识符
    identifier = str(uuid.uuid4())
    lockname = 'lock:' + lockname
    lock_timeout = int(math.ceil(lock_timeout))  # 确保传给exprie是整数
    end = time.time() + acquire_timeout
    # 在规定的时间内不断的重试
    while time.time() < end:
        # setnx key值设为value，key值存在则不进行任何操作
        if conn.setnx(lockname, identifier):
            # 过期时间后自动删除
            conn.expire(lockname, lock_timeout)
            return identifier
        # ttl
        elif not conn.ttl(lockname):  # 为没有设置超时时间的锁设置超时时间
            conn.expire(lockname, lock_timeout)

        time.sleep(0.001)
    return False


# 释放锁
def release_lock(conn, lockname, identifier):
    pipe = conn.pipeline(True)
    lockname = 'lock:' + lockname

    while True:
        try:
            pipe.watch(lockname)
            # 判断标志是否相同
            if str(pipe.get(lockname), encoding='utf-8') == identifier:
                pipe.multi()
                pipe.delete(lockname)
                pipe.execute()
                return True

            # 不同则直接退出 return False
            pipe.unwatch()
            break

        except redis.exceptions.WatchError:
            pass
    return False

# OOM command not allowed when used memory > 'maxmemory'
# 是redis默认的maxmemory限制了最大内存，在配置文件中修改参数即可。