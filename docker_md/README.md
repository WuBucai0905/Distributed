# Docker

容器技术的两个基本概念：

容器和镜像

容器就是进程； 镜像就是程序。 镜像运行起来就是容器。

把 代码、依赖和操作系统 打包一起就是镜像。

## 核心组件

docker客户端、docker服务器、docker镜像、registry、docker容器

## 制作 容器镜像

docker 使用 dockerfile文件来描述 镜像的构建过程。

```
内容定义如下：
FROM指令 指定了基础镜像是python:3.6-alpine
WORKDIR指令 做的是工作目录切换
ADD指令 将当前目录下的所有内容（app.py、requirements.txt）复制到镜像的 /app 目录下【ADD . /app】
RUN指令 运行pip命令安装依赖
EXPOSE指令 暴露允许被外界访问的端口
ENV指令 设置环境变量
CMD指令 设置容器内进程
ENTRYPOINT指令 和 CMD 都是 Docker 容器进程启动所必需的参数，完整执行格式是：“ENTRYPOINT CMD”
原因: 默认情况下，Docker 会为你提供一个隐含的 ENTRYPOINT，即：/bin/sh -c
Docker 容器的启动进程为实际为 ENTRYPOINT，而不是 CMD
```

docker build 会自动加载当前目录下的 Dockerfile 文件，然后按照顺序执行Dockerfile文件中的指令。【 -t 的作用是给这个镜像加一个 Tag，即：起一个好听的名字】

## 运行镜像得到容器

```
docker run -p 8082:8082 helloworld  运行镜像得到容器
【指定CMD后helloworld  后面什么都不用写，否则，需要把进程的启动命令加在后面】
```

curl命令通过宿主机的IP和端口号，来访问容器中的Web应用

```
# 查看运行中的容器
docker ps指令
```

## 分享镜像

Docker  Hub

docker login 命令  登录

push到Docker Hub之前，需要先给镜像指定一个版本号

```
docker tag helloworld liuchunming/helloworld:v1
docker push liuchunming/helloworld:v1  镜像push到Docker Hub上
```

## 镜像加速

配置加速器来解决：

点击Docker Desktop应用图标 -> Perferences。在settings页面中进入Docker Engine修改和添加Docker daemon 配置文件即可。  修改完成之后，点击Apply & Restart按钮，Docker就会重启并应用配置的镜像地址了。

## 与宿主机共享文件

容器技术使用了Rootfs机制和Mount Namespace构建出了一个同宿主机完全隔离开的文件系统环境。

**遇到的问题：**

- 容器里进程新建的文件，怎么才能让宿主机获取到？
- 宿主机上的文件和目录，怎么才能让容器里的进程访问到？

Volume机制  允许你将宿主机上指定的目录，挂载到容器里面进行读取和修改。

-v选项，可以宿主机目录~/work挂载进容器的 /test 目录当中

```
docker run -d -p 8082:8082 -v ~/work:/test --name flasky helloworld
# 这样，在容器flasky中 会创建/test目录，在/test目录下创建的文件，在宿主机的目录~/work中可看到。在宿主机的目录~/work中创建的文件，在容器flasky中/test目录下也可以看到。
# Mounts字段中Source的值就是宿主机上的目录，Destination是对应的容器中的目录
```

如果不显示声明宿主机目录，那么 Docker 就会在宿主机上创建一个临时目录/var/lib/docker/volumes/[VOLUMEID]/data，然后把它挂载到容器的 /test 目录上。

```
# 想要查看宿主机临时目录的内容，需要先查看到VOLUME_ID
docker volume ls
ls /var/lib/docker/volumes/24c7e73e88b23bdb198e190d9c3227201827735b1b92872c951f755847ff88ee/_data/
```

将容器的目录映射到宿主机的某个目录，一个重要使用场景是持久化容器中产生的文件，比如应用的日志，方便在容器外部访问。

## 容器加上资源限制

默认情况下，容器并没有被设定使用操作系统资源的上限。

Docker可以利用Linux Cgroups机制可以给容器设置资源使用限制。

Linux Cgroups 的全称是 Linux Control Group。它最主要的作用，就是限制一个进程组能够使用的资源上限，包括 CPU、内存、磁盘、网络带宽等等。Docker正是利用这个特性限制容器使用宿主上的CPU、内存。

**启动容器时给应用加上限制**

```
# 容器使用的CPU限制设定在最高20%，内存使用最多是300MB。
docker run -it --cpu-period=100000 --cpu-quota=20000 -m 300M helloworld
```

–cpu-period和–cpu-quota组合使用来限制容器使用的CPU时间。  表示在–cpu-period的一段时间内，容器只能被分配到总量为 --cpu-quota 的 CPU 时间。

-m选项则限制了容器使用宿主机内存的上限。

## 容器状态：

docker ps  查看当前运行中的容器，如果加上【-a选项，则可以查看运行中和已经停止的所有容器。】

Up状态，也就是处于运行中的状态

Exited(0)状态，也就是退出状态

Created状态，也就是创建中的状态

