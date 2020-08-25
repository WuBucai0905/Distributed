# scrapy

scrapy基于 twisted，性能是最大的优势

爬虫的作用

- 垂直领域的搜索引擎
- 推荐引擎
- 机器学习的数据样本
- 数据分析、舆情分析



## 正则表达式

贪婪匹配：反向匹配

| 字符            | 含义                                                         |
| --------------- | ------------------------------------------------------------ |
| ^               | 以 为开头                                                    |
| .               | 任意字符                                                     |
| *               | 可重复任意遍， 较多的去匹配                                  |
| $               | 以 为结尾                                                    |
| ?               | 非贪婪匹配。  【正向匹配，遇到第一个匹配的字符串结束】       |
| +               | 字符串 至少出现一次， 较少的去匹配                           |
| {}              | {2} 限定前面字符出现的次数为 2次<br />{2, } 限制前面字符出现的次数为 2次以上<br />{2, 5} 限制前面字符出现的次数为 2次以上，5次以下 |
| \|              | 或                                                           |
| []              | [] 里面的字符只需要满足任意一个就行<br />`[^1]` 字符不等于1<br />[0-9] 字符在0-9范围内 |
| \s              | 空格                                                         |
| \S              | 占位字符                                                     |
| \w              | [A-Za-z0-9_]                                                 |
| \W              | 空格                                                         |
| [\u4E00-\u9FA5] | 匹配 汉字                                                    |
| \d              | 匹配 数字                                                    |



遇到 `\r\n`，正则表达式只会取匹配第一行的。怎样取全部内容？

- `re.match(..., re.DOALL)`



## 字符串编码

ASCII

GB2312

Unicode将所有语言统一到一套编码里面

前面补零

乱码解决，传输和存储空间却增大了

可变长度编码 UTF-8



Unicode编码占用空间，但处理更简单

UTF-8编码省空间，但处理麻烦

![2020-07-21 202604](F:\Desktop\前端知识重新整理\media\2020-07-21 202604.png)



使用encode 时 必须将 字符的编码改为 Unicode

decode 将字符串变为Unicode字符串`.decode("指明当前的格式")`





## 爬虫去重



## 深度优先和广度优先

全站爬取 

深度优先 通过 递归来实现

- 递归 太深 可能会引起 栈的溢出

广度优先 通过 队列来实现





## scrapy

`scrapy shell http://xxxx` 对某个网址来进行调试

`scrapy shell -s USER_AGENT="XXX"`



提取结构化数据的两大工具

xpath

`Selector`选择器获取 data  --- `.extract()`  返回的为数组

`.extract_frist()` 提取不到 返回空None

css选择器

`::text` 不能取到下面 子元素里面的内容

| `::attr(href)`



翻页

获取文章列表页中的 文章url 并交给 解析函数就行具体字段的解析

获取下一页的 url 并交给scrapy进行下载，下载后进行 parse

```
from scrapy.http import Request
yield Request(url= xxx, callback = self.function)
```

取域名

```
from urllib import parse
parse.urljoin(base, url)
```



传递参数

```
Request(meta={"xxx": "xxxx"})
// 获取传递到的参数
// response.meta["xxx"]
response.meta,get("xxx", "")
```



#### `itemloader`

通过`itemloader`来加载 `item`

scrapy提供了 `itemloader`机制，把xpath， css选择器 的维护工作变得简单

```
from scrapy.loader import ItemLoader
item_loader = ItemLoader(item=类实例化, resnponse=response)
item_loader.add_css()
item_loader.xpath()
item_loader.add_value()
...
// 调用该方法对上面规则进行解析，解析后生成`item`对象
article_item= item_loader.load_item()
yield article_item
// 取出来的值时list ， 取出来的值还需要处理需加上处理函数
// 解决： 此时需要在`items.py`里面修改`scrapy.Field()`
from scrapy.loader.processors import MapCompose //可以传递任意多的预处理函数，调用顺序：从左到右依次调用
from scrapy.loader.processors import TakeFrist
// from scrapy.loader.processors import Join 查询资料
def function(arg1): //此时 arg1 == title
	pass
title = scrapy.Field(
	input_processor = MapCompose(function), //预处理
	output_processor = TakeFrist()
)

// 一次性完成 `TakeFrist()`
from scrapy.loader import ItemLoader
class ArticleItem(ItemLoader):
	default_output_processor = TakeFrist()
```







item类实例 可以路由到 pipeline中 集中处理数据的去重和存储



### item

1.  `items.py`内定义好

2. `spider`内 初始化类

