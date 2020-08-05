# 日志记录

logging模块

 logging 模块相比 print 有这么几个优点：

- 可以在 logging 模块中设置日志等级，在不同的版本（如开发环境、生产环境）上通过设置不同的输出等级来记录对应的日志，非常灵活。
- print 的输出信息都会输出到标准输出流中，而 logging 模块就更加灵活，可以设置输出到任意位置，如写入文件、写入远程服务器等。
- logging 模块具有灵活的配置和格式化功能，如配置输出当前模块信息、运行时间等，相比 print 的字符串格式化更加方便易用。

## 流程框架

日志记录框架分这么几部分：

- Logger：即 Logger Main Class，是我们进行日志记录时创建的对象，我们可以调用它的方法传入日志模板和信息，来生成一条条日志记录，称作 Log Record。
- Log Record：生成的一条条日志记录。
- Handler：即用来处理日志记录的类，将 Log Record 输出到我们指定的日志位置和存储形式等，如我们可以指定将日志通过 FTP 协议记录到远程的服务器上
- Formatter：实际上生成的 Log Record 也是一个个对象。格式化保存成一条条我们想要的日志文本
- Filter：保存日志前还需要进行过滤，保存某个级别的日志，或只保存包含某个关键字的日志等
- Parent Handler：Handler 之间可以存在分层关系，以使得不同 Handler 之间共享相同功能的代码。



## 相关用法

```
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info('This is a log info')
logger.debug('Debugging')
logger.warning('Warning exists')
logger.info('Finish')
```

### 1.模块基本配置

basicConfig 的参数

- filename：即日志输出的文件名，指定该信息会启用 FileHandler，而不是 StreamHandler，这样日志信息便会输出到文件中了。
- filemode：这个是指定日志文件的写入方式，有两种形式
  - 一种是 w，代表清除后写入
  - 一种是 a，代表追加写入
- stream：在没有指定 filename 的时候会默认使用 StreamHandler，这时 stream 可以指定初始化的文件流。
- format：指定日志信息的输出格式
  - %(levelno)s：打印日志级别的数值。
  - %(levelname)s：打印日志级别的名称。
  - %(pathname)s：打印当前执行程序的路径，其实就是sys.argv[0]。
  - %(filename)s：打印当前执行程序名。
  - %(funcName)s：打印日志的当前函数。
  - %(lineno)d：打印日志的当前行号。
  - %(asctime)s：打印日志的时间。
  - %(thread)d：打印线程ID。
  - %(threadName)s：打印线程名称。
  - %(process)d：打印进程ID。
  - %(processName)s：打印线程名称。
  - %(module)s：打印模块名称。
  - %(message)s：打印日志信息。
