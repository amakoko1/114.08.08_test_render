# Dockerfile
FROM alpine:latest
ARG FRP_VERSION=0.59.0
ARG TARGETARCH
RUN apk add --no-cache curl tar gzip && \
    case ${TARGETARCH} in \
        "amd64") ARCH="amd64" ;; \
        "arm64") ARCH="arm64" ;; \
        *) echo "Unsupported arch: ${TARGETARCH}"; exit 1 ;; \
    esac && \
    FRP_FILENAME="frp_${FRP_VERSION}_linux_${ARCH}" && \
    curl -Lo ${FRP_FILENAME}.tar.gz "https://github.com/fatedier/frp/releases/download/v${FRP_VERSION}/${FRP_FILENAME}.tar.gz" && \
    tar -zxvf ${FRP_FILENAME}.tar.gz && \
    mv ${FRP_FILENAME}/frps /usr/bin/frps && \
    rm -f ${FRP_FILENAME}.tar.gz "frp_${FRP_VERSION}_linux_${ARCH}/frpc*"

# 使用無參數的 CMD，frps 將自動從環境變數讀取所有配置
CMD ["/usr/bin/frps"]
