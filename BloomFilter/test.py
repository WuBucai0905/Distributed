import redis
from BloomFilter import BloomFilter
import mmh3
import math
from utils import acquire_lock_with_timeout, release_lock


class RedisFilter(BloomFilter):

    SEEDS = [543, 460, 171, 876, 796, 607, 650, 81, 837, 545, 591, 946, 846, 521, 913, 636, 878, 735, 414, 372,
             344, 324, 223, 180, 327, 891, 798, 933, 493, 293, 836, 10, 6, 544, 924, 849, 438, 41, 862, 648, 338,
             465, 562, 693, 979, 52, 763, 103, 387, 374, 349, 94, 384, 680, 574, 480, 307, 580, 71, 535, 300, 53,
             481, 519, 644, 219, 686, 236, 424, 326, 244, 212, 909, 202, 951, 56, 812, 901, 926, 250, 507, 739, 371,
             63, 584, 154, 7, 284, 617, 332, 472, 140, 605, 262, 355, 526, 647, 923, 199, 518]

    def __init__(self, host='localhost', port=6379, db=0, redis_key='bloomfilter_'):
        """

        :param host:
        :param port:
        :param db:
        :param key:
        """
        self.server = redis.Redis(host=host, port=port, db=db)
        self.redis_key = redis_key

        # 已存数据量
        self._data_count = 0

    def start(self, data_size, error_rate=0.001):
        """

        :param data_size: 所需存放数据的数量
        :param error_rate:  可接受的误报率，默认0.001
        :return:

        启动函数，通过数据量、误报率 确定位数组长度、哈希函数个数、哈希种子等
        """
        if not data_size > 0:
            raise ValueError("Capacity must be > 0")
        if not (0 < error_rate < 1):
            raise ValueError("Error_Rate must be between 0 and 1.")

        # 去重的数量
        self.data_size = data_size
        # 错误率
        self.error_rate = error_rate

        bit_num, hash_num = super()._adjust_param(data_size, error_rate)
        self._bit_num = bit_num if bit_num < (1 << 32) else (1 << 32)
        self._hash_num = hash_num
        # redis字符串最长为512M
        self._block_num = 1 if bit_num < (1 << 32) else math.ceil(math.ceil(bit_num/8/1024/1024)/512)
        # 将哈希种子固定为 1 - hash_num （预留持久化过滤的可能）
        # self._hash_seed = [i for i in range(1, hash_num+1)]
        self._hash_seed = self.SEEDS[0:hash_num]

    def add(self, key):
        """
        :param key: 要添加的数据
        :return:

        >>> bf = BloomFilter(data_size=100000, error_rate=0.001)
        >>> bf.add("test")
        True

        """
        if self._is_half_fill():
            raise IndexError("The capacity is insufficient")

        # keyname = self.redis_key + str(sum(map(ord, key)) % self._block_num)

        keyname = self.redis_key + "_" + str(ord(key[0]) % self._block_num)

        hashs = self.get_hashes(key)
        for hash in hashs:
            self.server.setbit(keyname, hash, 1)

        # key_hashed_idx = []
        # for time in range(self._hash_num):
        #     key_hashed_idx.append(mmh3.hash(keyname, self._hash_seed[time]) % self._bit_num)
        #
        # lock = acquire_lock_with_timeout(self.server, key)
        # if lock:
        #     for idx in key_hashed_idx:
        #         self.server.setbit(keyname, idx, 1)
        #
        #     self._data_count += 1
        #     release_lock(self.server, key, lock)

    def is_exists(self, key):
        """
        :param key:
        :return:

        判断该值是否存在
        有任意一位为0 则肯定不存在
        """
        keyname = self.redis_key + str(sum(map(ord, key)) % self._block_num)

        # hashs = self.get_hashes(key)
        # exist = True
        # for hash in hashs:
        #     exist = exist & self.server.getbit(keyname, hash)
        # return exist

        # lock = acquire_lock_with_timeout(self.server, key)


        for time in range(self._hash_num):
            key_hashed_idx = mmh3.hash(keyname, self._hash_seed[time]) % self._bit_num
            # 1代表有
            if not int(self.server.getbit(keyname, key_hashed_idx)):    # 类型？
                # release_lock(self.server, key, lock)
                return False

        # release_lock(self.server, key, lock)
        return True

    def get_hashes(self, key):
        key_hashed_idx = []
        for time in range(self._hash_num):
            key_hashed_idx.append(mmh3.hash(key, self._hash_seed[time]) % self._bit_num)
        return key_hashed_idx



if __name__ == '__main__':

    bf = RedisFilter()
    bf.start(10000, 0.0001)
    # # 仅测试输出，正常使用时透明
    # print(bf._bit_num, bf._hash_num)
    # print(bf._block_num)
    # print(bf._bit_num)

    a = ['when', 'how', 'where', 'too', 'there', 'to', 'when']
    for i in a:
        bf.add(i)

    # print('qwe in bf?: ', 'qwe' in bf)

    b = ['when', 'igdhfhfgfhfhtr', 'qwedafdgfdyjjyj']
    for i in b:
        if bf.is_exists(i):
            print('%s exist' % i)
        else:
            print('%s not exist' % i)

