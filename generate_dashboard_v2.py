import json

# 定義 Grafana Dashboard 結構
dashboard = {
    "annotations": {"list": [{"builtIn": 1, "datasource": "-- Grafana --", "enable": True, "hide": True, "iconColor": "rgba(0, 211, 255, 1)", "name": "Annotations & Alerts", "type": "dashboard"}]},
    "editable": True,
    "gnetId": None,
    "graphTooltip": 0,
    "id": None,
    "links": [],
    "panels": [],
    "schemaVersion": 30,
    "style": "dark",
    "tags": ["AI-Burn-In", "Hardware-Monitor", "v2-updated"],
    "templating": {
        "list": [
            {
                "current": {"text": "No data", "value": "No data"},
                "hide": 0, "includeAll": False, "label": "Instance (Host)", "multi": False, "name": "instance",
                "query": "label_values(node_uname_info, instance)", "refresh": 1, "type": "query"
            },
            {
                 "current": {"text": "No data", "value": "No data"},
                 "hide": 0, "label": "GPU ID", "name": "gpu",
                 "query": "label_values(DCGM_FI_DEV_GPU_TEMP, gpu)", "refresh": 1, "type": "query"
            }
        ]
    },
    "time": {"from": "now-1h", "to": "now"},
    "refresh": "1s",
    "title": "AI Hardware Burn-in Monitor (Full Stack)",
    "uid": "ai_burn_in_v2",
    "version": 4
}

def create_panel(id, title, description, targets, y_axis_unit, gridPos):
    return {
        "id": id, "gridPos": gridPos, "type": "timeseries", "title": title, "description": description, "targets": targets,
        "fieldConfig": {
            "defaults": {
                "custom": {"drawStyle": "line", "lineInterpolation": "smooth", "lineWidth": 2, "fillOpacity": 10},
                "unit": y_axis_unit
            },
            "overrides": []
        },
        "datasource": "Prometheus"
    }

# --- CPU & RAM SECTION ---
dashboard["panels"].append({"id": 10, "gridPos": {"h": 1, "w": 24, "x": 0, "y": 0}, "type": "row", "title": "CPU & Memory Performance", "collapsed": False})

dashboard["panels"].append(create_panel(11, "CPU Usage (%)", "Total CPU utilization", [{"expr": "100 - (avg by (instance) (rate(node_cpu_seconds_total{mode='idle', instance=~'$instance'}[1m])) * 100)", "legendFormat": "Usage", "refId": "A"}], "percent", {"h": 8, "w": 8, "x": 0, "y": 1}))
dashboard["panels"].append(create_panel(12, "CPU Temperature", "CPU Die Temp", [{"expr": "node_hwmon_temp_celsius{instance=~'$instance', chip=~'coretemp.*|cpu.*'}", "legendFormat": "{{sensor}}", "refId": "A"}], "celsius", {"h": 8, "w": 8, "x": 8, "y": 1}))
dashboard["panels"].append(create_panel(13, "System Load", "Queue Depth (Load1)", [{"expr": "node_load1{instance=~'$instance'}", "legendFormat": "Load 1m", "refId": "A"}], "short", {"h": 8, "w": 8, "x": 16, "y": 1}))

dashboard["panels"].append(create_panel(14, "RAM Usage (%)", "Memory usage", [{"expr": "100 * (1 - (node_memory_MemAvailable_bytes{instance=~'$instance'} / node_memory_MemTotal_bytes{instance=~'$instance'}))", "legendFormat": "RAM Used", "refId": "A"}], "percent", {"h": 8, "w": 12, "x": 0, "y": 9}))
dashboard["panels"].append(create_panel(15, "Page Faults", "Major page faults (Swapping indicator)", [{"expr": "rate(node_vmstat_pgmajfault{instance=~'$instance'}[1m])", "legendFormat": "Faults/sec", "refId": "A"}], "short", {"h": 8, "w": 12, "x": 12, "y": 9}))

# --- GPU SECTION ---
dashboard["panels"].append({"id": 20, "gridPos": {"h": 1, "w": 24, "x": 0, "y": 17}, "type": "row", "title": "GPU AI Performance (DCGM)", "collapsed": False})

