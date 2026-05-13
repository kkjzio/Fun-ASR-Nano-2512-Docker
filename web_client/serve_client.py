"""
FunASR-Nano-2512 Client Web Server
作者：凌封
来源：https://aibook.ren (AI全书)
"""
import http.server
import socketserver
import os
import socket
import asyncio
import threading
import urllib.parse

PORT = 8001
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

# =====================================================================
# SOCKS5 代理 & WebSocket 中继配置
# 如不需要代理，将 SOCKS5_PROXY 设为 None
# =====================================================================
SOCKS5_PROXY = {
    "host": "192.168.59.129",   # SOCKS5 代理地址
    "port": 1080,           # SOCKS5 代理端口
    "username": None,       # 认证用户名（无需认证时设为 None）
    "password": None,       # 认证密码  （无需认证时设为 None）
}

WS_RELAY_PORT = 10096       # 本地 WebSocket 中继监听端口
WS_TARGET_URL  = "ws://19.71.10.65:8003"  # 目标 ASR 服务的 WebSocket 地址
# =====================================================================


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def get_ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

async def relay_handler(client_ws):
    """通过 SOCKS5 代理中继 WebSocket 连接"""
    parsed     = urllib.parse.urlparse(WS_TARGET_URL)
    target_host = parsed.hostname
    target_port = parsed.port or 10095

    try:
        import websockets
        from python_socks.async_.asyncio import Proxy
    except ImportError as e:
        print(f"[中继] 缺少依赖: {e}")
        print("[中继] 请运行: pip install websockets python-socks")
        await client_ws.close(1011, "missing dependency")
        return

    try:
        connect_kwargs = dict(subprotocols=["binary"], ping_interval=None)

        if SOCKS5_PROXY:
            user = SOCKS5_PROXY.get("username")
            pwd  = SOCKS5_PROXY.get("password")
            if user and pwd:
                proxy_url = f"socks5://{user}:{pwd}@{SOCKS5_PROXY['host']}:{SOCKS5_PROXY['port']}"
            else:
                proxy_url = f"socks5://{SOCKS5_PROXY['host']}:{SOCKS5_PROXY['port']}"
            proxy = Proxy.from_url(proxy_url)
            sock = await proxy.connect(dest_host=target_host, dest_port=target_port)
            connect_kwargs["sock"] = sock
            print(f"[中继] {client_ws.remote_address} -> {WS_TARGET_URL} (via {proxy_url})")
        else:
            print(f"[中继] {client_ws.remote_address} -> {WS_TARGET_URL} (直连)")

        async with websockets.connect(WS_TARGET_URL, **connect_kwargs) as server_ws:
            async def forward(src, dst, tag):
                try:
                    async for msg in src:
                        await dst.send(msg)
                except Exception as e:
                    print(f"[中继][{tag}] 断开: {e}")

            await asyncio.gather(
                forward(client_ws, server_ws, "C->S"),
                forward(server_ws, client_ws, "S->C"),
            )
    except Exception as e:
        print(f"[中继] 连接失败: {e}")


async def run_relay():
    """启动 WebSocket 中继服务"""
    try:
        import websockets
    except ImportError:
        print("[中继] 错误: 缺少 websockets 库，请运行: pip install websockets python-socks")
        return

    async with websockets.serve(relay_handler, "0.0.0.0", WS_RELAY_PORT, subprotocols=["binary"]):
        await asyncio.Future()  # 永久运行


def start_relay_thread():
    asyncio.run(run_relay())


if __name__ == "__main__":
    ip = get_ip_address()

    # 启动 WebSocket 代理中继线程
    relay_thread = threading.Thread(target=start_relay_thread, daemon=True)
    relay_thread.start()

    print(f"Serving HTTP on 0.0.0.0 port {PORT} ...")
    print(f"Server directory: {DIRECTORY}")
    print("\n" + "="*60)
    print(f"访问地址:")
    print(f"  Local:   http://localhost:{PORT}")
    print(f"  Network: http://{ip}:{PORT}")
    print("="*60)
    if SOCKS5_PROXY:
        print(f"[中继] 本地 WebSocket 中继: ws://localhost:{WS_RELAY_PORT}")
        print(f"       SOCKS5 代理: {SOCKS5_PROXY['host']}:{SOCKS5_PROXY['port']}")
        print(f"       转发至: {WS_TARGET_URL}")
    print("="*60)
    print("\n[使用说明]")
    print("1. 【推荐】本地电脑测试：")
    print(f"   请直接访问: http://localhost:{PORT}")
    print("   无需任何配置，浏览器会直接允许麦克风权限。")
    print("\n2. 【高级】远程访问测试：")
    print(f"   如果您通过 IP (http://{ip}:{PORT}) 访问，浏览器可能因非 HTTPS 禁止麦克风。")
    print("   解决办法: 在 Chrome 地址栏输入 chrome://flags/#unsafely-treat-insecure-origin-as-secure")
    print(f"   填入 http://{ip}:{PORT} 并启用。")
    print("\n3. 【代理】通过 SOCKS5 代理连接：")
    print(f"   在页面中勾选「通过代理中继连接」，中继地址填入 ws://localhost:{WS_RELAY_PORT}")
    print(f"   确保脚本顶部 SOCKS5_PROXY 和 WS_TARGET_URL 已正确配置。")
    print("="*60 + "\n")

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")
