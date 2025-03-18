#!/usr/bin/env python3
import psutil # type: ignore
import time
import smtplib
import logging
import logging.handlers
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys
import os
from typing import Dict, Any, Optional, List
import json
from datetime import datetime

# 添加配置文件路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../config'))
from config import MONITOR_CONFIG

def validate_config() -> None:
    """验证配置文件的完整性"""
    required_fields = ['interval', 'log_file', 'thresholds', 'alert', 'email']
    for field in required_fields:
        if field not in MONITOR_CONFIG:
            raise ValueError(f"配置文件缺少必要字段: {field}")

    # 验证阈值配置
    threshold_fields = ['cpu', 'memory', 'disk']
    for field in threshold_fields:
        if field not in MONITOR_CONFIG['thresholds']:
            raise ValueError(f"阈值配置缺少必要字段: {field}")

    # 验证告警配置
    if 'levels' not in MONITOR_CONFIG['alert']:
        raise ValueError("告警配置缺少 'levels' 字段")
    if 'warning' not in MONITOR_CONFIG['alert']['levels']:
        raise ValueError("告警级别配置缺少 'warning' 字段")
    if 'critical' not in MONITOR_CONFIG['alert']['levels']:
        raise ValueError("告警级别配置缺少 'critical' 字段")

    # 验证邮件配置
    email_fields = ['sender', 'receiver', 'smtp_server', 'smtp_port', 'username', 'password']
    for field in email_fields:
        if field not in MONITOR_CONFIG['email']:
            raise ValueError(f"邮件配置缺少必要字段: {field}")

# 创建日志目录
log_dir = os.path.dirname(os.path.join(os.path.dirname(__file__), MONITOR_CONFIG['log_file']))
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 配置日志
logging.basicConfig(
    handlers=[
        logging.handlers.RotatingFileHandler(
            os.path.join(os.path.dirname(__file__), MONITOR_CONFIG['log_file']),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        ),
        logging.StreamHandler()  # 同时输出到控制台
    ],
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class SystemMonitor:
    def __init__(self):
        self.alert_manager = AlertManager()
        self.metrics_history: List[Dict[str, Any]] = []
        self.max_history_size = 1000  # 保存最近1000条记录

    def get_system_metrics(self) -> Optional[Dict[str, Any]]:
        """获取系统资源使用情况"""
        try:
            # CPU 信息
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()

            # 内存信息
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()

            # 磁盘信息
            disk = psutil.disk_usage('/')

            # 系统负载
            load_avg = psutil.getloadavg()

            # 网络信息
            network = self.get_network_metrics()

            metrics = {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count,
                    'freq_current': cpu_freq.current if cpu_freq else None,
                    'load_avg': load_avg
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'swap_percent': swap.percent
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': disk.percent
                }
            }

            if network:
                metrics['network'] = network

            # 保存历史记录
            self.metrics_history.append(metrics)
            if len(self.metrics_history) > self.max_history_size:
                self.metrics_history.pop(0)

            return metrics
        except Exception as e:
            logging.error(f"获取系统指标时出错: {str(e)}")
            return None

    def get_network_metrics(self) -> Optional[Dict[str, Any]]:
        """获取网络使用情况"""
        try:
            network = psutil.net_io_counters()
            return {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv,
                'packets_sent': network.packets_sent,
                'packets_recv': network.packets_recv,
                'errin': network.errin,
                'errout': network.errout,
                'dropin': network.dropin,
                'dropout': network.dropout
            }
        except Exception as e:
            logging.error(f"获取网络指标时出错: {str(e)}")
            return None

    def check_critical_processes(self) -> Dict[str, bool]:
        """检查关键进程状态"""
        process_status = {}
        try:
            for process_name in MONITOR_CONFIG['critical_processes']:
                process_found = False
                for proc in psutil.process_iter(['pid', 'name']):
                    if proc.info['name'] == process_name:
                        process_found = True
                        break
                process_status[process_name] = process_found
        except Exception as e:
            logging.error(f"检查进程状态时出错: {str(e)}")
        return process_status

    def get_alert_level(self, metrics: Dict[str, Any]) -> Optional[str]:
        """确定告警级别"""
        if not metrics:
            return None

        critical_threshold = MONITOR_CONFIG['alert']['levels']['critical']
        warning_threshold = MONITOR_CONFIG['alert']['levels']['warning']

        # 检查严重级别
        if (metrics['cpu']['percent'] > critical_threshold or
            metrics['memory']['percent'] > critical_threshold or
            metrics['disk']['percent'] > critical_threshold):
            return 'critical'

        # 检查警告级别
        if (metrics['cpu']['percent'] > warning_threshold or
            metrics['memory']['percent'] > warning_threshold or
            metrics['disk']['percent'] > warning_threshold):
            return 'warning'

        return None

    def format_alert_message(self, metrics: Dict[str, Any], level: str) -> str:
        """格式化告警消息"""
        process_status = self.check_critical_processes()

        message = f"""
系统资源告警 (级别: {level.upper()})
时间: {metrics['timestamp']}

CPU:
- 使用率: {metrics['cpu']['percent']}%
- 核心数: {metrics['cpu']['count']}
- 当前频率: {metrics['cpu']['freq_current']} MHz
- 系统负载: {metrics['cpu']['load_avg']}

内存:
- 使用率: {metrics['memory']['percent']}%
- 可用: {metrics['memory']['available'] / (1024*1024*1024):.2f} GB
- 总量: {metrics['memory']['total'] / (1024*1024*1024):.2f} GB
- 交换分区使用率: {metrics['memory']['swap_percent']}%

磁盘:
- 使用率: {metrics['disk']['percent']}%
- 可用: {metrics['disk']['free'] / (1024*1024*1024):.2f} GB
- 总量: {metrics['disk']['total'] / (1024*1024*1024):.2f} GB

关键进程状态:
"""
        for proc, status in process_status.items():
            message += f"- {proc}: {'运行中' if status else '未运行'}\n"

        if 'network' in metrics:
            message += f"""
网络状态:
- 发送: {metrics['network']['bytes_sent'] / (1024*1024):.2f} MB
- 接收: {metrics['network']['bytes_recv'] / (1024*1024):.2f} MB
- 错误 (入/出): {metrics['network']['errin']}/{metrics['network']['errout']}
- 丢包 (入/出): {metrics['network']['dropin']}/{metrics['network']['dropout']}
"""

        return message

    def save_metrics_to_file(self):
        """保存监控数据到文件"""
        try:
            filename = os.path.join(log_dir, f"metrics_{datetime.now().strftime('%Y%m%d')}.json")
            with open(filename, 'w') as f:
                json.dump(self.metrics_history, f, indent=2)
        except Exception as e:
            logging.error(f"保存监控数据时出错: {str(e)}")

    def run(self):
        """运行监控"""
        logging.info("系统监控启动")

        while True:
            try:
                # 获取系统指标
                metrics = self.get_system_metrics()
                if not metrics:
                    continue

                # 检查告警级别
                alert_level = self.get_alert_level(metrics)

                # 记录当前指标
                logging.info(
                    f"系统指标 - CPU: {metrics['cpu']['percent']}%, "
                    f"内存: {metrics['memory']['percent']}%, "
                    f"磁盘: {metrics['disk']['percent']}%"
                )

                # 如果需要告警
                if alert_level and self.alert_manager.should_send_alert(alert_level):
                    message = self.format_alert_message(metrics, alert_level)
                    self.alert_manager.send_alert_email(message, alert_level)

                # 定期保存监控数据
                if len(self.metrics_history) % 100 == 0:  # 每100条记录保存一次
                    self.save_metrics_to_file()

                # 等待下一次检查
                time.sleep(MONITOR_CONFIG['interval'])

            except Exception as e:
                logging.error(f"监控过程出错: {str(e)}")
                time.sleep(60)  # 出错后等待1分钟再继续

