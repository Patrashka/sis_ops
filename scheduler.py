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
    proc_copy.sort(key=lambda x: x['arrival'])
    time = 0
    completed = []
    ready = []
    index = 0

    while ready or index < len(proc_copy):
        if not ready and index < len(proc_copy) and proc_copy[index]['arrival'] > time:
            time = proc_copy[index]['arrival']
        while index < len(proc_copy) and proc_copy[index]['arrival'] <= time:
            ready.append(proc_copy[index])
            index += 1
        if ready:
            current = ready.pop(0)
            if 'start' not in current:
                current['start'] = time
            run_time = min(quantum, current['remaining'])
            time += run_time
            current['remaining'] -= run_time
            while index < len(proc_copy) and proc_copy[index]['arrival'] <= time:
                ready.append(proc_copy[index])
                index += 1
            if current['remaining'] > 0:
                ready.append(current)
            else:
                current['end'] = time
                current['turnaround'] = current['end'] - current['arrival']
                current['waiting'] = current['turnaround'] - current['burst']
                completed.append(current)
    return completed
