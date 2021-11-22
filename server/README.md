# 使用 pip 管理依赖

以 Flask 为例，首先是安装依赖：

```bash
(snow-venv) $ pip install flask
```

更新依赖：

```bash
(snow-venv) $ pip install --upgrade flask
```

或是：

```bash
(snow-venv) $ pip install -U flask
```

卸载依赖：

```bash
(snow-venv) $ pip uninstall flask
```

除此之外，还有 `pip show flask` 命令可以查看某个依赖的详细信息，`pip list` 列出所有依赖。

下面的命令可以手动生成依赖列表：

```bash
(snow-venv) $ pip freeze > requirements.txt
```

如果你需要手动开发依赖和生产依赖，可以手动把开发相关的依赖放到单独的文件，比如 requirements-dev.txt。

当你需要在新的机器创建程序运行环境时，（创建虚拟环境后）只需要使用下面的命令从依赖文件安装所有依赖：

```bash
(snow-venv) $ pip install -r requirements.txt
```

如果安装包的时候速度太慢，可以考虑设置 PyPI 国内镜像，具体参考这篇文章。