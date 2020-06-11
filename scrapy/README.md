# scrapy

## 流程

### 创建项目

```
scrapy  startproject  项目名称
```

### 创建spider

```
cd 项目名称
scrapy genspider arg1:spider名称  [arg2:网站域名]
```

spider类有三个属性：name、allowed_domains 和 start_urls，还有一个方法 parse。

- name，它是每个项目唯一的名字，用来区分不同的 Spider。
- allowed_domains，它是允许爬取的域名，如果初始或后续的请求链接不是这个域名下的，则请求链接会被过滤掉。
- start_urls，它包含了 Spider 在启动时爬取的 url 列表，初始请求是由它来定义的。
- parse，它是 Spider 的一个方法。默认情况下，被调用时 start_urls 里面的链接构成的请求完成下载执行后，返回的响应就会作为唯一的参数传递给这个函数。该方法负责解析返回的响应、提取数据或者进一步生成要处理的请求。

### 创建item

继承scrapy.Item类，定义类型为scrapy.Field字段

item保存爬取数据的容器，它的使用方法和字典类似。

相比字典，Item 多了额外的保护机制，可以避免拼写错误或者定义字段错误。

### 解析request得到Response

parse() 直接解析网页内容

提取的方式可以是css选择器或者是xpath选择器

### 使用Item

Item 可以理解为一个字典，不过在声明的时候需要实例化，最后需要将 item 返回

### 后续request

构造请求需要用到 scrapy.Request

​	**参数：**

- url：它是请求链接。
- callback：它是回调函数。当指定了该回调函数的请求完成之后，获取到响应，引擎会将该响应作为参数传递给这个回调函数。回调函数进行解析或生成下一个请求，回调函数如上文的 parse() 所示。
- meta： 来传递url内的参数
- dont_filter： 是否去重

### 运行

```
scrapy crawl 项目名称
```

### 保存到文件

Scrapy 提供的 Feed Exports 可以轻松将抓取结果输出

结果保存到 json 文件

```
scrapy crawl 项目名称 -o xxxx.json
```

每一个 Item 输出一行json， 输出后缀为 jl (jsonline)

```
scrapy crawl 项目名称 -o xxxx.jl(xxxx.jsonlines)
```

另外还可以通过自定义 ItemExporter 来实现其他的输出【还支持 ftp、s3 等远程输出】。

### 保存到数据库

**保存到文件【输出到数据库】Item Pipeline**

Item Pipeline 为项目管道。当 Item 生成后，它会自动被送到 Item Pipeline 进行处理

定义一个类并实现 process_item() 方法  ------必须返回包含数据的字典或 Item 对象，或者抛出 DropItem 异常

process_item() 方法有两个**参数**

- 一个参数是 item，每次 Spider 生成的 Item 都会作为参数传递过来
- 另一个参数是 spider，就是 Spider 的实例

**存储到mongodb**

from_crawler  用 @classmethod 标识，是一种依赖注入的方式，这是一个类方法。

**参数**crawler： 通过 crawler 这个我们可以拿到全局配置的每个配置信息

open_spider方法   当 Spider 被开启时，这个方法被调用。在这里主要进行了一些初始化操作。

close_spider方法   当 Spider 被关闭时，这个方法会调用，在这里将数据库连接关闭。

process_item方法   执行了数据插入操作

# scrapy_redis

## 源码分析

```
RFPDupeFilter中的request_seen()生成指纹
Scheduler中的 close()方法中的persist是否持久化; enqueue_request() and逻辑与:返回第一个为假的表达式，否则返回最后的表达式 or逻辑或:返回第一个为真的表达式，否则返回最后的表达式

```

scrapy中的spider中的start_request()中的dont_filter默认为True

##############################################