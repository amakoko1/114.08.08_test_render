# 使用官方或你信任的 frp 镜像
FROM snowdreamtech/frps:0.51.3
EXPOSE ${PORT:-8080} # 声明容器将监听的端口

# (可选) 如果你有自定义的 frps.ini 配置文件，可以复制进去
# 但请确保不要在 ini 文件中设置与环境变量冲突的项（如 port, vhost_http_port 等）
# COPY frps.ini /etc/frp/frps.ini

# 关键：确保 CMD 命令不使用 -c 参数加载配置文件，
# 这样 frps 才会默认从环境变量读取配置。
CMD ["frps"]
