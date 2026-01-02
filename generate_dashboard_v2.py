import json

# 定義 Grafana Dashboard 結構
dashboard = {
    "annotations": {
        "list": [
            {
                "builtIn": 1,
                "datasource": "-- Grafana --",
                "enable": True,
                "hide": True,
                "iconColor": "rgba(0, 211, 255, 1)",
                "name": "Annotations & Alerts",
                "type": "dashboard"
            }
        ]
    },
    "editable": True,
    "gnetId": None,
    "graphTooltip": 0,
    "id": None,
    "links": [],
    "panels": [],
    "schemaVersion": 30,
    "style": "dark",
    "tags": ["AI-Burn-In", "Hardware-Monitor", "v2"],
    "templating": {
        "list": [
            {
                "current": {"text": "No data", "value": "No data"},
                "hide": 0,
                "includeAll": False,
                "label": "Instance (Host)",
                "multi": False,
                "name": "instance",
                "options": [],
                "query": "label_values(node_uname_info, instance)",
                "refresh": 1,
                "regex": "",
                "skipUrlSync": False,
                "sort": 1,
                "type": "query"
            },
            {
                 "current": {"text": "No data", "value": "No data"},
                 "hide": 0,
                 "label": "GPU ID",
                 "name": "gpu",
                 "options": [],
                 "query": "label_values(DCGM_FI_DEV_GPU_TEMP, gpu)",
                 "refresh": 1,
                 "type": "query"
            }
        ]
    },
    "time": {
        "from": "now-1h",
        "to": "now"
    },
    "title": "AI Hardware Burn-in Monitor (Full Stack)",
    "uid": "ai_burn_in_v2",
    "version": 2
}

# 輔助函數：建立標準圖表 Panel
def create_panel(id, title, description, targets, y_axis_unit, gridPos):
    return {
        "id": id,
        "gridPos": gridPos,
        "type": "timeseries",
        "title": title,
        "description": description,
        "targets": targets,
        "fieldConfig": {
            "defaults": {
                "custom": {
                    "drawStyle": "line",
                    "lineInterpolation": "smooth",
                    "lineWidth": 2,
                    "fillOpacity": 10,
                    "gradientMode": "opacity"
                },
                "unit": y_axis_unit
            },
            "overrides": []
        },
        "datasource": "Prometheus"
    }

# --- 1. CPU & RAM Section (Row 0) ---
dashboard["panels"].append({
    "id": 10,
    "gridPos": {"h": 1, "w": 24, "x": 0, "y": 0},
    "type": "row",
    "title": "CPU & Memory Performance",
    "collapsed": False
})

# CPU Usage
dashboard["panels"].append(create_panel(
    id=11,
    title="CPU Usage Total (%)",
    description="Total CPU utilization",
    targets=[{
        "expr": "100 - (avg by (instance) (rate(node_cpu_seconds_total{mode='idle', instance=~'$instance'}[1m])) * 100)",
        "legendFormat": "CPU Usage",
        "refId": "A"
    }],
    y_axis_unit="percent",
    gridPos={"h": 8, "w": 8, "x": 0, "y": 1}
))

# RAM Usage (New!)
dashboard["panels"].append(create_panel(
    id=12,
    title="RAM Usage (%)",
    description="Memory usage",
    targets=[{
        "expr": "100 * (1 - (node_memory_MemAvailable_bytes{instance=~'$instance'} / node_memory_MemTotal_bytes{instance=~'$instance'}))",
        "legendFormat": "RAM Used",
        "refId": "A"
    }],
    y_axis_unit="percent",
    gridPos={"h": 8, "w": 8, "x": 8, "y": 1}
))

# Page Faults (New!)
dashboard["panels"].append(create_panel(
    id=13,
    title="Page Faults (Major)",
    description="Major page faults imply disk swapping (Bad for performance)",
    targets=[{
        "expr": "rate(node_vmstat_pgmajfault{instance=~'$instance'}[1m])",
        "legendFormat": "Major Faults/sec",
        "refId": "A"
    }],
    y_axis_unit="short",
    gridPos={"h": 8, "w": 8, "x": 16, "y": 1}
))


