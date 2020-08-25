# express框架 开启服务

确保安装好Nodejs

### 安装

```
npm install express
```

### 实例

```
const express = require('express')
const app = express()

app.get('/', function (req, res) {
  res.send('Hello World')
})

app.listen(3000)
```

然后运行(控制台下输入node xxx.js),并打开浏览器

```
function(req, res){
	...
}
```

- `req.query`
- `res.send()` 返回结果