import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

# 로그 파일에서 데이터 읽기
tasks_times = {1: [], 2: [], 3: []}

# WCET 초과 및 오버런 횟수 카운트
overrun_count = {1: 0, 2: 0, 3: 0}
deadline_exceeded_count = {1: 0, 2: 0, 3: 0}

# 데이터 읽기
with open("execution_log.txt", "r") as f:
    for line in f:
        parts = line.strip().split(",")
        task_id = int(parts[0])
        current_time_sec = float(parts[1])  # 초 단위 시간
        overrun = int(parts[2]) == 1  # 오버런 여부
        deadline_exceeded = int(parts[3]) == 1  # 데드라인 초과 여부

        # 태스크별 실행 시간 저장
        tasks_times[task_id].append((current_time_sec, overrun, deadline_exceeded))

        if overrun:
            overrun_count[task_id] += 1
        if deadline_exceeded:
            deadline_exceeded_count[task_id] += 1

# 최소, 최대 시간 계산
all_times = [t[0] for task_list in tasks_times.values() for t in task_list]
min_time = min(all_times) if all_times else 0
max_time = max(all_times) if all_times else 1

# 그래프 생성
plt.figure(figsize=(12, 6))

# 마커 및 색상 정의
shapes = {
    "normal": "|",  # 정상 실행은 세로 직선
    "deadline_exceeded": "o",  # 데드라인 초과는 원
    "overrun": "s",  # 오버런은 사각형
}
colors = {
    "normal": 'b',  # 정상 실행 시 파란색
    "deadline_exceeded": 'black',  # 데드라인 초과는 검은색
    "overrun": 'r',  # 오버런은 빨간색
}

# 각 태스크에 대한 마커 그리기
for task_id, task_times in tasks_times.items():
    for start_time, overrun, deadline_exceeded in task_times:
        if overrun:
            shape = shapes["overrun"]
            color = colors["overrun"]
        elif deadline_exceeded:
            shape = shapes["deadline_exceeded"]
            color = colors["deadline_exceeded"]
        else:
            shape = shapes["normal"]
            color = colors["normal"]

        # 태스크의 시작 시간에 마커 표시
        plt.scatter(start_time, f"Task {task_id}", color=color, marker=shape, s=100)

# x축 레이블
plt.xlabel('Time(s)')
plt.ylabel('Tasks')
plt.title('Task execution')

# x축 범위 설정
plt.xlim(min_time - 0.1, max_time + 0.1)

# 범례 정의
marker_legend = [
    Line2D([0], [0], marker="|", color='b', lw=0, markersize=15, label="Normal"),
    Line2D([0], [0], marker="o", color='black', lw=0, markersize=7, label="Deadline Exceeded"),
    Line2D([0], [0], marker="s", color='r', lw=0, markersize=7, label="Overrun"),
]

# 텍스트만 있는 Task 범례 정의
task_legend = [
    Line2D([0], [0], color='none', lw=0, label=f"Task 1 (Overrun: {overrun_count[1]}, Deadline Exceeded: {deadline_exceeded_count[1]})"),
    Line2D([0], [0], color='none', lw=0, label=f"Task 2 (Overrun: {overrun_count[2]}, Deadline Exceeded: {deadline_exceeded_count[2]})"),
    Line2D([0], [0], color='none', lw=0, label=f"Task 3 (Overrun: {overrun_count[3]}, Deadline Exceeded: {deadline_exceeded_count[3]})"),
]

# 두 가지 범례를 하나의 박스에 결합
handles = marker_legend + task_legend
labels = [line.get_label() for line in handles]

# 범례 표시
plt.legend(handles=handles, labels=labels, loc='upper center', bbox_to_anchor=(0.5, -0.25), ncol=2)

# 그래프 레이아웃
plt.tight_layout()

# PNG 파일로 저장
plt.savefig("task_execution.png")
plt.show()