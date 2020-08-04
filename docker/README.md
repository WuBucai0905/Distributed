# Docker

**两个基本概念**：

容器和镜像

容器就是进程； 镜像就是程序。 镜像运行起来就是容器。

把 代码、依赖和操作系统 打包一起就是镜像。

## 1.制作镜像

### 1.1Dockerfile

> dockerfile文件来描述 镜像的构建过程。
>
> 每一层构建之后记得清理掉无关的文件，这样镜像不会显得臃肿

**例子**

```
mkdir mynginx
cd mynginx/
touch Dockerfile
vi Dockerfile
编辑
docker build -t nginx:v3 .
```

**相关指令**

- FROM指令 指定基础镜像，如:python:3.6-alpine
- WORKDIR指令 工作目录切换
- ADD指令 将当前目录下的所有内容复制到镜像的 /app 目录下 【ADD . /app】
- RUN指令 运行pip命令安装依赖。 很多命令时 用 "\ &&"符号连接
- EXPOSE指令 暴露允许被外界访问的端口
- ENV指令 设置环境变量
- CMD指令 设置容器内进程
- ENTRYPOINT指令 和CMD指令都是 Docker 容器进程启动所必需的参数，完整执行格式是：`ENTRYPOINT CMD`
  - 原因: 默认情况下，Docker 会为你提供一个隐含的 ENTRYPOINT，即：`/bin/sh -c`
  - Docker容器的启动进程为实际为 ENTRYPOINT，而不是 CMD

### 1.2加载dockerfile文件

```
docker build -t nginx:v3
```

docker build 会自动加载当前目录下的 Dockerfile 文件，然后按照顺序执行Dockerfile文件中的指令。

- -t 的作用是给这个镜像加一个 Tag，即：起一个好听的名字



## 2.镜像加速

配置加速器来解决：

点击Docker Desktop应用图标 -> Perferences。在settings页面中进入Docker Engine修改和添加Docker daemon 配置文件即可。  修改完成之后，点击Apply & Restart按钮，Docker就会重启并应用配置的镜像地址了。



## 3.与宿主机共享文件

容器技术使用了Rootfs机制和Mount Namespace构建出了一个同宿主机完全隔离开的文件系统环境。

**遇到的问题：**

- 容器里进程新建的文件，怎么才能让宿主机获取到？
- 宿主机上的文件和目录，怎么才能让容器里的进程访问到？

**解决：**

Volume机制  允许你将宿主机上指定的目录，挂载到容器里面进行读取和修改。

```
docker run -d -p 8082:8082 -v ~/work:/test --name flasky helloworld
# Mounts字段中Source的值就是宿主机上的目录，Destination是对应的容器中的目录
```

- 容器flasky中 会创建/test目录。
  - /test目录下创建的文件，在宿主机的目录~/work中可看到；
  - 宿主机的目录~/work中创建的文件，在容器flasky中/test目录下也可以看到。

如果不显示声明宿主机目录，那么 Docker 就会在宿主机上创建一个临时目录 `/var/lib/docker/volumes/[VOLUMEID]/data`，然后把它挂载到容器的 /test 目录上。

**应用场景:**

持久化容器中产生的文件，比如应用的日志，方便在容器外部访问。



## 4.容器加上资源限制

默认情况下，容器并没有被设定使用操作系统资源的上限。

Docker可以利用Linux Cgroups机制可以给容器设置资源使用限制。

Linux Control Group最主要的作用，就是限制一个进程组能够使用的资源上限，包括 CPU、内存、磁盘、网络带宽等等。Docker正是利用这个特性限制容器使用宿主上的CPU、内存。

**启动容器时给应用加上限制**

```
# 容器使用的CPU限制设定在最高20%，内存使用最多是300MB。
docker run -it --cpu-period=100000 --cpu-quota=20000 -m 300M helloworld
```

`–cpu-period`和`–cpu-quota`组合使用来限制容器使用的CPU时间

- 表示在`–cpu-period`的一段时间内，容器只能被分配到总量为` --cpu-quota`的CPU时间



## 5.容器状态

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



## 6.维持容器运行状态

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



## 7.相关命令

### 7.1容器篇

- `docker ps`  查看当前**运行中**的容器，如果加上【-a选项，则可以查看运行中和已经停止的所有容器。】
- 容器创建
  - `docker create` + `docker start` == `docker run`
- 容器运行
  - `docker run` 
    - 执行该指令 会 返回容器ID
    - `-d` 运行web任务的容器通常以 后台进程进行的
    - `--name [name]`  指定容器名字
- 指定容器停止
  - `docker stop(kill) ID/NAME`
- 查看当前运行中的容器
  - `docker ps`
    - `-a`  查看运行中和已经停止的所有容器
- 进入容器
  - `docker attach LongID`
  - `docker exec -it ShortID bash`
    - `-it`  连接到容器后，启动一个terminal（终端）并开启input（输入）功能。-it后面接的是容器的名称或者容器的ID，/bin/sh表示进入到容器后执行的命令
  - attach和exec的区别
    - attach直接进入容器，启动命令的终端，不会启动新的进程
      - 缺点：当多个窗口同时attach到同一个容器时，所有的窗口都会同步的显示，假如其中的一个窗口发生阻塞时，其它的窗口也会阻塞
    - exec则是在容器中打开新的终端，并且可以启动新的进程
- 暂停容器
  - `docker pause ShortID`
- 恢复暂停容器
  - `docker unpause ShortID`
- 删除容器
  - `docker rm ShortID`
    - `-f`  删除处于任何状态下的容器. 
    - 不带`-f`选项，只能删除处于非Up状态的容器

### 7.2镜像篇

- 容器成为镜像
  - `docker commit`
- 查看镜像
  - `docker image ls`
- 查看镜像的元信息
  - `docker inspect [ helloworld:latest ]`
- 删除镜像
  - `docker image rm`

## Docker toolbox

> 内核都在虚拟机里面运行

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





