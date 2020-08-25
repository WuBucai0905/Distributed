

## 设置 appium 容器连接安卓模拟器

### SCRT连接 模拟器

```
user:docker
password:tcuser
```

### 创建镜像

```
docker run --privileged -d -p 4723:4723 --name appium1 appium/appium
```

```
# 此时是无法连接上的，需要手动连接
docker exec -it appium1 adb devices
```

```
# 手动连接先需要本地设置(确保本地和模拟器是连接上的)
# 改变了当前模拟器的连接方式(USB -> IP:端口)
adb -s 127.0.0.1:62025 tcpip 5555
# 然后
docker exec -it appium1 adb connect 172.17.100.15:5555[模拟器的IP地址:自己改的端口号]
# 此时可以查看是否已经连接上
docker exec -it appium1 adb devices
```

### 查看日志

```
可
docker exec -it appium1 bash
# 日志放在 
cd /var/log --> appium.log
# 该命令查看日志
tail -f appium.log
```



## 多容器

抓取抖音当前视频的作者数据

抓取快手当前视频的作者数据

抓取今日头条推荐板块新闻

### 系统搭建

下载好镜像

设置 docker toolbox网卡状态到桥接

VM boxes --> 设置 --> 网络 --> 桥接网卡

设置docker toolbox共享，挂载共享文件夹

VM boxes --> 设置 --> 共享文件夹[固定分配]

创建并启动响应的容器

报错解决：

1. 升级virtualbox
2. 安装 虚拟机的网络桥接驱动【更改适配器设置 --> 无线网卡 --> 属性】
   1. ndis6 --> 安装  --> 服务 --> 添加 --> 从磁盘安装【虚拟机的安装目录 --> drivers -->network --> netlmf】

改变虚拟机网卡后 IP地址发生了变化

查看：

虚拟机内状态栏中的 显示 --> `ifconfig | more`,按下右边的CTRL鼠标就可以动了

虚拟机内部的代码挂载

命令行内共享文件夹的设置

```
mkdir docker
cd docker/
pwd 查看路径
把本地文件夹挂载到虚拟机里面来 sudo mount -t vboxsf [共享文件夹名称] [虚拟机里面路径]
sudo umount [虚拟机里面路径]
cd
sudo mount -t vboxsf [共享文件夹名称] [虚拟机里面路径]
```

虚拟机内部文件映射到容器里面

```
docker run -it -v [虚拟机里面文件路径]:/root/ --name python [镜像名称] /bin/bash
```

再开一个容器mitmdump

```
# --rm 退出自动删除
docker run --rm -it [虚拟机里面文件路径]:/root/ -p 8889:8889 --name mitmdump [镜像名称] mitmdump -p 8889 -s /root/decode_data.py
```

再开一个容器appium[多开改端口号]

```
docker run --privileged -d -p 4723:4723 --name appium_kaoyanbang appium/appium
# 4725:4723 外:内
# 4727:4723
```

再开一个容器mongo

```
# 挂载：需要将db文件 挂载到本地磁盘上
docker run -p 27017:27017 -v /home/docker/docker:/root/ -d --name mongodb mongo
```

夜神模拟器

需要网络为桥接模式

需要安装响应的证书【容器里面的证书】

