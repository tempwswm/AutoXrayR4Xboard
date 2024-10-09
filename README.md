# AutoXrayR4XBoard

## 介绍
从XBoard获取信息然后自动部署XrayR节点的工具

暂时只支持ss节点（因为我还只学会这个，等我学会如何手动搭建其他类型，那么将会添加自动操作）

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

# 感谢
- [tempwswm](https://github.com/tempwswm) 
- [Xboard](https://github.com/cedar2025/Xboard)
- [XrayR](https://github.com/XrayR-project/XrayR)
- 其他相关项目、人员
- 给我打钱以及给我roll小鸡的人

# 讨饭
以下是我的USDT钱包，我很可爱，请给我钱 (╹ڡ╹ )
```
TRNVdKwdMZgbGtWyxBao8gRcKN2tf9aBHv
```