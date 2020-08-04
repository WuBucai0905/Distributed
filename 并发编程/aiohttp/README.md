# aiohttp + asyncio

# 1.aiohttp

异步web库

python3.5版本开始加入了`async`/`await`关键字

async定义一个协程，await用于挂起阻塞的异步调用接口

## 1.1发送session请求

>创建一个session，然后使用这个session执行所有的请求
>
>每个session对象内部包含了一个连接池，并且将会保持连接和连接复用（默认开启）可以加快整体的性能。

```
async with aiohttp.ClientSession() as session:　　#协程嵌套，只需要处理最外层协程即可fetch_async
  async with session.get(url) as resp:
  	await resp.text() # await关键字，实现异步。所有他上面的函数体需要声明为异步async
  	# 特殊响应内容json
  	# await resp.json()
```

session还支持其他方法：

```
session.put('http://httpbin.org/put', data=b'data')
session.patch('http://httpbin.org/patch', data=b'data')
...
```

### 1.1.1ClientSession 对象

```
使用代理（包含代理需要认证的情况）：
conn = aiohttp.ProxyConnector(proxy="http://some.proxy.com",	proxy_auth=aiohttp.BasicAuth('user', 'pass') # 代理认证)
session = aiohttp.ClientSession(connector=conn)

自定义cookie(自定义headers的话 数据要是dict格式)：
aiohttp.ClientSession({'cookies_are': 'working'})

超时设置
timeout = aiohttp.ClientTimeout(total=1)
aiohttp.ClientSession(timeout=timeout)

并发设置（直接放置在对应的爬取方法里面，使用 async with 语句将 semaphore 作为上下文对象即可）
semaphore = asyncio.Semaphore(CONCURRENCY)
async with semaphore:
	async with aiohttp.ClientSession().get(URL)
```



## 1.2POST传递数据

### 1.2.1模拟表单

- 转码情况：data=dict的方式，和form提交数据是一样的作用
- 不转码情况： data=str的方式，直接以字符串的形式不会被转码

```
payload = {'key1': 'value1', 'key2': 'value2'}
session.post('http://httpbin.org/post',data=payload)
```

### 1.2.2JSON

>json.dumps(payload)返回的也是一个字符串，只不过这个字符串可以被识别为json格式

```
payload = {'some': 'data'}
session.post(url, data=json.dumps(payload))
```

### 1.2.3小文件

> 如果将文件对象设置为数据参数，aiohttp将自动以字节流的形式发送给服务器

```
# 方法1
url = 'http://httpbin.org/post'
files = {'file': open('report.xls', 'rb')}
session.post(url, data=files)
# 方法2
url = 'http://httpbin.org/post'
data = FormData()
data.add_field('file',
    open('report.xls', 'rb'),
    filename='report.xls',
    content_type='application/vnd.ms-excel')
session.post(url, data=data)
```

### 1.2.4大文件

aiohttp支持多种类型的文件以流媒体的形式上传，所以我们可以在文件未读入内存的情况下发送大文件

```
@aiohttp.streamer
def file_sender(writer, file_name=None):
 with open(file_name, 'rb') as f:
  chunk = f.read(2**16)
  while chunk:
   yield from writer.write(chunk)
   chunk = f.read(2**16)
# Then you can use `file_sender` as a data provider
session.post('http://httpbin.org/post',data=file_sender(file_name='huge_file'))
```

### 1.2.5POST预压缩数据

通过aiohttp发送前就已经压缩的数据, 调用压缩函数的函数名（通常是deflate 或 zlib）作为content-encoding的值

```
async def my_coroutine(session, headers, my_data):
	data = zlib.compress(my_data)
	headers = {'Content-Encoding': 'deflate'}
	async with session.post('http://httpbin.org/post',
       data=data,
       headers=headers)
```



## 1.3连接池

> TCPConnector维持链接池，限制并行连接的总量，当池满了，有请求退出再加入新请求

```
conn = aiohttp.TCPConnector(limit=2)　　#默认100，0表示无限
aiohttp.ClientSession(connector=conn)
```

> limit_per_host： 同一端点的最大连接数量。同一端点即(host, port, is_ssl)完全相同

```
conn = aiohttp.TCPConnector(limit_per_host=30) #默认是0
```



## 1.4cookie的安全性

通过设置aiohttp.CookieJar 的 unsafe=True 来配置

```python
jar = aiohttp.CookieJar(unsafe=True)
session = aiohttp.ClientSession(cookie_jar=jar)
```



## 1.5获取响应内容

> 获取响应内容是一个阻塞耗时的过程， await实现协程切换

### 1.5.1使用text()方法

```
查看编码 r.charset
```

### 1.5.2使用read()方法

不进行编码，为字节形式

### 1.5.3StreamResponse

> 不像text,read一次获取所有数据, 把整个响应体读入内存
>
> 获取大量的数据，请考虑使用”字节流“（StreamResponse）

```
async def func1(url,params):
	async with aiohttp.ClientSession() as session:
		# session.get()是Response对象，他继承于StreamResponse
		async with session.get(url,params=params) as r:
   print(await r.content.read(10)) #读取前10字节
```

### 1.5.4获取网站状态码

```
async with session.get(url) as resp:
	print(resp.status)
```

### 1.5.5查看响应头

```
resp.headers 来查看响应头，得到的值类型是一个dict：
resp.raw_headers　　查看原生的响应头，字节类型
```

