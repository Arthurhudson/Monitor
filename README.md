# 系统资源监控工具

这是一个用 Python 编写的系统资源监控工具，可以监控 CPU、内存、磁盘使用率等系统指标，并在超过阈值时发送告警邮件。

## 功能特点

- 监控系统关键指标：
  - CPU 使用率、核心数、频率和系统负载
  - 内存使用率和交换分区状态
  - 磁盘使用率和可用空间
  - 网络流量统计（发送/接收字节数、错误数、丢包数）
- 监控关键进程运行状态
- 支持多级别告警（警告和严重）
- 告警频率控制，避免告警轰炸
- 监控数据 JSON 格式持久化存储
- 日志自动轮转（最大 10MB，保留 5 个备份）
- 优雅退出并保存数据
- 类型注解支持

## 安装要求

- Python 3.6+
- psutil >= 5.9.0
- typing-extensions >= 4.5.0

## 安装步骤

1. 克隆代码库：
```bash
git clone https://github.com/Arthurhudson/Monitor.git
cd Monitor
```

2. 安装依赖：
```bash
pip3 install -r requirements.txt
```

3. 配置监控参数：
   - 复制配置模板：`cp config/config.py.template config/config.py`
   - 修改 `config.py` 中的配置参数

## 配置说明

配置文件位于 `config/config.py`，主要配置项包括：

```python
MONITOR_CONFIG = {
    'interval': 300,  # 监控间隔（秒）
    'log_file': '../logs/monitor.log',  # 日志文件路径

    # 资源使用阈值（百分比）
    'thresholds': {
        'cpu': 80,
        'memory': 80,
        'disk': 85,
        'network': {
            'bytes_sent': 1000000,  # 1MB/s
            'bytes_recv': 1000000   # 1MB/s
        }
    },

    # 需要监控的关键进程
    'critical_processes': [
        'nginx',
        'mysql',
        'redis-server'
    ],

    # 告警配置
    'alert': {
        'interval': 3600,  # 相同告警的最小间隔（秒）
        'levels': {
            'warning': 80,  # 警告阈值
            'critical': 90  # 严重阈值
        }
    },

    # 邮件配置
    'email': {
        'sender': 'your-email@example.com',
        'receiver': 'admin@example.com',
        'smtp_server': 'smtp.example.com',
        'smtp_port': 587,
        'username': 'your-username',
        'password': 'your-password'
    }
}
```

## 运行方法

1. 直接运行：
```bash
python3 src/monitor.py
```

2. 后台运行：
```bash
nohup python3 src/monitor.py > /dev/null 2>&1 &
```

## 日志和数据文件

- 监控日志：`logs/monitor.log`
  - 自动轮转，单个文件最大 10MB
  - 保留最近 5 个备份文件
- 监控数据：`logs/metrics_YYYYMMDD.json`
  - 每天生成新文件
  - JSON 格式存储
  - 保存最近 1000 条记录

## 告警说明

系统支持两个告警级别：
- 警告（Warning）：资源使用率超过配置的警告阈值（默认 80%）
- 严重（Critical）：资源使用率超过配置的严重阈值（默认 90%）

告警信息包含：
- 告警级别和时间戳
- CPU 信息（使用率、核心数、频率、系统负载）
- 内存信息（总量、可用量、使用率、交换分区状态）
- 磁盘信息（总量、已用、可用、使用率）
- 网络状态（发送/接收流量、错误数、丢包数）
- 关键进程运行状态

## 注意事项

1. 确保配置文件中的邮件服务器信息正确
2. 建议将监控间隔设置在 5 分钟以上
3. 需要适当的系统权限来获取进程信息
4. 确保日志目录具有写入权限
5. 配置文件必须包含所有必需字段

## 贡献指南

欢迎提交 Issue 和 Pull Request 来改进这个工具。在提交代码时请：

1. 确保代码包含适当的类型注解
2. 通过所有测试用例
3. 更新相关文档

## 许可证

MIT License
