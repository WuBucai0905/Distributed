夜神模拟器

Fiddle抓包工具

mitmproxy中间人攻击

- 1、基于python
- 2、windows操作系统需要安装Microsoft Visual C++ V14.0以上
- 3、linux操作系统则直接基于python安装即可

Appium

封装了标准Selenium客户端类库

**aapt.exe 获取appium相关参数**

```
aapt.exe dump badging (app路径文件名)
package.name
launchable-activity.name
# 方式二（简单）
aapt dump badging (app路径文件名) | find "launchable-activity"
# 方式三
adb shell -> logcat | grep cmp= ->
```

### Android开发环境安装

Android SDK 指的是Android专属的软件开发工具包

安装SDK

- 配置JDK环境

  - java --> jdk / jre
  - 设置JAVA环境变量

  ```
  变量名：Path
  变量值：C:\ProgramData\Oracle\Java\javapath;%java_home%\bin;%java_home%\jre\bin
  新建
  变量名：JAVA_HOME
  变量值：C:\java\jdk
  新建
  变量名：ClassPath
  变量值：.;%JAVA_HOME%\lib\dt.jar;%JAVA_HOME%\lib\tools.jar;
  ```

- SDK安装

  - 设置SDK环境

    ```
    ANDROID_HOME	C:\SDK
    PATH	;%ANDROID_HOME%\platform-tools;%ANDROID_HOME%\tools;
    ```

  - SDK Manager --> 修改 hosts 文件

uiautomator 工具

- uiautomatorviewer – 一个图形界面工具来扫描和分析应用的UI控件。存放在tools目录

- uiautomator – 一个测试的Java库，包含了创建UI测试的各种API和执行自动化测试的引擎。

adb工具

- 所有 adb 客户端均使用端口 5037 与 adb 服务器通信


- 使用adb命令工具，需要移动客户端（手机）开启开发者模式，并允许USB调试

**adb连接出现版本问题时：**

```
# SDK/piatform-tools --> 夜神模拟器中替代这四个文件
adb.exe
AdbWinApi.dll
AdbWinUsbApi.dll
nox_adb.exe 用现在的adb.exe代替
```

**当adb未连接到devices时：**

```
adb connect 127.0.0.1:62025
```

**怎么查看包名**

```
/data/app/		or	
adb shell pm list package
```

**PC端与模拟器端互传**

```
PC端传文件到 模拟器
adb push (PC路径) (夜深路径)
反向
adb pull (夜深路径) (PC路径)
```


