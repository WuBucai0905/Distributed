## 状态管理器

集中管理



requests队列集中管理

> scheduler 放在一个 query里面， query是放在内存里面。所以要做 集中管理

去重集中管理

> 去重的扩展 是通过内存的set集合。



拷贝 `scrapy_redis` 的包集成到项目中

`RedisMixin`类的

`setup_redis`方法 对每一个spider 会设置一个 `redis_key`

`next_requests` 方法

- `scrapy` 获取 `next_requests` 时候是通过 `scrapy.scheduler` 来完成的。队列维持在内存中









`dupefilter.py`

去重的文件

继承 `BaseDupeFilter`类

`__init__`

`from_settings`方法中

- server 调用了 `connection.py` 的 `get_redis_from_settings(settings)`
  - 初始化 就生成server，连接到 `redis`
- key 传入 `defaults`中的 `DUPFEILTER_KEY`
- debug 直接识别 `DUPFEILTER_DEBUG`
  - 会将 过滤信息打印出来



`request_seen`方法中

- 调用 `request_fingerprint`
- 将 指纹 加入 `self.key`里面
  - 成功返回1， 失败返回0





`picklecompat.py`

序列化的文件

调用`pickle`， 是python的一个标准库





`pipelines.py`

将 `item` 放入 `redis` 中

`RedisPiprline`类

 入口 `from_settings`

- 先初始化 server
- 初始化 `redis_items_key`
- 初始化 `REDIS_ITEMS_SERIALIZER`
  - serializer 将传过来的 item 进行序列化再放入 redis中

`from_settings` 被 `from_crawler`调用



`process_item`方法

- `defetToThread` 异步化操作，放入另外线程中去调用
  - --- 为了高效， 后边 的 item 不会受到影响

该过程 可以不放在 redis 上运行







`queue.py`

与 scheduler调度来一起使用

Base

`FifoQueue`类

放队列放入队头， 取队列从队尾取



`PriorityQueue`类

默认使用该类

push

- `zcard` 有序集合
- `score`分数优先级

pop

- `zrange`



`LifoQueue`类

