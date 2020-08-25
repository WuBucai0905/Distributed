数据通过Ajax加载，Ajax接口加密，需要破解才能获取数据。

绕过使用 selenium ， selenium模拟操作又不好获取Ajax的数据了。通过渲染后的HTML提取数据又非常麻烦

解决：

selenium 驱动页面，又把Ajax请求的数据保存下来

1. 代理mitmdump
2. AjaxHook



AjaxHook作者提供了两个主要方法，一个是 proxy，一个是 hook，起作用都是来 Hook XMLHttpRequest 的

- hook 的拦截粒度细，可以具体到 XMLHttpRequest 对象的某一方法、属性、回调，但是使用起来比较麻烦，很多时候，不仅业务逻辑需要散落在各个回调当中，而且还容易出错。
- 而 proxy 抽象度高，并且构建了请求上下文，请求信息 config 在各个回调中都可以直接获取，使用起来更简单、高效。

使用方法

```
proxy({
    //请求发起前进入
    onRequest: (config, handler) => {
        console.log(config.url)
        handler.next(config);
    },
    //请求发生错误时进入，比如超时；注意，不包括http状态码错误，如404仍然会认为请求成功
    onError: (err, handler) => {
        console.log(err.type)
        handler.next(err)
    },
    //请求成功后进入
    onResponse: (response, handler) => {
        console.log(response.response)
        handler.next(response)
    }
})
```

数据爬取就只要实现 onResponse 方法。



### 实操

1. 引入ajaxHook

   `https://github.com/wendux/Ajax-hook/blob/master/dist/ajaxhook.min.js`

2. 代码复制到网站的控制台里，得到 ah 对象，对象里就存在着 proxy 方法

3. 实现 onResponse 方法

   ```
   ah.proxy({
     //请求成功后进入
     onResponse: (response, handler) => {
       if (response.config.url.startsWith('/api/movie')) {
         console.log(response.response)
         handler.next(response)
       }
     }
   })
   ```

4. 此时就可以获取到Ajax的数据了。

### 存储浏览器里的数据

flask 弄个接口，解除跨域限制

```
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/receiver/movie', methods=['POST'])
def receive():
    content = json.loads(request.data)
    print(content)
    # to something
    return jsonify({'status': True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
```

此时可以完成 数据的切割和存储数据库...

#### axios库

放到 浏览器执行就能用

`https://unpkg.com/axios@0.19.2/dist/axios.min.js`

**修改proxy方法**

```
ah.proxy({
  //请求成功后进入
  onResponse: (response, handler) => {
    if (response.config.url.startsWith('/api/movie')) {
      axios.post('http://localhost/receiver/movie', {
        url: window.location.href,
        data: response.response
      })
      console.log(response.response)
      handler.next(response)
    }
  }
})
```

1. 调用 axios 的 post 方法，把当前 url 和 Response 的数据发给了 Server。
2. 每次 Ajax 请求的 Response 结果都会被发给这个 Flask Server，Flask Server 对其进行存储和处理就好了

### 自动化

`https://mp.weixin.qq.com/s/Nw3ZoBHa4f4Ew8XEfuyY1g`