3. 填值

   ```
   类["xxx"] = xxx
   ...
   ```

4. 返回值到 `pipelines.py`

   ```
   yield 类
   ```





scrapy内有自动下载图片的机制

需要`PIL`库

```
ITEM_PIPELINES ={
	"scrapy.pipelines.images.ImagesPipeline": 300
}
IMAGES_URLS_FIELD = "item字段名" //需要是 **数组**
IMAGES_STORE = "路径"

IMAGES_MIN_HEIGHT = 100
IMAGES_MIN_WIDTH = 100 // 过滤
```







### pipelines

保存数据



定制保存图片个性化：

> 重写 `pipelines.py`时 一定要注意 `return item`

`items.py`内继承 `ImagesPipeline` 然后改写重载

- `item_completed(self, results, item, info)`
  - `results` 文件保存路径





打开文件可以用到 python的 codecs

可以避免很多 编码的工作

#### json

```
// 自定义
import codecs
def __init__(self):
	self.file = codecs.open("article.json", "w", encoding="utf-8")
def process_item(self, item, spider):
	lines = json.dumps(dict(item), ensure_ascii=False)
	self.file.write(lines)
	return item

def spider_closed(self, spider):
	self.file.close()
```

内置

`jsonExportPipeline`



#### MySQL

twisted 提供了 关系型数据库的异步操作

twisted实现异步操作： 连接池

```
from twisted.enterprise import adbapi //将MySQLDB变成异步化操作

class MysqlTwistedPipeline(object):
	def __init__(self, dbpool):
		self.dbpool = dbpool
	
	@classmethod
	def from_settings(cls, settings):
		host = settings["MYSQL_HOST"]
		...
		
	def process_item(self, item, spider):
		query = self.dbpool.runInteraction(self.do_insert, item)
		query.addErrorback(self.handle_error)
		
	def do_insert(self, cursor, item):
		...
		
	def handle_error(self, ...):
		...
		
	
```





cookie 本地存储方式

存储在某个域名之下，不能跨域访问 (是一种安全机制)

session  服务器存储方式

防止csrf攻击： 每次请求时都会生成一个随机的字符串。

- `xsrf`一般会存储在 页面源代码或者`cookies`中



```
import http.cookiejar as cookielib
```

模拟登录不使用`request.post`方法而使用 `request.session` --- 长连接，效率更高

```
session = requests.session()
// 用法同request.post
// 可以直接存储`session`中的`cookie`到本地
session.cookies = cookiejar.LWPCookieJar(filename='cookies.txt')
session.cookies.save()
```

如果存储了`cookies`，可直接load 进来

```
session.cookies.load(ignore_discard=True)
```



不传递`allow_redirects`参数，session 在做请求的时候，服务器返回302，它会自动取获取302之后的页面

```
session.get(url, headers, allow_redirects=False)
```



**HTTP状态码**

| code    | 说明                      |
| ------- | ------------------------- |
| 200     | 请求被成功处理            |
| 301/302 | 永久性重定向/临时性重定向 |
| 403     | 没有权限访问              |
| 404     | 表示没有对应的资源        |
| 500     | 服务器错误                |
| 503     | 服务器停机或正在维护      |





scrapy完成模拟登录

入口在`start_requests`，所有必须重写 `start_requests`

```
def start_requests(self):
	return [scrapy.FormRequest(
		url,
		formdata,
		...
	)]
```

获取某些加密参数放入 `scrapy.FormRequest`

- 可以使用 `requests`来解决
- scrapy提供的异步机制 `return [scrapy.Request('', callback)]`
  - callback 返回的是 function ， 而不是 function()

`SCRAPY`不需要将 `cookies`值保存起来，在后边所有跟踪的request中，会默认将 cookies 放置进去

`scrapy.Request`不写回调函数 ，默认会调用`self.parse()`



登陆完成后 `scrapy.Request` 里面带的是 `session`和`cookies`

- `yield scrapy.Request()` 保证携带同样的`session`和`cookies`





`genspider`生成默认爬虫代码 

`scrapy genspider --list`

- basic
- crawl
- csvfeed
- xmlfeed





全站数据爬虫`crawlspider`

`scrapy genspider -t crawl ...`



`CrawlSpider(Spider)`

`CrawlSpider`不能重载 `parse`函数

源码核心函数`_parse_response`



Rule参数

- link_extractor
- callback
- cb_kwargs
- follow 深度优先爬取
- process_links 预处理函数
- process_request

LinkExtractor





scrapy里面两个重要的类

Request

Response

- 子类
  - TextResponse
  - HtmlResponse
  - XmlResponse