- datefmt：指定时间的输出格式。
- style：如果 format 参数指定了，这个参数就可以指定格式化时的占位符风格，如 %、{、$ 等。
- level：指定日志输出的类别，程序会输出大于等于此级别的信息。
- handlers：可以指定日志处理时所使用的 Handlers，必须是可迭代的

#### level

```
logger = logging.getLogger(__name__)
logging.setLevel(level=logging.WARN)
```

| 等级     | 数值 |
| -------- | ---- |
| CRITICAL | 50   |
| FATAL    | 50   |
| ERROR    | 40   |
| WARNING  | 30   |
| WARN     | 30   |
| INFO     | 20   |
| DEBUG    | 10   |
| NOSET    | 0    |

#### handler

可以使用 basicConfig 全局配置， 也可以使用 声明对象的方式

```
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
handler = logging.FileHandler('output.log')
logger.addHandler(handler)
```

#### formatter

```
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.WARN)
formatter = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y/%m/%d %H:%M:%S')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)
```

#### 捕获traceback

```
try:
    result = 10 / 0
except Exception:
    logger.error('Faild to get result', exc_info=True)
logger.info('Finished')
```

 error() 方法中添加了一个参数，将 exc_info 设置为了 True，这样我们就可以输出执行过程中的信息了，即完整的 Traceback 信息。

#### 配置共享

在写项目的时候，我们肯定会将许多配置放置在许多模块下面，这时如果我们每个文件都来配置 logging 配置那就太繁琐了，logging 模块提供了父子模块共享配置的机制，会根据 Logger 的名称来自动加载父模块的配置。

1. 首先定义一个 main.py 文件

   ```
   logger = logging.getLogger('main')
   ```

2. 接下来我们定义 core.py

   ```
   logger = logging.getLogger('main.core')
   ```

    Logger 的名称为 main.core，注意这里开头是 main，即刚才我们在 main.py 里面的 Logger 的名称，这样 core.py 里面的 Logger 就会复用 main.py 里面的 Logger 配置，而不用再去配置一次了

#### 文件配置

配置在代码里面写死并不是一个好的习惯，更好的做法是将配置写在配置文件里面

将配置写入到配置文件，然后运行时读取配置文件里面的配置，这样是更方便管理和维护的

1. 首先定义一个`yaml`配置文件

   ```
   version: 1
   formatters:
     brief:
       format: "%(asctime)s - %(message)s"
     simple:
       format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
   handlers:
     console:
       class : logging.StreamHandler
       formatter: brief
       level   : INFO
       stream  : ext://sys.stdout
     file:
       class : logging.FileHandler
       formatter: simple
       level: DEBUG
       filename: debug.log
     error:
       class: logging.handlers.RotatingFileHandler
       level: ERROR
       formatter: simple
       filename: error.log
       maxBytes: 10485760
       backupCount: 20
       encoding: utf8
   loggers:
     main.core:
       level: DEBUG
       handlers: [console, file, error]
   root:
     level: DEBUG
     handlers: [console]
   ```

   定义了 formatters、handlers、loggers、root 等模块，实际上对应的就是各个 Formatter、Handler、Logger 的配置，参数和它们的构造方法都是相同的

2. 接下来我们定义一个主入口文件main.py

   ```
   import logging
   import core
   import yaml
   import logging.config
   import os
   
   def setup_logging(default_path='config.yaml', default_level=logging.INFO):
       path = default_path
       if os.path.exists(path):
           with open(path, 'r', encoding='utf-8') as f:
               config = yaml.load(f)
               logging.config.dictConfig(config)
       else:
           logging.basicConfig(level=default_level)
   
   def log():
       logging.debug('Start')
       logging.info('Exec')
       logging.info('Finished')
   
   if __name__ == '__main__':
       yaml_path = 'config.yaml'
       setup_logging(yaml_path)
       log()
       core.run()
   ```

    setup_logging() 方法，里面读取了 yaml 文件的配置，然后通过 dictConfig() 方法将配置项传给了 logging 模块进行全局初始化

### 2.声明对象

声明Logger对象，日志输出的主类。

- 初始化的时候我们传入了模块的名称，这里直接使用 `__name__` 来代替
- 调用对象的 info() 方法就可以输出 INFO 级别的日志信息，调用 debug() 方法就可以输出 DEBUG 级别的日志信息...

## 常见误区

### 字符串拼接

```
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# bad
logging.debug('Hello {0}, {1}!'.format('World', 'Congratulations'))
# good
logging.debug('Hello %s, %s!', 'World', 'Congratulations')
```

logging 模块提供了字符串格式化的方法，我们只需要在第一个参数写上要打印输出的模板，占位符用 %s、%d 等表示即可，然后在后续参数添加对应的值就可以了

### 异常处理

通常我们会直接将异常进行字符串格式化，但其实可以直接指定一个参数将 traceback 打印出来

```
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

try:
    result = 5 / 0
except Exception as e:
    # bad
    logging.error('Error: %s', e)
    # good
    logging.error('Error', exc_info=True)
    # good
    logging.exception('Error')
```

