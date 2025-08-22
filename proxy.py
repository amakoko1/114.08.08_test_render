import asyncio
import os
import sys

# --- 組態設定 ---
# 監聽的 HOST，在容器環境中必須是 '0.0.0.0'
LISTEN_HOST = '0.0.0.0'
# Render 會透過 'PORT' 環境變數告訴我們應該監聽哪個埠
# 我們給一個預設值 10000 方便在本機測試
LISTEN_PORT = int(os.environ.get('PORT', 10000))

# 目標伺服器 (IB TWS) 的資訊，從環境變數讀取
TARGET_HOST = os.environ.get('TARGET_HOST')
TARGET_PORT = int(os.environ.get('TARGET_PORT', 0))

# --- 核心邏輯 ---

async def pipe(reader, writer, pipe_name):
    """
    一個非同步的 "管線"，不斷從 reader 讀取數據並寫入 writer。
    """
    try:
        while not reader.at_eof():
            data = await reader.read(4096)
            if not data:
                break
            writer.write(data)
            await writer.drain()
    except ConnectionResetError:
        print(f"[{pipe_name}] 連線被重設。")
    except Exception as e:
        print(f"[{pipe_name}] 發生未知錯誤: {e}")
    finally:
        writer.close()
        # print(f"[{pipe_name}] 管線已關閉。")


async def handle_connection(client_reader, client_writer):
    """
    處理每一個來自您本地電腦的新連線。
    """
    client_addr = client_writer.get_extra_info('peername')
    print(f"[新連線] 接收到來自 {client_addr} 的連線請求。")

    try:
        # 連接到真正的 IB 伺服器
        print(f"[代理中] 正在嘗試連接到目標: {TARGET_HOST}:{TARGET_PORT}...")
        target_reader, target_writer = await asyncio.open_connection(
            TARGET_HOST, TARGET_PORT)
        target_addr = target_writer.get_extra_info('peername')
        print(f"[代理成功] 已建立通道: {client_addr} <--> {target_addr}")

        # 建立兩個雙向的管線，並同時運行它們
        await asyncio.gather(
            pipe(client_reader, target_writer, f"{client_addr[0]}:{client_addr[1]} -> IB"),
            pipe(target_reader, client_writer, f"IB -> {client_addr[0]}:{client_addr[1]}")
        )

    except Exception as e:
        print(f"[錯誤] 無法連接到目標 {TARGET_HOST}:{TARGET_PORT}。錯誤: {e}")
    finally:
        client_writer.close()
        await client_writer.wait_closed()
        print(f"[連線關閉] {client_addr} 的連線已完全終止。")


async def main():
    """
    主函數，啟動代理伺服器。
    """
    if not TARGET_HOST or not TARGET_PORT:
        print("錯誤: 必須設定 'TARGET_HOST' 和 'TARGET_PORT' 環境變數。")
        sys.exit(1)

    print(f"--- TCP 代理伺服器啟動 ---")
    print(f"監聽位址: {LISTEN_HOST}:{LISTEN_PORT}")
    print(f"轉發目標: {TARGET_HOST}:{TARGET_PORT}")
    print("-------------------------")

    server = await asyncio.start_server(
        handle_connection, LISTEN_HOST, LISTEN_PORT)

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n伺服器已手動關閉。")
