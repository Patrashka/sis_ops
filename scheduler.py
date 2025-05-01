from typing import List, Dict
import copy

def fcfs(processes: List[Dict]) -> List[Dict]:
    sorted_proc = sorted(processes, key=lambda x: x['arrival'])
    current_time = 0
    for p in sorted_proc:
        p['start'] = max(current_time, p['arrival'])
        p['end'] = p['start'] + p['burst']
        p['turnaround'] = p['end'] - p['arrival']
        p['waiting'] = p['start'] - p['arrival']
        current_time = p['end']
    return sorted_proc

def sjf(processes: List[Dict]) -> List[Dict]:
    proc_copy = copy.deepcopy(processes)
    current_time = 0
    result = []
    while proc_copy:
        available = [p for p in proc_copy if p['arrival'] <= current_time]
        if not available:
            current_time += 1
            continue
        shortest = min(available, key=lambda x: x['burst'])
        shortest['start'] = current_time
        shortest['end'] = current_time + shortest['burst']
        shortest['turnaround'] = shortest['end'] - shortest['arrival']
        shortest['waiting'] = shortest['start'] - shortest['arrival']
        current_time = shortest['end']
        proc_copy.remove(shortest)
        result.append(shortest)
    return result

def round_robin(processes: List[Dict], quantum: int) -> List[Dict]:
    proc_copy = copy.deepcopy(processes)
    queue = sorted(proc_copy, key=lambda x: x['arrival'])
    time = 0
    completed = []
    ready = []
    last_arrival_idx = 0

    while queue or ready:
        while last_arrival_idx < len(proc_copy) and proc_copy[last_arrival_idx]['arrival'] <= time:
            ready.append(proc_copy[last_arrival_idx])
            last_arrival_idx += 1

        if not ready:
            time += 1
            continue

        current = ready.pop(0)
        run_time = min(quantum, current['remaining'])
        current.setdefault('start', time)
        time += run_time
        current['remaining'] -= run_time

        if current['remaining'] == 0:
            current['end'] = time
            current['turnaround'] = current['end'] - current['arrival']
            current['waiting'] = current['turnaround'] - current['burst']
            completed.append(current)
        else:
            while last_arrival_idx < len(proc_copy) and proc_copy[last_arrival_idx]['arrival'] <= time:
                ready.append(proc_copy[last_arrival_idx])
                last_arrival_idx += 1
            ready.append(current)
    return completed
