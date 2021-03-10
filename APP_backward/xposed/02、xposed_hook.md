
###hook普通方法、静态方法
```
    public void handleLoadPackage(LoadPackageParam lpparam) throws Throwable {
    // 获取应用程序的包名
    String pack = lpparam.packageName;
        if ("org.foyou.bbb".equals(pack)) {
            XposedBridge.log("目标程序已启动——开始Hook");
            //获取类
            Class clazz = lpparam.classLoader.loadClass(pack + ".MainActivity");
            //获取控件
            final Field field = clazz.getDeclaredField("tv");
            field.setAccessible(true);
            //hook普通方法、静态方法
            XposedHelpers.findAndHookMethod(clazz,
                            "onClick", 
                            View.class, 
                            new XC_MethodReplacement() {
                @Override
                protected Object replaceHookedMethod(MethodHookParam param) throws Throwable {
                    XposedBridge.log("Hook onClick 成功");
                    TextView tv = (TextView) field.get(param.thisObject);
                    tv.setText(i-- + "");
                    return null;
                }
            });
            //hook匿名内部类
            // 反编译拿到smail文件，找到 要hook的方法在哪个smail文件内
            ...$1...
        }
    }

```

###hook匿名内部类


###主动调用方法
```
XposedHelpers.call...
XposedHelpers.callStaticMethod(
    param.thisObject.getClass(),
    "toHexString",
    new Object[]{
        ...args
    }
)
```