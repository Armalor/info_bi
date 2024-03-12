### Установка сервиса

```shell
cp  /var/www/backend/webserver.service /etc/systemd/system

systemctl enable webserver.service
systemctl start webserver.service

systemctl status webserver.service
```

##### Рестарт
```shell
systemctl restart webserver.service
```

##### Просмотр текущего состояния
```shell
journalctl --follow -u webserver.service
```
