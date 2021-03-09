
###导入 jar 包
本地包 放的位置是 lib 而不是libs
工具包在libs文件中，默认是加入到编译路径中的，编译出来的程序中也是包含了这个 工具包中的所有类，
其他文件夹 添加工具包然后 add buildpath 后只是工程引用工具包功能

###注册到清单
```
<meta-data
    android:name="xposedmodule"
    android:value="true"/>     <!--表示是xpose模块，因此xpose框架能识别它-->
<meta-data
    android:name="xposeddescription"
    android:value="module test"/>  <!--对模块功能的描述信息-->
<meta-data
    android:name="xposedminversion"
    android:value="54"/><!--jar包的最低版本，包是54，你这里写30也没问题的-->
```

###新建类，实现框架接口和方法

###注册指明实现框架的类
新建asset文件夹，新建一个无后缀的文件，文件名 xposed_init，并将该类的全包名写进去