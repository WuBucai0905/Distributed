selenium获取Ajax数据

`https://github.com/lightbody/browsermob-proxy/`

BrowserMob Proxy

原理就是开了一个代理服务器，然后抓包，同时对接了 Java、Python API，以方便我们可以直接通过代码来获取到内容。

### 实现

```
pip3 install browsermob-proxy
```

还需要下载 browsermob-proxy 的二进制文件，以便于启动 BrowserMob Proxy

下载的`https://github.com/lightbody/browsermob-proxy/releases`

下载好的文件放到 项目目录即可

```
from browsermobproxy import Server
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# 启动代理
server = Server('./browsermob-proxy-2.1.4/bin/browsermob-proxy')
server.start()
proxy = server.create_proxy()
print('proxy', proxy.proxy)

# 启动浏览器
chrome_options = Options()
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--proxy-server={0}'.format(proxy.proxy))
driver = webdriver.Chrome(options=chrome_options)

# 监听结果
base_url = 'https://dynamic2.scrape.center/'
proxy.new_har(options={
    'captureContent': True,
    'captureHeaders': True
})
driver.get(base_url)
time.sleep(3)

# 读取结果
result = proxy.har
for entry in result['log']['entries']:
    print(entry['request']['url'])
    print(entry['response']['content'])
```

1. 第一步便是启动 BrowserMob Proxy，它会在本地启动一个代理服务，这里注意 Server 的第一个参数需要指定 BrowserMob Proxy 的可执行文件路径，这里我就指定了下载下来的 BrowserMob Proxy 的 bin 目录的 browsermob-proxy 的路径。
2. 第二步便是启动 Selenium 了，它可以设置 Proxy Server 为 BrowserMob Proxy 的地址。
3. 第三步便是访问页面同时监听结果，这里我们需要调用 new_har 方法，同时指定捕获 Resopnse Body 和 Headers 信息，紧接着调用 Selenium 的 get 方法访问一个页面，这时候浏览器便会加载这个页面，同时所有的请求和响应信息都会被记录到 HAR 中。
4. 第四步便是读取 HAR 到内容了，我们调用 log 到 entries 字段，里面便包含了请求和响应的具体结果，这样所有的请求和响应信息我们便能获取到了，Ajax 的内容也不在话下。

har 的内容其实是一个 JSON 对象，里面记录了在访问页面的过程中发生的所有请求和响应内容，一般内容都会记录在 logs 的 entries 字段里面



`https://mp.weixin.qq.com/s/DJaipGFNo9k8xK2-MV1A7A`

