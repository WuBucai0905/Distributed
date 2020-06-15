# celery

## 组件

**broker**:	中间人用来 接收和分发任务消息，用来存储任务执行的结果（可以用消息队列服务器）

**exchange routing-key queue**:	依次为 中间转换机， 路由键， 队列。 完成消息的整个从发送到具体队列的路由机制

**worker**:	负责任务的处理

**task**:	最基本单元，任务被调用时来发送信息； 工作进程在收到消息时操作任务执行

**result backend**:	任务执行后结果存储的地方

**celery beat**:	定时任务调度器

监控组件flower

### broker消息中间件

本身不提供消息服务，rabbitmq来做中间人

作为接收者来接收需要执行的任务信息；	作为安排者来安排worker去取走接收到的任务

redis作为broker时，task信息实际上保存在queue中，消息未被消费时任务信息持久存储在queue中。消息中间件的ack机制保证了每条任务信息确实执行

**ack消息确认机制**

中间件将消息分给了消费者，消息就会被删除。如果正在执行任务的消费者突然出现宕机就会丢失某些消息。 | 为了保证消息不丢失， 消费者消费完消息后，返回中间件一个消息应答，告知消息处理完毕，中间件就可以去删除这条消息了。

### exchange routing-key queue

**direct**

指定这个消息被那个队列接收，通过bindkey直接匹配完成

**topic**

消息 路由到 binding key与 routing key相匹配的queue中， 引入通配符匹配到多个queue

**fanout**

只要和该交换机绑定的queue 统统发出

### worker任务执行单元

worker并发的运行在分布式的系统节点中

启动一个worker时，worker与broker建立 TCP长链接， 有数据传输时会创建相应的channel（可以有多个channel）， worker就回去broker的队列里面取相应的 task来进行消费。【典型的生产者消费者模型】

启动worker时， 整个程序的配置都是在它启动的时候配置生效的。

### task基本任务单元

可以在任何除 可调用对象外的地方创建一个类， 定义了一个任务被调用时会发生什么，以及一个工作单元获取到消息后会做什么 | 每个任务都有不同的名称，发给celery的任务消息中会引用这个名称，工作单元就是根据这个名称找到正确的执行函数

任务函数如果是  幂等的，意味着一个任务函数以同样的参数被调用多次也不会导致不可预料的效果

任务函数是幂等的话可以设置 acks_late选项让工作单元在任务执行返回之后在确认任务消息

避免任务阻塞可以设置过期时间来避免

### result backend任务执行结果存储

执行完异步任务后会得到一个 id， 根据这个 id 可以得到该任务的执行状态或者结果

### beat定时任务管理者

解决业务场景中的定时和周期任务。 | 很好用的配合插件 djcelery 来动态的定时任务



## worker

### 启动指定参数

```
celery worker -A proj -n worker4 -Q queue4,queue5 -E -l info
```

celery worker: 启动一个 celery worker程序

-A proj ： -app instance 表示指定应用 proj 用来启动

```
app = Celery('proj')
```

-n worker4 ： 指定worker的 name

-Q queue4,queue5 ： 指定worker去绑定的队列

-l info ： 输出log信息日志， info级别的

-E ： events表示监听worker在执行task时的一些事件触发



worker停止，向worker发送了shutdown命令后，worker在实际终止前会执行完当前所有正在执行的任务。 | 使用 kill 信号强行终止 worker时当前正在执行的任务会丢失（除非task设置了acks_late选项）

一般我们通过 celery multi 管理 workers 的启动

生产中需要使用 初始化脚本 或者类似supervisor的进程管理系统来管理 worker进程的启动或停止



### worker并发池

支持四种并发方式：

1. solo
2. prefork
3. eventlet
4. gevent

启动配置文件中可以通过 worker_pool 来指定，默认为prefork ， 还可以通过配置concurrency来指定并发池的size，size的配置和可用的cpu的个数一般是相同的， 还可以通过 --autoscale来指定并发池的上下限

## task

### 常用基础

- 普通基础任务@task类型的装饰器来指定注册为 celery 的 task

- 根据任务状态执行不同操作 on_success、on_failure

- 绑定任务为实例方法
- 定时、周期任务 配置中配置好周期任务，运行一个周期任务触发器即可； 还可以使用djcelery配合使用
- 链式任务 多个子任务组成的任务用异步回调的方式来进行链式任务的调用 | 前一个任务的返回值默认是下一个任务的输入值之一

### 任务创建

对任务的定义可以做重试机制的设置

```
@app.task(autoretry_for=(), default_retry_delay=15, retry_kwargs={'max_retries':3})
```

任务状态

- PENDING | STARTED | SUCCESS | FAILURE | RETRY | REVOKED(任务取消)

- 也可以在任务中自定义任务的状态来表明该任务在执行中

task的创建一定要考虑是否会有永久阻塞

### 任务调用

指定调用

- 配置文件中配置好了任务的路由机制，
- 调用的时候去指定exchange和routingkey
- 配置好的匹配规则还可以通过前端程序调用去覆盖更新这个规则然后达到指定任务到指定队列的功能

任务一个接着一个调用link回调任务，将父任务完成的结果继续调用

eta( now + timedelta(seconds=10) ) countdown expires

group调用一系列任务

chain 链式任务

signatures(也叫 subtasks) 把task函数和参数打包成一个signature对象，然后再去调用delay或apply_async

```
add.subtasks((2, 2)) === add.s(2, 2)
```

immutabel signatures 有些任务在回调的时候把参数传进来，有时候又并不想得到某个函数的值，这时候就设置 immutabel=True | 简写为 add.si(2, 2)

## beat

如果没有指定CELERYBEAT_SCHEDULE,它是默认以文件的形式去作为scheduler去管理定时任务的，会去生成一个celerybeat-schedule文件

### 任务计划

- 整数秒
- timedelta对象：指定一个时间去执行
- crontab对象：利用cron表达式去指定一个执行计划
- solar对象：用日升日落表示时间间隔

除配置文件直接定义好定时任务外，还可以将定时任务添加到 业务代码里面去 add_periodic_task()

```
app.on_after_configure.connect装饰器
通过sender这个对象使用add_periodic_task() 既可以把定时任务添加到 beat的执行计划中去
```

### djcelery插件

INSTALED_APPS添加 djcelery， 然后 migrate生成对应的数据表， 再在配置文件中添加好database的配置， 再加上一段配置 CELERY_SCHEDULER='djcelery.schedulers.DatabaseScheduler' 即可完成利用数据库表内数据的操作达到对定时任务的动态管理

实际上worker也可以结合django去使用，还有包括 beat的启动，启动方式变为：

```
python mange.py celery worker beat
```

甚至我们可以用django-admin后台管理平台去操作添加定时任务的配置

【建议使用单纯的celery，不建议结合django一起使用】

## 日志

自带日志工具 get_task_logger