class AlertManager:
    def __init__(self):
        self.last_alert_time: Dict[str, float] = {}
        self.alert_interval = MONITOR_CONFIG['alert']['interval']

    def should_send_alert(self, alert_type: str) -> bool:
        """检查是否应该发送告警"""
        current_time = time.time()
        if alert_type not in self.last_alert_time:
            self.last_alert_time[alert_type] = current_time
            return True

        if current_time - self.last_alert_time[alert_type] >= self.alert_interval:
            self.last_alert_time[alert_type] = current_time
            return True
        return False

    def send_alert_email(self, message: str, level: str):
        """发送告警邮件"""
        try:
            subject = f"系统资源告警通知 - {level.upper()}"

            msg = MIMEMultipart()
            msg['From'] = MONITOR_CONFIG['email']['sender']
            msg['To'] = MONITOR_CONFIG['email']['receiver']
            msg['Subject'] = subject
            msg.attach(MIMEText(message, 'plain'))

            server = smtplib.SMTP(
                MONITOR_CONFIG['email']['smtp_server'],
                MONITOR_CONFIG['email']['smtp_port']
            )
            server.starttls()
            server.login(
                MONITOR_CONFIG['email']['username'],
                MONITOR_CONFIG['email']['password']
            )
            server.send_message(msg)
            server.quit()

            logging.info(f"告警邮件发送成功 (级别: {level})")
        except Exception as e:
            logging.error(f"发送告警邮件时出错: {str(e)}")

def setup_signal_handlers(monitor: SystemMonitor):
    """设置信号处理"""
    def signal_handler(signum, frame):
        logging.info("接收到退出信号，正在保存监控数据...")
        monitor.save_metrics_to_file()
        logging.info("监控数据已保存，正在停止监控...")
        sys.exit(0)

    import signal
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

def test_monitor_components():
    """测试监控系统各个组件"""
    try:
        # 测试配置验证
        logging.info("测试配置验证...")
        validate_config()
        logging.info("配置验证通过")

        # 测试系统指标获取
        logging.info("测试系统指标获取...")
        monitor = SystemMonitor()
        metrics = monitor.get_system_metrics()
        if metrics is None:
            raise ValueError("无法获取系统指标")
        logging.info("系统指标获取成功")

        # 测试进程监控
        logging.info("测试进程监控...")
        process_status = monitor.check_critical_processes()
        logging.info(f"关键进程状态: {process_status}")

        # 测试告警级别判断
        logging.info("测试告警级别判断...")
        alert_level = monitor.get_alert_level(metrics)
        logging.info(f"当前告警级别: {alert_level}")

        # 测试告警消息格式化
        logging.info("测试告警消息格式化...")
        if alert_level:
            message = monitor.format_alert_message(metrics, alert_level)
            logging.info("告警消息格式化成功")

        # 测试数据保存
        logging.info("测试数据保存...")
        monitor.save_metrics_to_file()
        logging.info("数据保存测试完成")

        return True
    except Exception as e:
        logging.error(f"测试过程中出错: {str(e)}")
        return False

def main():
    """主函数"""
    try:
        # 验证配置
        validate_config()

        # 运行测试
        if len(sys.argv) > 1 and sys.argv[1] == '--test':
            logging.info("开始测试监控系统组件...")
            if test_monitor_components():
                logging.info("所有测试通过")
                sys.exit(0)
            else:
                logging.error("测试失败")
                sys.exit(1)

        # 创建并运行监控
        monitor = SystemMonitor()
        setup_signal_handlers(monitor)
        monitor.run()
    except Exception as e:
        logging.error(f"监控启动失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
