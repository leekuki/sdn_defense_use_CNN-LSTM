import psutil
import time
import csv
import sys

def get_ryu_process():
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['cmdline'] and 'ryu-manager' in ' '.join(proc.info['cmdline']):
                return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return None

ryu_proc = get_ryu_process()

if not ryu_proc:
    print(" 未找到 ryu-manager 进程！请先启动 Ryu 控制器。")
    sys.exit(1)

print(f"成功锁定 Ryu 控制器进程 (PID: {ryu_proc.pid})")
ryu_proc.cpu_percent(interval=None)

log_filename = "ryu_overhead_log.csv"
print(f"开始监控 CPU 和内存开销，数据将保存至 {log_filename} (按 Ctrl+C 停止)")

with open(log_filename, mode='w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["Time_sec", "CPU_Percent", "Memory_MB"])
    
    time_sec = 0
    try:
        while True:
            time.sleep(1)
            cpu_usage = ryu_proc.cpu_percent(interval=None)
            mem_info = ryu_proc.memory_info()
            mem_mb = mem_info.rss / (1024 * 1024)
            
            writer.writerow([time_sec, round(cpu_usage, 2), round(mem_mb, 2)])
            print(f"[{time_sec:02d}s] Ryu CPU: {cpu_usage:5.1f}% | 内存: {mem_mb:6.2f} MB")
            
            time_sec += 1
    except KeyboardInterrupt:
        print(f"\n监控已手动停止！数据已保存至 {log_filename}")
