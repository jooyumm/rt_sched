import time
import threading
import os
import queue
import argparse
import random
from collections import defaultdict

# POSIX 실시간 스케줄러 설정
SCHED_OTHER = 0
SCHED_FIFO = 1
SCHED_RR = 2

# 주기 설정 (ms)
PERIOD_MS_WEATHER = 550
PERIOD_MS_STOCK = 400
PERIOD_MS_NEWS = 500

# 데드라인 설정 (ms)
DEADLINE_MS_WEATHER = 550
DEADLINE_MS_STOCK = 400
DEADLINE_MS_NEWS = 500

# WCET 설정 (ms)
WCET_MS_WEATHER = 650
WCET_MS_STOCK = 500
WCET_MS_NEWS = 600

# 우선순위 설정 (낮은 숫자가 높은 우선순위)
PRIORITY_WEATHER = 3
PRIORITY_STOCK = 1
PRIORITY_NEWS = 2

execution_log = []  # 실행 로그 저장
stop_event = threading.Event()
task_queue = queue.PriorityQueue()

# 통계 데이터 저장
task_stats = defaultdict(lambda: {"count": 0, "overrun": 0, "deadline_exceeded": 0})

def set_scheduler(policy):
    try:
        param = os.sched_param(99)  # 최대 우선순위
        os.sched_setscheduler(0, policy, param)
    except PermissionError:
        print("Permission denied")

def log_task(task_id, current_time, overrun, deadline_exceeded):
    execution_log.append((task_id, current_time, overrun, deadline_exceeded))
    task_stats[task_id]["count"] += 1
    if overrun:
        task_stats[task_id]["overrun"] += 1
    if deadline_exceeded:
        task_stats[task_id]["deadline_exceeded"] += 1

def save_execution_log():
    with open('execution_log.txt', 'w') as f:
        for task_id, current_time, overrun, deadline_exceeded in execution_log:
            f.write(f"{task_id},{current_time:.6f},{int(overrun)},{int(deadline_exceeded)}\n")

def check_timing(start_time, deadline_ms, wcet_ms, task_id):
    current_time = time.time()
    elapsed_time_ms = (current_time - start_time) * 1000
    deadline_exceeded = elapsed_time_ms > deadline_ms
    overrun = elapsed_time_ms > wcet_ms
    log_task(task_id, current_time, overrun, deadline_exceeded)
    return elapsed_time_ms, overrun, deadline_exceeded

def task_runner(task_script, period_ms, deadline_ms, wcet_ms, task_id, priority):
    while not stop_event.is_set():
        start_time_task = time.time()
        extra_exec_time = random.uniform(0, 50.0)
        
        # 다른 스크립트를 실행
        os.system(f'python3 {task_script}')

        # Log timing information
        elapsed_time_ms, overrun, deadline_exceeded = check_timing(start_time_task, deadline_ms, wcet_ms, task_id)
        if deadline_exceeded:
            print(f"[Task {task_id}] Deadline exceeded! {elapsed_time_ms - deadline_ms:.3f}ms")
        if overrun:
            print(f"[Task {task_id}] Overrun! {elapsed_time_ms - wcet_ms:.3f}ms")
        
        # Sleep to simulate task period
        time.sleep(extra_exec_time / 1000.0)
        time.sleep(period_ms / 1000.0)
        
        # Put task in the queue (for priority handling)
        task_queue.put((priority, f"Task {task_id}"))

def start_task_threads():
    t1 = threading.Thread(target=task_runner, args=('weather.py', PERIOD_MS_WEATHER, DEADLINE_MS_WEATHER, WCET_MS_WEATHER, 1, PRIORITY_WEATHER))
    t2 = threading.Thread(target=task_runner, args=('stock.py', PERIOD_MS_STOCK, DEADLINE_MS_STOCK, WCET_MS_STOCK, 2, PRIORITY_STOCK))
    t3 = threading.Thread(target=task_runner, args=('news.py', PERIOD_MS_NEWS, DEADLINE_MS_NEWS, WCET_MS_NEWS, 3, PRIORITY_NEWS))

    # Start all threads
    t1.start()
    t2.start()
    t3.start()

    return t1, t2, t3

if __name__ == "__main__":
    # Argument parsing for scheduling policy
    parser = argparse.ArgumentParser(description="Set scheduler policy")
    parser.add_argument("--RR", action="store_true", help="Use SCHED_RR scheduler")
    parser.add_argument("--FIFO", action="store_true", help="Use SCHED_FIFO scheduler")
    parser.add_argument("--OTHER", action="store_true", help="Use SCHED_OTHER scheduler")
    args = parser.parse_args()

    # Select scheduler based on arguments
    if args.RR:
        selected_scheduler = SCHED_RR
    elif args.FIFO:
        selected_scheduler = SCHED_FIFO
    else:
        selected_scheduler = SCHED_OTHER  # default

    # Set scheduler policy
    set_scheduler(selected_scheduler)

    # Start task execution
    start_time = time.time()
    t1, t2, t3 = start_task_threads()

    # Monitor execution for 10 seconds
    while time.time() - start_time < 10:
        try:
            _, task = task_queue.get(timeout=1)
        except queue.Empty:
            pass

    # Stop tasks and save results
    print("\nStopping tasks and saving results...")
    stop_event.set()
    t1.join()
    t2.join()
    t3.join()

    save_execution_log()
    
    # Print summary statistics
    print("\nExecution Summary:")
    for task_id, stats in sorted(task_stats.items()):
        print(f"Task {task_id}: Executed {stats['count']} times, Overrun {stats['overrun']} times, Deadline Missed {stats['deadline_exceeded']} times")
    
    os.system("python3 result.py")