dashboard["panels"].append(create_panel(21, "GPU & Tensor Util (%)", "Compute Activity", [
    {"expr": "avg by (gpu) (DCGM_FI_DEV_GPU_UTIL{gpu=~'$gpu'})", "legendFormat": "GPU {{gpu}} Util", "refId": "A"},
    {"expr": "avg by (gpu) (DCGM_FI_PROF_PIPE_TENSOR_ACTIVE{gpu=~'$gpu'})", "legendFormat": "GPU {{gpu}} Tensor", "refId": "B"}
], "percent", {"h": 9, "w": 8, "x": 0, "y": 18}))

dashboard["panels"].append(create_panel(22, "GPU VRAM Usage (MB)", "Framebuffer used", [{"expr": "DCGM_FI_DEV_FB_USED{gpu=~'$gpu'}", "legendFormat": "GPU {{gpu}} VRAM", "refId": "A"}], "mbytes", {"h": 9, "w": 8, "x": 8, "y": 18}))
dashboard["panels"].append(create_panel(23, "GPU Power Usage", "Instant Power (W)", [{"expr": "DCGM_FI_DEV_POWER_USAGE{gpu=~'$gpu'}", "legendFormat": "GPU {{gpu}} Power", "refId": "A"}], "watt", {"h": 9, "w": 8, "x": 16, "y": 18}))
dashboard["panels"].append(create_panel(24, "GPU Temperature", "Thermal status", [{"expr": "DCGM_FI_DEV_GPU_TEMP{gpu=~'$gpu'}", "legendFormat": "GPU {{gpu}} Temp", "refId": "A"}], "celsius", {"h": 9, "w": 24, "x": 0, "y": 27}))

# --- SSD SECTION ---
dashboard["panels"].append({"id": 30, "gridPos": {"h": 1, "w": 24, "x": 0, "y": 36}, "type": "row", "title": "SSD / Storage I/O (NVMe)", "collapsed": False})

dashboard["panels"].append(create_panel(31, "NVMe IOPS", "R/W Operations per sec", [
    {"expr": "rate(node_disk_reads_completed_total{instance=~'$instance', device=~'nvme.*'}[1m])", "legendFormat": "{{device}} Read IOPS", "refId": "A"},
    {"expr": "rate(node_disk_writes_completed_total{instance=~'$instance', device=~'nvme.*'}[1m])", "legendFormat": "{{device}} Write IOPS", "refId": "B"}
], "iops", {"h": 8, "w": 8, "x": 0, "y": 37}))

dashboard["panels"].append(create_panel(32, "NVMe Throughput", "MB/s", [
    {"expr": "rate(node_disk_read_bytes_total{instance=~'$instance', device=~'nvme.*'}[1m])", "legendFormat": "{{device}} Read", "refId": "A"},
    {"expr": "rate(node_disk_written_bytes_total{instance=~'$instance', device=~'nvme.*'}[1m])", "legendFormat": "{{device}} Write", "refId": "B"}
], "bytes", {"h": 8, "w": 8, "x": 8, "y": 37}))

dashboard["panels"].append(create_panel(33, "NVMe Latency", "I/O Wait Time", [{"expr": "rate(node_disk_io_time_seconds_total{instance=~'$instance', device=~'nvme.*'}[1m])", "legendFormat": "{{device}} Latency", "refId": "A"}], "s", {"h": 8, "w": 8, "x": 16, "y": 37}))
dashboard["panels"].append(create_panel(34, "NVMe Temperatures", "Disk Thermal", [{"expr": "node_hwmon_temp_celsius{instance=~'$instance', chip=~'nvme.*'}", "legendFormat": "{{chip}} {{sensor}}", "refId": "A"}], "celsius", {"h": 8, "w": 24, "x": 0, "y": 45}))

# Save
filename = "ai_burn_in_dashboard_v2.json"
with open(filename, "w", encoding='utf-8') as f:
    json.dump(dashboard, f, indent=2, ensure_ascii=False)
print(f"Updated Dashboard saved to {filename}")