#### 重定向的响应头

```
resp.history　　#查看被重定向之前的响应头
```

### 1.5.6获取网站cookie

```
# response header
session.cookie_jar.filter_cookies("https://segmentfault.com")
```

- `resp.cookie` 只会获取到当前url下设置的cookie;
- `cookie_jar.filter_cookies` 会维护整站的cookie



## 1.6自定义域名解析地址

可以指定域名服务器的 IP 对我们提供的get或post的url进行解析

```
from aiohttp.resolver import AsyncResolver
resolver = AsyncResolver(nameservers=["8.8.8.8", "8.8.4.4"])
conn = aiohttp.TCPConnector(resolver=resolver)
```



# 2.asyncio

定义异步函数： `async def`

## 2.1实现过程

### 2.1.1定义一个协程

**async关键字**  定义一个协程（coroutine）, 协程不能直接运行，返回的是一个协程对象，需要将协对象程加入到事件循环loop中

1. 创建事件循环 `asyncio.get_event_loop`
2. 注册事件循环 `run_until_complete(future)`
   - 其实`run_until_complete` 内部会做检查，会自动将 协程对象 封装为 future
3. 启动事件循环

**协程对象de处理**

ensure_future() 函数把 协程对象 包装成了 future

**协程对象运行两种方式**

- 在一个运行的协程中用 await 等待它
- 通过 ensure_future 函数计划他的运行。协程对象包装成了 future



### 2.1.2创建一个task

`run_until_complete`将协程 封装为一个任务（task）对象

- task对象是Future类的子类，保存了协程运行后的状态，用于未来获取协程的结果


```
task = loop.create_task(coroutine)
task = asyncio.ensure_future(coroutine)
```



### 2.1.3绑定回调

**应用场景**

协程是一个 IO 的读写操作，等它读完数据后，我们希望得到通知，以便下一步数据的处理。

在task执行完成的时候可以获取执行的结果，回调的最后一个参数是future对象，通过该对象可以获取协程返回值

**添加回调**

`add_done_callback`。 当task（也可以说是coroutine）执行完成的时候,就会调用回调函数。并通过参数future获取协程执行的结果。



### 2.1.4阻塞和await

await可以针对耗时的操作进行挂起，就像生成器里的yield一样，函数让出控制权。

协程遇到await，事件循环将会挂起该协程，执行别的协程，直到其他的协程也挂起或者执行完毕，再进行下一个协程的执行



### 2.1.5并发(多个协程)

#### asyncio.gather(*tasks)

> 将多个协程交给loop，需要借助 **asyncio.gather 函数**
>
> 也可以 先将协程存在列表里

```
loop.run_until_complete(asyncio.gather(do_some_work(1), do_some_work(3)))
```

#### asyncio.wait(tasks) 

> 接受一个task列表



### 2.1.6协程嵌套

一个协程中await了另外一个协程

** ** 待开发 ** **



### 2.1.7协程停止

future对象有几个状态：

Pending Running Done Cacelled

创建future的时候，task为pending，事件循环调用执行的时候当然就是running，调用完毕自然就是done。

如果需要停止事件循环，就需要先把task取消。可以使用asyncio.Task获取事件循环的task



### 2.1.8不同线程的事件循环

#### 主线程

- `loop=get_event_loop()`

#### 其他线程

1. `loop=new_event_loop()`, 创建一个event loop对象
2. `set_event_loop(loop)`, 将event loop对象指定为当前协程的event loop

一个协程内只允许 运行一个 event loop



## 2.2run_until_complete和run_forever

###  run_until_complete

`run_until_complete` 来运行 loop ，等到 future 完成，`run_until_complete` 也就返回了

```
async def do_some_work(x):
    print('Waiting ' + str(x))
    await asyncio.sleep(x)
    print('Done')
loop = asyncio.get_event_loop()
coro = do_some_work(3)
loop.run_until_complete(coro)

输出：
Waiting 3
<等待三秒钟>
Done
<程序退出>
```

### run_forever

`run_forever` 会一直运行，直到 `stop`被调用 。

但是如果 `run_forever` 不返回，`stop` 永远也不会被调用。所以，只能在协程中调 `stop` 。

```
# loop里面单个协程的程序退出
async def do_some_work(loop, x):
    print('Waiting ' + str(x))
    await asyncio.sleep(x)
    print('Done')
    loop.stop()
```

loop里面多个协程的程序退出，需要用到 gather 将多个协程合并为一个future， 并添加 回调， 然后在回调里面去停止loop。

```
# loop里面多个协程的程序退出
async def do_some_work(loop, x):
    print('Waiting ' + str(x))
    await asyncio.sleep(x)
    print('Done')

def done_callback(loop, futu):
    loop.stop()

loop = asyncio.get_event_loop()

futus = asyncio.gather(do_some_work(loop, 1), do_some_work(loop, 3))
futus.add_done_callback(functools.partial(done_callback, loop))

loop.run_forever()
```

### loop.close

loop只要不关闭就还可以再运行。

如果关闭了就不能再运行了。



## 多链接的异步访问

将 异步函数包装在asyncio的Future对象中【asyncio.ensure_future】，然后将Future对象列表【task.append()】作为任务传递给事件循环

## 收集HTTP响应

```
asyncio.gather(*tasks)
```

## 异常解决

并发达到1000个，程序会报错：ValueError: too many file descriptors in select()

### 处理方法

限制并发数量