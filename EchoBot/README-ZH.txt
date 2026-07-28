广播机器人便携版 使用说明

1. 启动机器人：
   - 调试模式（显示窗口）：双击 run_broadcast.bat
   - 后台静默模式（无窗口）：双击 run_broadcast_hidden.vbs

2. 停止机器人：
   - 双击 stop_broadcast.vbs（会杀掉所有 python.exe 进程）

3. 开机自启动：
   - 按 Win+R，输入 shell:startup，回车
   - 把 run_broadcast_hidden.vbs 的快捷方式放进去

4. Web 管理面板：
   - 双击 broadcast_manager.html 在浏览器中打开
   - 可实现启动/暂停/停止、修改间隔、发送消息、查看在线用户

5. 修改配置：
   - 用记事本打开 broadcast-new.py，修改 ROOM、INTERVAL、关键词回复等。

6. 注意事项：
   - 使用公共 MQTT 服务器，消息不加密，勿发隐私信息。
   - 如需更改城市天气，修改 broadcast-new.py 中 wttr.in/Beijing 部分。

有任何问题，请联系机器人管理员。
