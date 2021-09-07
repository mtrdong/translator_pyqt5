# 基于PyQT5的百度翻译



> 封装exe可执行文件时，需修改`PyExecJS`的`_external_runtime.py`第121行代码：

```python
Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, cwd=self._cwd, universal_newlines=True, creationflags=CREATE_NO_WINDOW)
```



> 封装exe单文件版（启动慢）：

```shell
pyinstaller main-single.spec
```



> 封装exe便携版（启动快）：

```shell
pyinstaller main-portable.spec
```

