# celery

> celery本身不提供消息服务，使用第三方消息服务 来传递任务.可以是`rabbitmq`/`redis`

## 1.组件

### 1.1broker

> 消息中间件. 指任务队列本身
>
> Celery 扮演生产者和消费者的角色，brokers 就是生产者和消费者存放/拿取产品的地方(队列)

redis作为broker时，task信息实际上保存在queue中，消息未被消费时任务信息持久存储在queue中。消息中间件的`ack机制`保证了每条任务信息确实执行

**`ack消息确认机制`**

> 中间件将消息分给了消费者，消息就会被删除。如果正在执行任务的消费者突然出现宕机就会丢失某些消息。
>
> 为了保证消息不丢失， 消费者消费完消息后，返回中间件一个消息应答，告知消息处理完毕，中间件就可以去删除这条消息了。

### 1.2result backend

> 任务执行后结果存储的地方

执行完异步任务后会得到一个 id， 根据这个 id 可以得到该任务的执行状态或者结果

### 1.3workers

> 处理任务,celery中的工作者

worker并发的运行在分布式的系统节点中

启动一个worker时，worker与broker建立 TCP长链接， 有数据传输时会创建相应的channel（可以有多个channel）， worker就回broker的队列里面取相应的 task来进行消费。【典型的生产者消费者模型】

启动worker时， 整个程序的配置都是在它启动的时候配置生效的。

### 1.4tasks

> 最基本的单元. 
>
> 一般由用户/触发器 或者其他操作将任务入队, 然后交由 workers 进行处理.

可以在任何 除可调用对象外的地方创建一个类， 定义了一个任务被调用时会发生什么，以及一个工作单元获取到消息后会做什么

每个任务都有不同的名称，发给celery的任务消息中会引用这个名称，工作单元就是根据这个名称找到正确的执行函数.

任务函数如果是  幂等的，意味着一个任务函数以同样的参数被调用多次也不会导致不可预料的效果

任务函数是幂等的话可以设置 `acks_late`选项让工作单元在任务执行返回之后在确认任务消息

避免任务阻塞可以设置过期时间来避免

### 1.5beat

> 定时任务管理者

解决业务场景中的定时和周期任务。 | 很好用的配合插件 djcelery 来动态的定时任务

### 1.6flower

> 监控组件



## 2.安装

```
pip install celery
pip install redis
```



## 3.使用

### 3.1worker

#### 3.1.1启动指定参数

```
celery worker -A proj -n worker4 -Q queue4,queue5 -E -l info
```

- `celery worker:` 启动一个 celery worker程序

- `-A proj` ： -app instance 表示指定应用 proj 用来启动

  ```
  app = Celery('proj')
  ```

- `-n worker4` ： 指定worker的 name

- `-Q queue4,queue5` ： 指定worker去绑定的队列

- `-E` ： events表示监听worker在执行task时的一些事件触发

- `-l info` ： 输出log信息日志， info级别的

worker停止，向worker发送了shutdown命令后，worker在实际终止前会执行完当前所有正在执行的任务。

使用 kill 信号强行终止 worker时当前正在执行的任务会丢失（除非task设置了acks_late选项）



一般我们通过 celery multi 管理 workers 的启动

生产中需要使用 初始化脚本 或者类似supervisor的进程管理系统来管理 worker进程的启动或停止

#### 3.1.2worker并发池

支持四种并发方式：

1. solo
2. prefork
3. eventlet
4. gevent

启动配置文件中可以通过 worker_pool 来指定，默认为prefork . 

还可以通过配置concurrency来指定并发池的size，size的配置和可用的cpu的个数一般是相同的.  

还可以通过 --autoscale来指定并发池的上下限

### 3.2task

#### 3.2.1常用基础

- 普通基础任务 @task类型的装饰器来指定注册为 celery 的 task
- 根据任务状态执行不同操作 on_success、on_failure
- 绑定任务为实例方法
- 定时、周期任务 配置中配置好周期任务，运行一个周期任务触发器即可
- 链式任务 多个子任务组成的任务用异步回调的方式来进行链式任务的调用 | 前一个任务的返回值默认是下一个任务的输入值之一

#### 3.2.2任务创建

对任务的定义可以做重试机制的设置

```
@app.task(autoretry_for=(), default_retry_delay=15, retry_kwargs={'max_retries':3})
```

**任务状态**

- PENDING | STARTED | SUCCESS | FAILURE | RETRY | REVOKED(任务取消)
- 也可以在任务中自定义任务的状态来表明该任务在执行中

task的创建一定要考虑是否会有永久阻塞

#### 3.2.3任务调用

##### exchange

> 中间转换机

**direct**

指定这个消息被那个队列接收，通过bindkey直接匹配完成

**topic**

消息 路由到 binding key与 routing key相匹配的queue中， 引入通配符匹配到多个queue

**fanout**

只要和该交换机绑定的queue 统统发出

##### routing-key

> 路由键

指定调用

- 配置文件中配置好了任务的路由机制
- 调用的时候去指定exchange 和 routingkey
- 配置好的匹配规则 还可以通过前端程序调用去覆盖更新这个规则, 然后达到指定任务到指定队列的功能

**group**调用一系列任务

**chain** 链式任务

**signatures**(也叫 subtasks) 把task函数和参数打包成一个signature对象，然后再去调用delay或apply_async

```
add.subtasks((2, 2)) === add.s(2, 2)
```

**immutabel signatures** 有些任务在回调的时候把参数传进来，有时候又并不想得到某个函数的值，这时候就设置 immutabel=True | 简写为 add.si(2, 2)

### 3.3beat

如果没有指定CELERYBEAT_SCHEDULE,它是默认以文件的形式去作为scheduler去管理定时任务的，会去生成一个celerybeat-schedule文件

#### 3.3.1任务计划

- 整数秒
- timedelta对象：指定一个时间去执行
- crontab对象：利用cron表达式去指定一个执行计划
- solar对象：用日升日落表示时间间隔

除配置文件直接定义好定时任务外，还可以将定时任务添加到业务代码里面`add_periodic_task()`

```
app.on_after_configure.connect装饰器
通过sender这个对象使用add_periodic_task() 既可以把定时任务添加到 beat的执行计划中去
```

### 3.4日志

自带日志工具 get_task_logger


