# 发布订阅

发布订阅里面有哪些模块？ 角色、发布者、频道、订阅者

```python
######api#######
发布publish channel message 返回订阅者个数
订阅subscribe [channel]
取消订阅unsubscribe [channel]
```

# 2.持久化

将 内存中的数据异步的保存到磁盘上的操作

## 2.1实现方式

### 2.1.1快照

redis的RDB；	mysql的dump

#### RDB

触发机制【主要三种方式】

- save【同步】	文件策略：RDB文件新替换老	复杂度o(n)
- bgsave【异步】fork() 
- 自动

```
# 最佳配置
dbfilename  dump-$(port).rdb
dir /bigdiskpath
stop-writes-on-bgsave-error yes
rdbcompression yes # 压缩
rdbchecksum yes # 检验
```

### 2.1.2写日志

redis的AOF；	mysql的binlog

> 使用AOF原因： RDB问题：耗时，耗性能；不可控，丢失数据

#### AOF

将读写操作通过自己的方式写入到AOF文件中

##### 三种策略

- always	缓冲区的写命令 每条命令fsync到硬盘的aof文件中

- everysec	缓冲区的写命令 每秒的命令fsync到硬盘的aof文件中

- no	OS决定 fsync

##### 实现方式

bgrewriteaof

fork子进程

AOF重写配置

**配置**

auto-aof-rewrite-min-size	aof文件重写需要的尺寸 

auto-aof-rewrite-percentage	aof文件增长率

**统计项**

aof-current-size	aof当前尺寸（字节）

aof-base-size	aof上次启动和重写的尺寸

同时满足时会实现自动重写

- aof-current-size > auto-aof-rewrite-min-size;

- aof-current-size - aof-base-size / aof-base-size > auto-aof-rewrite-percentage

```
# 配置
appendonly yes
appendfilename ...
appendfsync everysec
dir ...
no-appendfsync-in-rewrite yes	# aof重写时非常消耗性能的
auto-aof-rewrite-precentage 100
auto-aof-rewrite-min-size 64mb
```

aof重启加载时是否去忽略错误（突然死机）：aof-load-truncated  yes

### 持久化开发运维问题

fork操作时一个同步操作，不是一个内存的完整的拷贝，

看fork执行的时间	info: latest-fork-usec

#### 改善fork：

- 好的物理机或高效支持fork操作的虚拟化操作
- 控制redis实例最大可用内存: maxmemory
- 合理配置Linux内存分配策略

#### 子进程的开销与优化

cpu：rdb与aof文件生成 属于cpu密集型

​		优化： 不做CPU绑定，不和cpu密集型部署

内存：fork内存开销。copy-on-write

硬盘：rdb与aof文件写入

​		优化：不与高硬盘负载服务部署一起；	no-appendfsync-on-rewrite = yes

## 主从复制

单机瓶颈	主从复制可以实现读写分离

```
取消复制 slaveof no one
```

**配置**

```
slaveof ip port
```

变成从节点时 会对当前已有的数据进行清除

### 全量复制

run_id：标识 （重启或者其他重大变化，run-id改变，从节点同步：全量复制）

偏移量： 总从写入的多少的数字化显示

#### 开销

bgsave

rdb文件网络传输时间

从节点清空数据时间

从节点加载rdb的时间

可能的aof重写时间

### 部分复制

######################################

### 故障处理

### 主从复制常见问题

#### 读写分离

读流量分摊到从节点

**可能遇到问题**

复制数据延迟（阻塞，可以通过偏移量来监控这个问题）

读到过期数据（slave不能写数据）

从节点故障

#### 主从配置不一致

maxmemory不一致：丢失数据

数据结构优化参数：内存不一致

#### 规避全量复制

开销非常大

第一次全量复制不可避免

**解决**

小主节点，低峰

节点运行ID不匹配

主节点重启（运行ID变化）

**解决**

故障转移，例如：哨兵或集群

复制积压缓冲区不足

网络中断，部分复制无法满足

**解决**

增大复制缓冲区设置，网络增强

#### 规避复制风暴

单主节点复制风暴

问题：主节点重启，多从节点复制

解决：更换复制拓扑

#### 单机器复制风暴

问题：机器死机后，大量全量复制

解决：主节点分散多机器

## sentinel

主从复制高可用

**主从复制问题**

- 手动故障转移
- 写能力和存储能力受限

### 安装与配置

主从节点配置

#######################################

sentinel主要配置

```
port ${port}
dir ...
logfile "..."
sentinel monitor mymaster ip port 2 # 几个sentinel发现有故障时出现故障转移
# 三个定时任务每1秒回去ping；30秒没收到回复会做下线的判断（主观下线）
sentinel down-after-milliseconds mymaster 30000 # ping 30秒不通认为出现故障发生转移
sentinel parallel-syncs mymaster 1 # 选择新master后 slave并发还是串行复制
sentinel failover-timeout mymaster 180000 # 默认转移时间
```

### 三个定时任务

每10秒 每个sentinel对master和slave执行info；

- 发现slave节点
- 确定主从关系

每2秒 每个sentinel通过master节点的channel交换信息(pub/sub)

- 通过 __ sentinel __:hello 频道交互
- 交互对节点的 看法 和自身信息

每1秒 每个sentinel 对其他sentinel和redis执行ping

- 心跳检测

### 主观下线和客观下线

主观下线：每个sentinel节点对 redis节点失败的 ”偏见“；

客观下线：所有sentinel节点对 redis节点失败 达成共识，超过quorum个统一；

```
sentinel is-master-down-by-addr
```

### 领导者选举

只需要一个 sentinel 节点完成故障转移

通过 sentinel is-master-down-by-addr 命令都想要成为领导者

- 每个做主观下线的sentinel节点 向其他sentinel节点发送命令，要求将其设置为领导者
- 收到命令的sentinel节点如果没有同意通过其他sentinel节点发送的命令，将会同意请求，否则拒绝
- 该sentinel节点发现自己的票数超过sentinel半数且超过quorum，将成为领导者
- 多个sentinel成为领导者将会等待一段时间后重新选举

### 故障转移

1. 从slave节点中选出一个 合适的节点作为新的 master节点
2. 对上面的slave节点执行slaveof no one 让其成为 master节点
3. 向剩余的slave节点发送命令，让他们成为新的master节点的slave节点，复制规则和parallel-syncs参数有关
4. 更新对原来master节点配置为slave，并保持着对其关注，当其恢复后 去复制新的master节点

#### 怎么选择合适的slave节点？

- 选择 slave-priority(节点优先级)最高的slave节点，存在则返回，不存在则继续
- 选择复制偏移量最大的slave节点(复制的最完整)，存在则返回，不存在则继续

### sentinel开发运维问题

#### 节点运维

##### 节点下线

###### 主节点

```
# 忽略主观下线、客观下线和领导者选举等步骤
sentinel failover <mastername>
```

###### 从节点

临时下线还是永久下线？是否做一些清理工作？考虑读写分离的情况

###### sentinel节点

同从节点

##### 节点上线

###### 主节点

sentinel failover进行替换

###### 从节点

slaveof即可，sentinel可以感知

#### 高可用读写分离

##### 从节点的作用

副本：高可用的基础

扩展：读能力

#### 关注slave的三个消息

switch-master

convert-to-slave（原主节点降为从节点）

sdown主观下线

