# IP代理池

## 准备工作

aiohttp、 requests、 redis、 flask

## 架构

![img](https://qiniu.cuiqingcai.com/2019-08-02-060342.jpg)

基本模块分为四块，获取模块、存储模块、检查模块、接口模块。

- 获取模块 需要定时去各大代理网站抓取代理，抓取完之后将可用代理保存到数据库中。
- 存储模块 负责存储抓取下来的代理。保证代理不重复，标识代理的可用情况，动态实时处理每个代理，所以说，一种比较高效和方便的存储方式就是使用 Redis 的 Sorted Set，也就是有序集合。
- 检测模块 需要定时将数据库中的代理进行检测，设置一个检测链接，另外我们需要标识每一个代理的状态，如设置分数标识，100 分代表可用，分数越少代表越不可用，检测一次如果可用，我们可以将其立即设置为100 满分，也可以在原基础上加 1 分，当不可用，可以将其减 1 分，当减到一定阈值后就直接从数据库移除。通过这样的标识分数，我们就可以区分出代理的可用情况，选用的时候会更有针对性。
- 接口模块 需要用 API 来提供对外服务的接口，其实我们可以直接连数据库来取，但是这样就需要知道数据库的连接信息，不太安全，而且需要配置连接，所以一个比较安全和方便的方式就是提供一个 Web API 接口，通过访问接口即可拿到可用代理。另外由于可用代理可能有多个，我们可以提供随机返回一个可用代理的接口，这样保证每个可用代理都可以取到，实现负载均衡。

## 实现

### 存储模块

存储在这里我们使用 Redis 的有序集合，集合的每一个元素都是不重复的，这样的一个代理就是集合的一个元素。

另外有序集合的每一个元素还都有一个分数字段，分数是可以重复的，是一个浮点数类型，也可以是整数类型。该集合会根据每一个元素的分数对集合进行排序，数值小的排在前面，数值大的排在后面，这样就可以实现集合元素的排序了。

设置分数可以作为我们判断一个代理可用不可用的标志，我们将 100 设为最高分，代表可用，0 设为最低分，代表不可用。从代理池中获取代理的时候会随机获取分数最高的代理，注意这里是随机，这样可以保证每个可用代理都会被调用到。

**设置分数规则**

- 分数 100 为可用，检测器会定时循环检测每个代理可用情况，一旦检测到有可用的代理就立即置为 100，检测到不可用就将分数减 1，减至 0 后移除。
- 新获取的代理添加时将分数置为 10，当测试可行立即置 100，不可行分数减 1，减至 0 后移除。

**规则设置原因**

- 当检测到代理可用时立即置为 100，这样可以保证所有可用代理有更大的机会被获取到。你可能会说为什么不直接将分数加 1 而是直接设为最高 100 呢？设想一下，我们有的代理是从各大免费公开代理网站获取的，如果一个代理并没有那么稳定，平均五次请求有两次成功，三次失败，如果按照这种方式来设置分数，那么这个代理几乎不可能达到一个高的分数，也就是说它有时是可用的，但是我们筛选是筛选的分数最高的，所以这样的代理就几乎不可能被取到，当然如果想追求代理稳定性的化可以用这种方法，这样可确保分数最高的一定是最稳定可用的。但是在这里我们采取可用即设置 100 的方法，确保只要可用的代理都可以被使用到。
- 当检测到代理不可用时，将分数减 1，减至 0 后移除，一共 100 次机会，也就是说当一个可用代理接下来如果尝试了 100 次都失败了，就一直减分直到移除，一旦成功就重新置回 100，尝试机会越多代表将这个代理拯救回来的机会越多，这样不容易将曾经的一个可用代理丢弃，因为代理不可用的原因可能是网络繁忙或者其他人用此代理请求太过频繁，所以在这里设置为 100 级。
- 新获取的代理分数设置为 10，检测如果不可用就减 1，减到 0 就移除，如果可用就置 100。由于我们很多代理是从免费网站获取的，所以新获取的代理无效的可能性是非常高的，可能不足 10%，所以在这里我们将其设置为 10，检测的机会没有可用代理 100 次那么多，这也可以适当减少开销。

```
MAX_SCORE = 100
MIN_SCORE = 0
INITIAL_SCORE = 10
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_PASSWORD = None
REDIS_KEY = 'proxies'
 
import redis
from random import choice
 
class RedisClient(object):
    def __init__(self, host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD):
        """
        初始化
        :param host: Redis 地址
        :param port: Redis 端口
        :param password: Redis密码
        """
        self.db = redis.StrictRedis(host=host, port=port, password=password, decode_responses=True)
 
    def add(self, proxy, score=INITIAL_SCORE):
        """
        添加代理，设置分数为最高
        :param proxy: 代理
        :param score: 分数
        :return: 添加结果
        """
        if not self.db.zscore(REDIS_KEY, proxy):
            return self.db.zadd(REDIS_KEY, score, proxy)
 
    def random(self):
        """
        随机获取有效代理，首先尝试获取最高分数代理，如果不存在，按照排名获取，否则异常
        :return: 随机代理
        """
        result = self.db.zrangebyscore(REDIS_KEY, MAX_SCORE, MAX_SCORE)
        if len(result):
            return choice(result)
        else:
            result = self.db.zrevrange(REDIS_KEY, 0, 100)
            if len(result):
                return choice(result)
            else:
                raise PoolEmptyError
 
    def decrease(self, proxy):
        """
        代理值减一分，小于最小值则删除
        :param proxy: 代理
        :return: 修改后的代理分数
        """
        score = self.db.zscore(REDIS_KEY, proxy)
        if score and score > MIN_SCORE:
            print('代理', proxy, '当前分数', score, '减1')
            return self.db.zincrby(REDIS_KEY, proxy, -1)
        else:
            print('代理', proxy, '当前分数', score, '移除')
            return self.db.zrem(REDIS_KEY, proxy)
 
    def exists(self, proxy):
        """
        判断是否存在
        :param proxy: 代理
        :return: 是否存在
        """
        return not self.db.zscore(REDIS_KEY, proxy) == None
 
    def max(self, proxy):
        """
        将代理设置为MAX_SCORE
        :param proxy: 代理
        :return: 设置结果
        """
        print('代理', proxy, '可用，设置为', MAX_SCORE)
        return self.db.zadd(REDIS_KEY, MAX_SCORE, proxy)
 
    def count(self):
        """
        获取数量
        :return: 数量
        """
        return self.db.zcard(REDIS_KEY)
 
    def all(self):
        """
        获取全部代理
        :return: 全部代理列表
        """
        return self.db.zrangebyscore(REDIS_KEY, MIN_SCORE, MAX_SCORE)
```

首先定义了一些常量，如 MAX_SCORE、MIN_SCORE、INITIAL_SCORE 分别代表最大分数、最小分数、初始分数。REDIS_HOST、REDIS_PORT、REDIS_PASSWORD 分别代表了 Redis 的连接信息，即地址、端口、密码。REDIS_KEY 是有序集合的键名，可以通过它来获取代理存储所使用的有序集合。

接下来定义了一个 RedisClient 类，用以操作 Redis 的有序集合，其中定义了一些方法来对集合中的元素进行处理，主要功能如下：

- **init**() 方法是初始化的方法，参数是Redis的连接信息，默认的连接信息已经定义为常量，在 **init**() 方法中初始化了一个 StrictRedis 的类，建立 Redis 连接。这样当 RedisClient 类初始化的时候就建立了Redis的连接。
- add() 方法向数据库添加代理并设置分数，默认的分数是 INITIAL_SCORE 也就是 10，返回结果是添加的结果。
- random() 方法是随机获取代理的方法，首先获取 100 分的代理，然后随机选择一个返回，如果不存在 100 分的代理，则按照排名来获取，选取前 100 名，然后随机选择一个返回，否则抛出异常。
- decrease() 方法是在代理检测无效的时候设置分数减 1 的方法，传入代理，然后将此代理的分数减 1，如果达到最低值，那么就删除。
- exists() 方法判断代理是否存在集合中
- max() 方法是将代理的分数设置为 MAX_SCORE，即 100，也就是当代理有效时的设置。
- count() 方法返回当前集合的元素个数。
- all() 方法返回所有的代理列表，供检测使用。

定义好了这些方法，我们可以在后续的模块中调用此类来连接和操作数据库，非常方便。如我们想要获取随机可用的代理，只需要调用 random() 方法即可，得到的就是随机的可用代理。

### 获取模块

### 检测模块

在获取模块中，我们已经成功将各个网站的代理获取下来了，然后就需要一个检测模块来对所有的代理进行一轮轮的检测，检测可用就设置为 100，不可用就分数减 1，这样就可以实时改变每个代理的可用情况，在获取有效代理的时候只需要获取分数高的代理即可。

由于代理的数量非常多，为了提高代理的检测效率，我们在这里使用异步请求库 **Aiohttp** 来进行检测。

### 接口模块

通过上述三个模块我们已经可以做到代理的获取、检测和更新了，数据库中就会以有序集合的形式存储各个代理还有对应的分数，分数 100 代表可用，分数越小代表越不可用。

但是我们怎样来方便地获取可用代理呢？用 RedisClient 类来直接连接 Redis 然后调用 random() 方法获取当然没问题，这样做效率很高，但是有这么几个弊端：

- 需要知道 Redis 的用户名和密码，如果这个代理池是给其他人使用的就需要告诉他连接的用户名和密码信息，这样是很不安全的。
- 代理池如果想持续运行需要部署在远程服务器上运行，如果远程服务器的 Redis 是只允许本地连接的，那么就没有办法远程直连 Redis 获取代理了。
- 如果爬虫所在的主机没有连接 Redis 的模块，或者爬虫不是由 Python 语言编写的，那么就无法使用 RedisClient 来获取代理了。
- 如果 RedisClient 类或者数据库结构有更新，那么在爬虫端还需要去同步这些更新。

综上考虑，为了使得代理池可以作为一个独立服务运行，我们最好增加一个接口模块，以 Web API 的形式暴露可用代理。

这样获取代理只需要请求一下接口即可，以上的几个缺点弊端可以解决。

### 调度模块

将上面模块通过多进程的形式运行起来



原理讲解： https://cuiqingcai.com/7048.html

github: https://github.com/Python3WebSpider/ProxyPool