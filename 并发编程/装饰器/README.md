# 装饰器

> 本质是一个闭包函数,作用在于不改变原函数功能和调用方法的基础上给它添加额外的功能

**语法糖:**  @ 符号

**执行过程:**

- 不会 首先去执行 装饰器装饰的函数
- 将 装饰的函数 作为参数 传递给 装饰器

## 1.使用方法

1. 先定义一个装饰器（帽子） 
2. 再定义你的业务函数或者类（人）
3. 最后把这装饰器（帽子）扣在这个函数（人）头上

## 2.实现功能

### 2.1日志打印器

1. 在函数执行前，先打印一行日志告知要执行函数了。
2. 在函数执行完再打印一行日志告知执行完啦。

```
# 这是装饰器函数，参数 func 是被装饰的函数
def logger(func):
    def wrapper(*args, **kw):
        print('主人，我准备开始执行：{} 函数了:'.format(func.__name__))

        # 真正执行的是这行。
        func(*args, **kw)

        print('主人，我执行完啦。')
    return wrapper
```

### 2.2时间计时器

```
# 这是装饰函数
def timer(func):
    def wrapper(*args, **kw):
        t1=time.time()
        # 这是函数真正执行的地方
        func(*args, **kw)
        t2=time.time()

        # 计算下时长
        cost_time = t2-t1
        print("花费时间：{}秒".format(cost_time))
    return wrapper
```

## 3.带参数的函数装饰器

装饰器本身就是一个函数，它也可以传参数

```
def say_hello(contry):
    def wrapper(func):
        def deco(*args, **kwargs):
            if contry == "china":
                print("你好!")
            elif contry == "america":
                print('hello.')
            else:
                return

            # 真正执行函数的地方
            func(*args, **kwargs)
        return deco
    return wrapper
###############################
# 小明，中国人
@say_hello("china")
def xiaoming():
    pass
# jack，美国人
@say_hello("america")
def jack():
    pass

xiaoming()
print("------------")
jack()
看看输出结果:
你好!
------------
hello.
```

## 带参数的 类装饰器

```
class logger(object):
    # 不再接收被装饰函数，而是接收传入参数
    def __init__(self, level='INFO'):
        self.level = level
    # 接收被装饰函数，实现装饰逻辑
    def __call__(self, func): # 接受函数
        def wrapper(*args, **kwargs):
            print("[{level}]: the function {func}() is running..."\
                .format(level=self.level, func=func.__name__))
            func(*args, **kwargs)
        return wrapper  #返回函数

@logger(level='WARNING')
def say(something):
    print("say {}!".format(something))

say("hello")

[WARNING]: the function say() is running...
say hello!
```

## 使用偏函数与类 实现装饰器

可调用(callable)对象

- 函数
- 类【类只要实现了`__call__`函数】
- 偏函数

​        ###########################

## 能装饰类的装饰器

##############################

## wraps装饰器

```
from functools import wraps
def test(func):
    # @wraps(func)
    def inner():
        '装饰器'
        print(inner.__name__,inner.__doc__)
        return func()
    return inner
@test
def func():
    '原函数'
    print(11111)
    print(func.__name__,func.__doc__)     
func()

# 有@wraps(func)
# func 原函数
# 11111
# func 原函数
# 没有@wraps(func)
# inner 装饰器
# 11111
# inner 装饰器
```

加上wraps装饰器,可以保证原函数在执行时不会发生异常

## 内置装饰器property

property 存在于类中，可以将一个函数定义成一个属性，属性的值就是该函数return的内容 | 还可以定义只读属性

```
class Student(object):
    @property
    def score(self):
        return self._score
        
    @score.setter
    def score(self, value):
        if not isinstance(value, int):
            raise ValueError('score must be an integer!')
        if value < 0 or value > 100:
            raise ValueError('score must between 0 ~ 100!')
        self._score = value

# @property本身又创建了另一个装饰器@score.setter，负责把一个setter方法变成属性赋值
>>> s = Student()
>>> s.score = 60 # OK，实际转化为s.set_score(60)
>>> s.score # OK，实际转化为s.get_score()
60
>>> s.score = 9999
Traceback (most recent call last):
  ...
ValueError: score must between 0 ~ 100!
```