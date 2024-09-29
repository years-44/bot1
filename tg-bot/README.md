<div align="center">

# tg-dice-bot

_Telegram骰子机器人_

该骰子机器人项目已**升级**为功能更强大的<a href="https://github.com/deanxv/telegram-dice-bot" style="font-size: 20px;">Telegram-Dice-Bot 骰子娱乐机器人</a>

</div>

## 功能

1. 记录开奖历史
2. 记录下注记录
3. 支持积分系统
4. 支持签到奖励
5. 支持领取低保
   ...

### Bot命令

```
/help                帮助
/start               开启
/stop                关闭
/register            用户注册
/sign                用户签到
/my                  查询积分
/myhistory           查询历史下注记录
/iampoor             领取低保
玩法例子(竞猜-单,下注-20): #单 20
默认开奖周期: 1分钟

支持下注种类: 单、双、大、小、豹子
```

### 功能示例

![IMG](https://s2.loli.net/2023/12/12/Y6mBkRM94rUKLul.gif)


## 部署

### 基于 Docker-Compose(All In One) 进行部署

```shell
docker-compose pull && docker-compose up -d
```

#### docker-compose.yml
```docker
version: '3.4'

services:
  tg-dice-bot:
    image: ghcr.io/deanxv/tg-dice-bot:latest
    container_name: tg-dice-bot
    restart: always
    volumes:
      - ./data/tgdicebot:/data
    environment:
      - MYSQL_DSN=tgdicebot:123456@tcp(db:3306)/dice_bot  # 可修改此行 SQL连接信息
      - REDIS_CONN_STRING=redis://redis
      - TZ=Asia/Shanghai
      - TELEGRAM_API_TOKEN=6830xxxxxxxxxxxxxxxx3GawBHc7ywDuU  # 必须修改此行telegram-bot的token
    depends_on:
      - redis
      - db

  redis:
    image: redis:latest
    container_name: redis
    restart: always

  db:
    image: mysql:8.2.0
    restart: always
    container_name: mysql
    volumes:
      - ./data/mysql:/var/lib/mysql  # 挂载目录，持久化存储
    ports:
      - '3306:3306'
    environment:
      TZ: Asia/Shanghai   # 可修改默认时区
      MYSQL_ROOT_PASSWORD: 'root@123456' # 可修改此行 root用户名 密码
      MYSQL_USER: tgdicebot   # 可修改初始化专用用户用户名
      MYSQL_PASSWORD: '123456'    # 可修改初始化专用用户密码
      MYSQL_DATABASE: dice_bot   # 可修改初始化专用数据库
```

### 基于 Docker 进行部署

```shell
docker run --name tg-dice-bot -d --restart always \
-e MYSQL_DSN="root:123456@tcp(localhost:3306)/dice_bot" \
-e REDIS_CONN_STRING="redis://default:<password>@<addr>:<port>" \
-e TELEGRAM_API_TOKEN="683091xxxxxxxxxxxxxxxxywDuU" \
deanxv/tg-dice-bot
```

其中，`MYSQL_DSN`,`REDIS_CONN_STRING`,`TELEGRAM_API_TOKEN`修改为自己的，Mysql中新建名为`dice_bot`的db。

如果上面的镜像无法拉取，可以尝试使用 GitHub 的 Docker 镜像，将上面的 `deanxv/tg-dice-bot`
替换为 `ghcr.io/deanxv/tg-dice-bot` 即可。

### 部署到第三方平台

<details>
<summary><strong>部署到 Zeabur</strong></summary>
<div>

> Zeabur 的服务器在国外，自动解决了网络的问题，同时免费的额度也足够个人使用

点击一键部署:

[![Deploy on Zeabur](https://zeabur.com/button.svg)](https://zeabur.com/templates/SEFL7Z?referralCode=deanxv)

**一键部署后 `MYSQL_DSN` `REDIS_CONN_STRING` `TELEGRAM_API_TOKEN`变量也需要替换！**

或手动部署:

1. 首先 fork 一份代码。
2. 进入 [Zeabur](https://zeabur.com?referralCode=deanxv)，登录，进入控制台。
3. 新建一个 Project，在 Service -> Add Service 选择 prebuilt，选择 MySQL，并记下连接参数（用户名、密码、地址、端口）。
4. 新建一个 Project，在 Service -> Add Service 选择 prebuilt，选择 Redis，并记下连接参数（密码、地址、端口）。
5. 使用mysql视图化工具连接mysql，运行 ```create database `dice_bot` ``` 创建数据库。
6. 在 Service -> Add Service，选择 Git（第一次使用需要先授权），选择你 fork 的仓库。
7. Deploy 会自动开始，先取消。
8. 添加环境变量

   `MYSQL_DSN`:`<username>:<password>@tcp(<addr>:<port>)/dice_bot`

   `REDIS_CONN_STRING`:`redis://default:<password>@<addr>:<port>`

   `TELEGRAM_API_TOKEN`:`你的TG机器人的TOKEN`

   保存。
9. 选择 Redeploy。

</div>
</details>



## 配置

### 环境变量

1. `MYSQL_DSN`：`MYSQL_DSN=root:123456@tcp(localhost:3306)/dice_bot`
2. `REDIS_CONN_STRING`：`REDIS_CONN_STRING:redis://default:<password>@<addr>:<port>`
3. `TELEGRAM_API_TOKEN`：`683091xxxxxxxxxxxxxxxxywDuU` 你的TG机器人的TOKEN