# --- 2. GPU Section (Row 10) ---
dashboard["panels"].append({
    "id": 20,
    "gridPos": {"h": 1, "w": 24, "x": 0, "y": 9},
    "type": "row",
    "title": "GPU AI Performance (DCGM)",
    "collapsed": False
})

# GPU Utilization
dashboard["panels"].append(create_panel(
    id=21,
    title="GPU & Tensor Core Util",
    description="Utilization",
    targets=[
        { "expr": "avg by (gpu) (DCGM_FI_DEV_GPU_UTIL{instance=~'$instance', gpu=~'$gpu'})", "legendFormat": "GPU {{gpu}} Util", "refId": "A" },
        { "expr": "avg by (gpu) (DCGM_FI_PROF_PIPE_TENSOR_ACTIVE{instance=~'$instance', gpu=~'$gpu'})", "legendFormat": "GPU {{gpu}} Tensor", "refId": "B" }
    ],
    y_axis_unit="percent",
    gridPos={"h": 9, "w": 8, "x": 0, "y": 10}
))

# GPU Power & Temp
dashboard["panels"].append(create_panel(
    id=22,
    title="GPU Power & Temp",
    description="Power & Thermal",
    targets=[
        { "expr": "DCGM_FI_DEV_POWER_USAGE{instance=~'$instance', gpu=~'$gpu'}", "legendFormat": "GPU {{gpu}} Power (W)", "refId": "A" },
        { "expr": "DCGM_FI_DEV_GPU_TEMP{instance=~'$instance', gpu=~'$gpu'}", "legendFormat": "GPU {{gpu}} Temp (C)", "refId": "B" }
    ],
    y_axis_unit="watt",
    gridPos={"h": 9, "w": 8, "x": 8, "y": 10}
))

# GPU Fan Speed (New!)
dashboard["panels"].append(create_panel(
    id=23,
    title="GPU Fan Speed",
    description="Cooling fan speed percentage",
    targets=[
        { "expr": "DCGM_FI_DEV_FAN_SPEED{instance=~'$instance', gpu=~'$gpu'}", "legendFormat": "GPU {{gpu}} Fan", "refId": "A" }
    ],
    y_axis_unit="percent",
    gridPos={"h": 9, "w": 8, "x": 16, "y": 10}
))


# --- 3. SSD Section (Row 20) ---
dashboard["panels"].append({
    "id": 30,
    "gridPos": {"h": 1, "w": 24, "x": 0, "y": 19},
    "type": "row",
    "title": "SSD / Storage I/O",
    "collapsed": False
})

# Disk Throughput
dashboard["panels"].append(create_panel(
    id=31,
    title="Disk Throughput (MB/s)",
    description="R/W Speed",
    targets=[
        { "expr": "rate(node_disk_read_bytes_total{instance=~'$instance'}[1m])", "legendFormat": "{{device}} Read", "refId": "A" },
        { "expr": "rate(node_disk_written_bytes_total{instance=~'$instance'}[1m])", "legendFormat": "{{device}} Write", "refId": "B" }
    ],
    y_axis_unit="bytes",
    gridPos={"h": 8, "w": 12, "x": 0, "y": 20}
))

# Disk Temp (Generic)
dashboard["panels"].append(create_panel(
    id=32,
    title="Hardware Temperatures (SSD/Chipset)",
    description="All sensors reported by hwmon (Look for nvme/drive)",
    targets=[
        { "expr": "node_hwmon_temp_celsius{instance=~'$instance'}", "legendFormat": "{{chip}} {{sensor}}", "refId": "A" }
    ],
    y_axis_unit="celsius",
    gridPos={"h": 8, "w": 12, "x": 12, "y": 20}
))

# Save
filename = "ai_burn_in_dashboard_v2.json"
with open(filename, "w", encoding='utf-8') as f:
    json.dump(dashboard, f, indent=2, ensure_ascii=False)

print(f"Updated Dashboard saved to {filename}")