- CONTAINER ID：容器ID，唯一标识容器
- IMAGE：创建容器时所用的镜像
- COMMAND：在容器最后运行的命令
- CREATED：容器创建的时间
- STATUS：容器的状态
- PORTS：对外开放的端口号
- NAMES：容器名（具有唯一性，Docker负责命名）

## 维持容器运行状态

docker run指令有一个参数--restart，在容器中启动的进程正常退出或发生OOM时， docker会根据--restart的策略判断是否需要重启容器。

如果容器是因为执行docker stop或docker kill退出，则不会自动重启。

**支持restart的策略判断**

- no – 容器退出时不要自动重启。这个是默认值。
- on-failure[:max-retries] – 只在容器以非0状态码退出时重启。可选的，可以退出docker daemon尝试重启容器的次数。
- always – 不管退出状态码是什么始终重启容器。当指定always时，docker daemon将无限次数地重启容器。容器也会在daemon启动时尝试重启容器，不管容器当时的状态如何。
- unless-stopped – 不管退出状态码是什么始终重启容器。不过当daemon启动时，如果容器之前已经为停止状态，不启动它。

每次重启服务器不断地增加重启延迟，来防止影响服务器。直到超过on-failure限制，或执行docker stop或docker rm -f。

容器重启成功（容器启动后并运行至少10秒），然后delay重置为默认的100ms。

**两种重启策略**

```
docker run --restart=always flasky
# restart策略为always，使得容器退出时，Docker将重启它。并且是无限制次数重启。
docker run --restart=on-failure:10 flasky
# restart策略为on-failure，最大重启次数为10的次。容器以非0状态连续退出超过10次，Docker将中断尝试重启这个容器。
```

## Docker toolbox

内核都在虚拟机里面运行

### 安装

先安装git可能出现Windows正在寻找 base.exe

```
"D:\Program Files\Git\bin\bash.exe"(git的bash.exe位置) -login -i "D:\Program Files\Docker Toolbox\start.sh"(toolbox的start.sh位置)
```

更改镜像源

```
# 1、进入VM bash
docker-machine ssh [machine-name]
# 2、
sudo vi /var/lib/boot2docker/profile
# 3、在–label provider=virtualbox的下一行添加(阿里云加速器)
--registry-mirror https://xxxxxxxx.mirror.aliyuncs.com
# 4、重启docker  退出
exit
# 5、
docker-machine restart default
```

### 相关命令

#### 容器创建

```
创建  docker create
启动  docker start
 == docker run 是两个的组合
```

#### 容器长期运行

```
docker run (-d) centos /bin/bash -c "while true;do sleep 1;done"
返回容器的ID
docker run -d 运行web任务的容器通常以 后台进程进行的。 【-d 选项】
```

#### 指定容器名字

```
docker run --name [name] ...
```

#### 容器停止

```
docker stop(kill) ID/NAME
```

#### 进入容器

```
docker attach LongID
docker exec -it ShortID bash |||||| 2、 ps -ef
-it: 以交互的模式打开tty,执行bash
【-it选项指的是连接到容器后，启动一个terminal（终端）并开启input（输入）功能。-it后面接的是容器的名称，/bin/sh表示进入到容器后执行的命令。还可以通过容器的ID进入容器中】
```

**attach和exec的区别如下：**

attach直接进入容器，启动命令的终端，不会启动新的进程；

【不建议使用】docker attach container_id

【缺点】当多个窗口同时attach到同一个容器时，所有的窗口都会同步的显示，假如其中的一个窗口发生阻塞时，其它的窗口也会阻塞。

exec则是在容器中打开新的终端，并且可以启动新的进程

#### 进入已有的停止的容器

```
docker start ShortID

restart = stop + start
```

#### 暂停容器

```
docker pause ShortID
```

#### 恢复暂停的容器

```
docker unpause ShortID
```

#### 删除容器

```
docker rm ShortID
docker rm -f ShortID
```

【不带-f选项，只能删除处于非Up状态的容器，带上-f则可以删除处于任何状态下的容器。】

#### 批量删除容器

```
docker rm -v $(docker ps -aq -f status=exited)
```

#### 容器成为镜像

```
docker commit flasky2 liuchunming033/helloworld:v2  将正在运行的容器，commit成新的镜像
```



#### 删除镜像

```
docker rmi image
```

### 命令解释：

```
docker run -it centos /bin/bash
# docker客户端用docker命令来运行
# run参数表明客户端要运行一个新的容器
# -it 以交互的模式打开容器
# 运行新容器要告诉docker守护进程的最小参数：
# 	容器从哪个镜像创建，【centos】
# 	容器要运行的命令 【/bin/bash】容器中运行bash shell
```

命令

```
docker image ls  查看镜像
docker inspect [ helloworld:latest ] 查看镜像的元信息
docker image rm 删除镜像
```



NAT技术

公有IP地址 内部来规划私有网络

容器中设置端口映射

```
# 详情请看hpptd
# docker run -d -p 80 httpd
docker run -d -p  80:80 httpd
```

