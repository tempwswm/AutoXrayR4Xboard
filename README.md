# NodeController

## 介绍
从XBoard获取信息然后自动部署XrayR节点的工具

暂时只支持ss节点

## 使用
### 服务端
```shell
docker run -d \
--network=host --restart=always \
--name board_watcher ghcr.io/tempwswm/autoxrayr4xboard:master \
-s --url http://192.168.35.129:4567/token \
--board_url http://192.168.35.129:7001/841315ed \
--board_email admin@demo.com --board_password aaaaaaaaaa 
```

### 节点端
```shell
docker run -d --restart=always \
-v /var/run/docker.sock:/var/run/docker.sock \
-v /etc/XrayR/config.yml:/etc/XrayR/config.yml \
--name node_deployer ghcr.io/tempwswm/autoxrayr4xboard:master \
-n --url http://192.168.35.129:4567/token \
--label label
```

## 配置
在XBoard内配置节点时在IPs填入对应的Label，即可自动部署到对应机器上