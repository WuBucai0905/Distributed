# selenium

### 浏览器不同标签页间的切换

1. 获取所有标签页的窗口句柄
2. 利用窗口句柄字切换到句柄指向的标签页

```
# 1. 获取当前所有的标签页的句柄构成的列表
current_windows = driver.window_handles

# 2. 根据标签页句柄列表索引下标进行切换
driver.switch_to.window(current_windows[0])
```

### 执行js代码

```
driver.execute_script(js) # 执行js的方法
```

### 页面等待

1. 强制等待

   ```
   time.sleep()
   ```

   缺点是不智能，设置的时间太短，元素还没有加载出来；设置的时间太长，则会浪费时间

2. 隐式等待

   针对的是元素定位， 设置一段时间，在一段时间内判断元素是否定位成功，成功执行下一步

   ```
   driver.implicitly_wait(10) # 隐式等待，最长等20秒
   ```

3. 显式等待

   每经过 多少秒就查看一次 等待条件是否达成，达成就就停止等待继续执行后续代码，没达成报超时异常

   ```
   # 显式等待
   WebDriverWait(driver, 20, 0.5).until(
       EC.presence_of_element_located((By.LINK_TEXT, '好123')))  
   # 参数20表示最长等待20秒
   # 参数0.5表示0.5秒检查一次规定的标签是否存在
   # EC.presence_of_element_located((By.LINK_TEXT, '好123')) 表示通过链接文本内容定位标签
   # 每0.5秒一次检查，通过链接文本内容定位标签是否存在，如果存在就向下继续执行；如果不存在，直到20秒上限就抛出异常
   ```

### 无界面模式

- 实例化配置对象 `options = webdriver.ChromeOptions()`
- 配置对象添加开启无界面模式的命令 `options.add_argument("--headless")`
- 配置对象添加禁用gpu的命令 `options.add_argument("--disable-gpu")`
- 实例化带有配置对象的driver对象 `driver = webdriver.Chrome(chrome_options=options)`

### 代理IP

- 实例化配置对象  `options = webdriver.ChromeOptions()`
- 配置对象添加使用代理ip的命令 `options.add_argument('--proxy-server=http://x.x.x.x:端口')`
- 实例化带有配置对象的driver对象 `driver = webdriver.Chrome('./chromedriver', chrome_options=options)`

### 替换UserAgent

- 实例化配置对象 `options = webdriver.ChromeOptions()`
- 配置对象添加替换UA的命令 `options.add_argument('--user-agent=Mozilla/5.0 HAHA')`
- 实例化带有配置对象的driver对象 `driver = webdriver.Chrome('./chromedriver', chrome_options=options)`

### 对cookie的处理

1. 获取cookie

   `driver.get_cookies()`返回列表，其中包含的是完整的cookie信息

   如果想要把获取的 cookie 信息和 requests 模块配合使用的话，需要转换为 name、value 作为键值对的 cookie 字典

   ```
   # 获取当前标签页的全部cookie信息
   print(driver.get_cookies())
   # 把cookie转化为字典
   cookies_dict = {cookie[‘name’]: cookie[‘value’] for cookie in driver.get_cookies()}
   ```

2. 删除cookie

   ```
   #删除一条cookie
   driver.delete_cookie("CookieName")
   
   # 删除所有的cookie
   driver.delete_all_cookies()
   ```

