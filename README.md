# 基于PyQT5的百度翻译

**通过`requests`获取翻译结果，使用`PyQT5`设计界面，使用`SystemHotkey`设置全局快捷键**

**1. 实现基本翻译功能**

**2. 实现截图（支持快捷键F1启动）或拖入图片进行识别翻译**

**3. 实现伪划词（复制）翻译，悬浮窗方式输出翻译结果**

**4. 支持音标发音，翻译结果播报**

**5. 支持一键复制翻译结果**

......



> 封装exe可执行文件时，需修改`PyExecJS`的`_external_runtime.py`第1、121行代码：

```python
from subprocess import Popen, PIPE, CREATE_NO_WINDOW  # 第1行
Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, cwd=self._cwd, universal_newlines=True, creationflags=CREATE_NO_WINDOW)  # 第121行
```



> 封装exe单文件版（启动慢）：

```shell
pyinstaller main-single.spec
```



> 封装exe便携版（启动快）：

```shell
pyinstaller main-portable.spec
```



> 解决Linux运行程序时报错：`Could not load the Qt platform plugin "xcb" in "" even though it was found.`：

```shell
sudo apt-get install libxcb-xinerama0
```



> 解决Linux运行程序时报错：`Could not find an available JavaScript runtime.`：

```shell
sudo apt-get install nodejs
```



> 解决Linux运行程序无法输入中文：

复制文件：`/usr/lib/x86_64-linux-gnu/qt5/plugins/platforminputcontexts/libfcitxplatforminputcontextplugin.so`

到：`site-packages/PyQt5/Qt5/plugins/platforminputcontexts`