spider yield Request

downloader return Response



随机切换UA

插件`user-agent`

```
u_a_list = [ ... ]
import random
random_index = random.randint(0, len(u_a_list)-1)
random_ua = u_a_list[random_index]

downloadermiddlewares
// 默认取消掉
class RandomUAMiddleware(object):
	def __init__(self, crawler):
		super(RandomUAMiddleware, self).__init__()
		self.u_a_list = crawler.settings.get("u_a_list", [])
	
	@classmethod
	def from_crawler(cls, crawler):
		return cls(crawler)
		
	def process_request(self, request, spider):
		request.headers.setdefault("UESR-AGENT", random())
```



设置IP代理

```
request.meta['proxy'] = 'http://127.0.0.1:8080'
```

设置IP代理池

插件`scrapy_proxies`





验证码识别

在线打码

云打码



scrapy的降低发现爬虫概率的配置

COOKIES_ENABLED = False

TELNETCONSOLE_ENABLED = True

根据不同的 spider 用不同的配置值：  `custom_settings`





动态网页的爬取

selenium

`页面元素提取` 建议使用

```
from scrapy.selector import Selector
Selector(text=browser.page_source)
```



```
browser.excute_script()
```



selenium集成到scrapy

```
// 中间件
from scrapy.http import HtmlResponse

	// 不会像downloader发送而是直接返回到spider
	return HtmlResponse(
		url,
		body,
		encoding,
		request,
	)
```

注意通过一个`browser`去请求多个页面

```
// 中间件类
def __init__(self,):
	self.browser = webdriver.Chrome()
	super(中间件类, self).__init__()
	
def process_request(...):
	self.browser.get(url)
```



隐患

爬虫关闭后 chrome浏览器并没有及时关闭：

Chrome 放入 `spider`里面，而不是`middleware`里面



状态收集器

scrapy的信号

> scrapy使用信号来通知事情发生，通过捕捉信号(使用extension) 来完成额外的工作或添加额外的功能，扩展scrapy
>
> scrapy 的组件以及 扩展 都是基于信号来设计的
>
> 信号提供一些参数，不过处理函数不用接收所欲的参数。
>
> 信号分发机制 仅仅提供处理函数 接收的参数

```
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
```

当爬虫退出的时候关闭chrome

```
dispatcher.connect(self.spider_closed, signals.spider_closed)

def spider_closed(self, spider):
	self.browser.quit()
```

延迟的信号处理器

信号量







开发扩展

> 扩展框架提供一个机制，使得你能将自定义功能绑定到 scrapy
>
> 扩展只是正常的类，在scrapy启动时 被实例化，初始化









异步实现selenium

自寻查找资料



无界面

```
pip install pyvirtualdisplay
// linux上支持	
from pyvirtualdisplay import Display
display = Display(visible=0, size=(800, 650))
display.start()
```



scrapy 解决动态网站的方案

scrapy splash

不推荐， 支持分布式



selenium grid

支持分布式



splinter

python去操控浏览器的解决方案，与selenium类似







scrapy的暂停与重启

```
// 不同spider不能共用同一个目录
scrapy crawl lagou -s JOBDIR=job_info/001
```

接收暂停的信号是 CTRL +  C 的命令  按一次







scrapy的去重原理

`dupefilters.py`





scrapy的telnet

打开telnet服务端和 telnet客户端





### middleware

#### downloadermiddleware



#### spidermiddleware



#### depthmiddleware

监控爬取层数





数据收集

对状态进行收集

数据收集器永远都是可用的， 并注入到 spider里面







# `scrapyd`

部署 scrapy项目，允许使用 HTTP JSON API 来控制你的 spider。

```
pip install scrapyd
```

```
pip install scrapyd-client
```

会拷贝进入一个文件 `scrapy-deploy`

添加 `scrapy-deploy,bat`

```
@echo off
"虚拟环境的... .exe" ".....\scrapy-deploy" %1 %2 %3 %4 %5 %6 %7 %8 %9
```



scrapyd 可以理解为是一个服务器。

scrapy-client 允许将本地的 spider 打包发送给 scrapyd-server

真正部署爬虫的时候需要 scrapyd服务器 和 scrapy-client





部署前需要保证 `scrapy list`命令行可以使用

```
scrapyd-deploy xxx -p Proj
```

打包 将文件传送给 scrapyd







去除HTML中的tags

```
from w3lib.html import remove_tags
```





```
import os
import sys
// 目录使用 `os` 模块来拼接
sys.path.insert(0, "目录")
```

