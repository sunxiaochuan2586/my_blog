<h2>windows下部署</h2>

首先创建一个名为venv的文件夹
> python -m venv venv

输入以下指令进入虚拟环境
> .\venv\Scripts\activate


```
At line:1 char:1
+ .\venv\Scripts\activate
+ ~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : SecurityError: (:) [], PSSecurityException
    + FullyQualifiedErrorId : UnauthorizedAccess
```
如果出现以上报错，在终端输入以下命令
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass  

然后输入再输入一次上面的指令就可以了

在虚拟环境里安装
> pip install flask flask_sqlalchemy flask_bcrypt flask_login flask_migrate markdown
> pip install email_validator
> pip install flask-wtf
> pip install tzdata
> pip install mistune


在项目目录下创建一个instance文件夹
运行
> $env:FLASK_APP = "run.py"

> flask db init       # 初始化 migration 文件夹（只做一次）

> flask db migrate -m "Initial migration"  # 自动生成迁移脚本

> flask db upgrade    # 应用迁移，创建数据库

给予账号管理员权限
> python -m flask commands make-admin "注册邮箱"
