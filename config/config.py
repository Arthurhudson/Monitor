"""
系统监控配置文件
"""

MONITOR_CONFIG = {
    # 监控间隔（秒）
    'interval': 300,  # 5分钟

    # 日志文件路径
    'log_file': '../logs/monitor.log',

    # 资源使用阈值（百分比）
    'thresholds': {
        'cpu': 90,     # CPU 使用率阈值调高
        'memory': 85,  # 内存使用率阈值调整
        'disk': 90,    # 磁盘使用率阈值调高
        'network': {
            'bytes_sent': 5000000,  # 5MB/s
            'bytes_recv': 5000000   # 5MB/s
        }
    },

    # 关键进程列表 - 根据实际需要修改
    'critical_processes': [
        'python3',     # 确保至少有一个正在运行的进程
        'sshd',        # SSH 服务器进程
        'postfix'      # 邮件服务器进程
    ],

    # 告警配置
    'alert': {
        'interval': 3600,  # 相同告警的最小间隔（秒）
        'levels': {
            'warning': 85,  # 警告阈值
            'critical': 95  # 严重阈值
        }
    },

    # 邮件配置
    'email': {
        'sender': 'System Monitor <monitor@monitor.localhost>',  # 更友好的发件人名称
        'receiver': 'hateli@163.com',  # 接收告警的 Gmail 地址
        'smtp_server': 'localhost',
        'smtp_port': 25,            # 本地 Postfix 使用默认的 25 端口
        'username': '',             # 本地服务器不需要认证
        'password': ''              # 本地服务器不需要密码
    }
}
