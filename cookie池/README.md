# Cookie池

- 自动生成cookies
- 定时检测cookies
- 提供随机cookies

## 架构

![img](https://user-gold-cdn.xitu.io/2018/4/10/162ae44b93a3787b?imageView2/0/w/1280/h/960/format/webp/ignore-error/1)

**四大基本模块**：存储模块、获取模块、接口模块、检测模块

- 存储模块负责存储每个账号的用户名密码以及每个账号对应的Cookies信息，同时还需要提供一些方法来实现方便的存取操作。
- 获取模块负责生成新的Cookies。此模块会从存储模块逐个拿取账号的用户名和密码，然后模拟登录目标页面，判断登录成功，就将Cookies返回并交给存储模块存储。
- 检测模块需要定时检测数据库中的Cookies。在这里我们需要设置一个检测链接，不同的站点检测链接不同，检测模块会逐个拿取账号对应的Cookies去请求链接，如果返回的状态是有效的，那么此Cookies没有失效，否则Cookies失效并移除。接下来等待生成模块重新生成即可。
- 接口模块需要用API来提供对外服务的接口。由于可用的Cookies可能有多个，我们可以随机返回Cookies的接口，这样保证每个Cookies都有可能被取到。Cookies越多，每个Cookies被取到的概率就会越小，从而减少被封号的风险

## 实现

### 存储模块

需要存储的内容无非就是账号信息和Cookies信息。

账号由用户名和密码两部分组成，我们可以存成用户名和密码的映射。

Cookies可以存成JSON字符串，但是我们后面得需要根据账号来生成Cookies。生成的时候我们需要知道哪些账号已经生成了Cookies，哪些没有生成。所以需要同时保存该Cookies对应的用户名信息，其实也是用户名和Cookies的映射。

这里就是两组映射，我们自然而然想到Redis的Hash，于是就建立两个Hash

![img](https://user-gold-cdn.xitu.io/2018/4/10/162ae44b93b6f6b1?imageView2/0/w/1280/h/960/format/webp/ignore-error/1)

![img](https://user-gold-cdn.xitu.io/2018/4/10/162ae44b93ebb35c?imageView2/0/w/1280/h/960/format/webp/ignore-error/1)

Hash的Key就是账号，Value对应着密码或者Cookies

**可扩展性**: 支持多平台的cookies池

**解决**：

Hash的名称可以做二级分类，例如存账号的Hash名称可以为accounts:weibo，Cookies的Hash名称可以为cookies:weibo。如要扩展知乎的Cookies池，我们就可以使用accounts:zhihu和cookies:zhihu

### 获取模块

负责获取各个账号信息并模拟登录，随后生成Cookies并保存。我们首先获取两个Hash的信息，看看账户的Hash比Cookies的Hash多了哪些还没有生成Cookies的账号，然后将剩余的账号遍历，再去生成Cookies即可。

这里主要逻辑就是找出那些还没有对应Cookies的账号，然后再逐个获取Cookies

```
for username in accounts_usernames:
    if not username in cookies_usernames:
        password = self.accounts_db.get(username)
        print('正在生成Cookies', '账号', username, '密码', password)
        result = self.new_cookies(username, password)
```

获取模块里我们可以根据不同的状态码做不同的处理。

- 例如状态码为1的情况，表示成功获取Cookies，我们只需要将Cookies保存到数据库即可。
- 如状态码为2的情况，代表用户名或密码错误，那么我们就应该把当前数据库中存储的账号信息删除。
- 如状态码为3的情况，则代表登录失败的一些错误，此时不能判断是否用户名或密码错误，也不能成功获取Cookies，那么简单提示再进行下一个处理即可

### 检测模块

解决Cookies失效的问题

- 时间太长导致Cookies失效
- Cookies使用太频繁导致无法正常请求网页

定时检测模块，它负责遍历池中的所有Cookies，同时设置好对应的检测链接，我们用一个个Cookies去请求这个链接。如果请求成功，或者状态码合法，那么该Cookies有效；如果请求失败，或者无法获取正常的数据，比如直接跳回登录页面或者跳到验证页面，那么此Cookies无效，我们需要将该Cookies从数据库中移除。

Cookies移除之后，刚才所说的生成模块就会检测到Cookies的Hash和账号的Hash相比少了此账号的Cookies，生成模块就会认为这个账号还没生成Cookies，那么就会用此账号重新登录，此账号的Cookies又被重新更新。

为了实现通用可扩展性，我们首先定义一个检测器的父类，声明一些通用组件，实现如下所示：

```
class ValidTester(object):
    def __init__(self, website='default'):
        self.website = website
        self.cookies_db = RedisClient('cookies', self.website)
        self.accounts_db = RedisClient('accounts', self.website)

    def test(self, username, cookies):
        raise NotImplementedError

    def run(self):
        cookies_groups = self.cookies_db.all()
        for username, cookies in cookies_groups.items():
            self.test(username, cookies)复制代码
```

在这里定义了一个父类叫作`ValidTester`，在`__init__()`方法里指定好站点的名称`website`，另外建立两个存储模块连接对象`cookies_db`和`accounts_db`，分别负责操作Cookies和账号的Hash，`run()`方法是入口，在这里是遍历了所有的Cookies，然后调用`test()`方法进行测试，在这里`test()`方法是没有实现的，也就是说我们需要写一个子类来重写这个`test()`方法，每个子类负责各自不同网站的检测，如检测微博的就可以定义为`WeiboValidTester`，实现其独有的`test()`方法来检测微博的Cookies是否合法，然后做相应的处理，所以在这里我们还需要再加一个子类来继承这个`ValidTester`，重写其`test()`方法，实现如下：

```
import json
import requests
from requests.exceptions import ConnectionError

class WeiboValidTester(ValidTester):
    def __init__(self, website='weibo'):
        ValidTester.__init__(self, website)

    def test(self, username, cookies):
        print('正在测试Cookies', '用户名', username)
        try:
            cookies = json.loads(cookies)
        except TypeError:
            print('Cookies不合法', username)
            self.cookies_db.delete(username)
            print('删除Cookies', username)
            return
        try:
            test_url = TEST_URL_MAP[self.website]
            response = requests.get(test_url, cookies=cookies, timeout=5, allow_redirects=False)
            if response.status_code == 200:
                print('Cookies有效', username)
                print('部分测试结果', response.text[0:50])
            else:
                print(response.status_code, response.headers)
                print('Cookies失效', username)
                self.cookies_db.delete(username)
                print('删除Cookies', username)
        except ConnectionError as e:
            print('发生异常', e.args)复制代码
```

`test()`方法首先将Cookies转化为字典，检测Cookies的格式，如果格式不正确，直接将其删除，如果格式没问题，那么就拿此Cookies请求被检测的URL。`test()`方法在这里检测微博，检测的URL可以是某个Ajax接口，为了实现可配置化，我们将测试URL也定义成字典，如下所示：

```
TEST_URL_MAP = {
    'weibo': 'https://m.weibo.cn/'
}复制代码
```

如果要扩展其他站点，我们可以统一在字典里添加。对微博来说，我们用Cookies去请求目标站点，同时禁止重定向和设置超时时间，得到Response之后检测其返回状态码。如果直接返回200状态码，则Cookies有效，否则可能遇到了302跳转等情况，一般会跳转到登录页面，则Cookies已失效。如果Cookies失效，我们将其从Cookies的Hash里移除即可。

### 接口模块

Cookies最终还是需要给爬虫来用，同时一个Cookies池可供多个爬虫使用，所以我们还需要定义一个Web接口，爬虫访问此接口便可以取到随机的Cookies。我们采用Flask来实现接口的搭建

```
import json
from flask import Flask, g
app = Flask(__name__)
# 生成模块的配置字典
GENERATOR_MAP = {
    'weibo': 'WeiboCookiesGenerator'
}
@app.route('/')
def index():
    return '<h2>Welcome to Cookie Pool System</h2>'

def get_conn():
    for website in GENERATOR_MAP:
        if not hasattr(g, website):
            setattr(g, website + '_cookies', eval('RedisClient' + '("cookies", "' + website + '")'))
    return g

@app.route('/<website>/random')
def random(website):
    """
    获取随机的Cookie, 访问地址如 /weibo/random
    :return: 随机Cookie
    """
    g = get_conn()
    cookies = getattr(g, website + '_cookies').random()
    return cookies复制代码
```

我们同样需要实现通用的配置来对接不同的站点，所以接口链接的第一个字段定义为站点名称，第二个字段定义为获取的方法，例如，/weibo/random是获取微博的随机Cookies，/zhihu/random是获取知乎的随机Cookies。

### 调度模块

最后加上一个调度模块让这几个模块配合运行起来，主要的工作就是驱动几个模块定时运行，同时各个模块需要在不同进程上运行

```
import time
from multiprocessing import Process
from cookiespool.api import app
from cookiespool.config import *
from cookiespool.generator import *
from cookiespool.tester import *

class Scheduler(object):
    @staticmethod
    def valid_cookie(cycle=CYCLE):
        while True:
            print('Cookies检测进程开始运行')
            try:
                for website, cls in TESTER_MAP.items():
                    tester = eval(cls + '(website="' + website + '")')
                    tester.run()
                    print('Cookies检测完成')
                    del tester
                    time.sleep(cycle)
            except Exception as e:
                print(e.args)

    @staticmethod
    def generate_cookie(cycle=CYCLE):
        while True:
            print('Cookies生成进程开始运行')
            try:
                for website, cls in GENERATOR_MAP.items():
                    generator = eval(cls + '(website="' + website + '")')
                    generator.run()
                    print('Cookies生成完成')
                    generator.close()
                    time.sleep(cycle)
            except Exception as e:
                print(e.args)

    @staticmethod
    def api():
        print('API接口开始运行')
        app.run(host=API_HOST, port=API_PORT)

    def run(self):
        if API_PROCESS:
            api_process = Process(target=Scheduler.api)
            api_process.start()

        if GENERATOR_PROCESS:
            generate_process = Process(target=Scheduler.generate_cookie)
            generate_process.start()

        if VALID_PROCESS:
            valid_process = Process(target=Scheduler.valid_cookie)
            valid_process.start()
```

这里用到了两个重要的配置，即产生模块类和测试模块类的字典配置，如下所示：

```
# 产生模块类，如扩展其他站点，请在此配置
GENERATOR_MAP = {
    'weibo': 'WeiboCookiesGenerator'
}

# 测试模块类，如扩展其他站点，请在此配置
TESTER_MAP = {
    'weibo': 'WeiboValidTester'
}
```

这样的配置是为了方便动态扩展使用的，键名为站点名称，键值为类名。如需要配置其他站点可以在字典中添加，如扩展知乎站点的产生模块，则可以配置成：

```
GENERATOR_MAP = {
    'weibo': 'WeiboCookiesGenerator',
    'zhihu': 'ZhihuCookiesGenerator',
}
```

Scheduler里将字典进行遍历，同时利用`eval()`动态新建各个类的对象，调用其入口`run()`方法运行各个模块。同时，各个模块的多进程使用了multiprocessing中的Process类，调用其`start()`方法即可启动各个进程。

另外，各个模块还设有模块开关，我们可以在配置文件中自由设置开关的开启和关闭，如下所示：

```
# 产生模块开关
GENERATOR_PROCESS = True
# 验证模块开关
VALID_PROCESS = False
# 接口模块开关
API_PROCESS = True
```

定义为True即可开启该模块，定义为False即关闭此模块。




## 扩展

### redis中hash的基本操作

```
import random
import redis

class RedisClient(object):
    def __init__(self, type, website, host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD):
        """
        初始化Redis连接
        :param host: 地址
        :param port: 端口
        :param password: 密码
        """
        self.db = redis.StrictRedis(host=host, port=port, password=password, decode_responses=True)
        self.type = type
        self.website = website

    def name(self):
        """
        获取Hash的名称
        :return: Hash名称
        """
        return "{type}:{website}".format(type=self.type, website=self.website)

    def set(self, username, value):
        """
        设置键值对
        :param username: 用户名
        :param value: 密码或Cookies
        :return:
        """
        return self.db.hset(self.name(), username, value)

    def get(self, username):
        """
        根据键名获取键值
        :param username: 用户名
        :return:
        """
        return self.db.hget(self.name(), username)

    def delete(self, username):
        """
        根据键名删除键值对
        :param username: 用户名
        :return: 删除结果
        """
        return self.db.hdel(self.name(), username)

    def count(self):
        """
        获取数目
        :return: 数目
        """
        return self.db.hlen(self.name())

    def random(self):
        """
        随机得到键值，用于随机Cookies获取
        :return: 随机Cookies
        """
        return random.choice(self.db.hvals(self.name()))

    def usernames(self):
        """
        获取所有账户信息
        :return: 所有用户名
        """
        return self.db.hkeys(self.name())

    def all(self):
        """
        获取所有键值对
        :return: 用户名和密码或Cookies的映射表
        """
        return self.db.hgetall(self.name())复制代码
```

这里我们新建了一个`RedisClien`t类，初始化`__init__()`方法有两个关键参数`type`和`website`，分别代表类型和站点名称，它们就是用来拼接Hash名称的两个字段。如果这是存储账户的Hash，那么此处的`type`为`accounts`、`website`为`weibo`，如果是存储Cookies的Hash，那么此处的`type`为`cookies`、`website`为`weibo`。

接下来还有几个字段代表了Redis的连接信息，初始化时获得这些信息后初始化`StrictRedis`对象，建立Redis连接。

`name()`方法拼接了`type`和`website`，组成Hash的名称。`set()`、`get()`、`delete()`方法分别代表设置、获取、删除Hash的某一个键值对，`count()`获取Hash的长度。

比较重要的方法是`random()`，它主要用于从Hash里随机选取一个Cookies并返回。每调用一次`random()`方法，就会获得随机的Cookies，此方法与接口模块对接即可实现请求接口获取随机Cookies。