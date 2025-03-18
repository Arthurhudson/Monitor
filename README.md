# 系统资源监控工具

这是一个用Python编写的系统资源监控工具，可以监控CPU、内存、磁盘使用率等系统指标，并在超过阈值时发送告警邮件。

## 功能特点

- 监控系统关键指标：
  - CPU使用率、核心数和频率
  - 内存使用率和交换分区状态
  - 磁盘使用率
  - 网络流量和错误统计
- 监控关键进程运行状态
- 支持多级别告警（警告和严重）
- 告警频率控制，避免告警轰炸
- 监控数据历史记录和持久化
- 日志自动轮转
- 优雅退出并保存数据

## 安装要求

- Python 3.6+
- psutil库

## 安装步骤

1. 克隆代码库：
```bash
git clone <repository_url>
cd Monitor
```

2. 安装依赖：
```bash
pip install -r requirements.txt
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
        'sender': 'monitor@example.com',
        'receiver': 'admin@example.com',
        'smtp_server': 'smtp.example.com',
        'smtp_port': 587,
        'username': 'your_username',
        'password': 'your_password'
    }
}
```

## 运行方法

1. 直接运行：
```bash
python src/monitor.py
```

2. 后台运行：
```bash
nohup python src/monitor.py > /dev/null 2>&1 &
```

## 日志和数据文件

- 日志文件：`logs/monitor.log`
- 监控数据：`logs/metrics_YYYYMMDD.json`

## 告警说明

系统支持两个告警级别：
- 警告（Warning）：资源使用率超过80%
- 严重（Critical）：资源使用率超过90%

告警信息包含：
- 当前CPU、内存、磁盘使用情况
- 系统负载
- 关键进程运行状态
- 网络状态

## 注意事项

1. 确保配置文件中的邮件服务器信息正确
2. 建议将监控间隔设置在5分钟以上
3. 需要适当的系统权限来获取进程信息
4. 建议定期检查日志文件大小

## 贡献指南

欢迎提交Issue和Pull Request来改进这个工具。

## 许可证

MIT License
