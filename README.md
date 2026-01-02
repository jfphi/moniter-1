# AI Hardware Burn-in Monitor (Full Stack)

一套基於 Docker Compose 的自動化監控方案，專為 AI 訓練與燒機測試設計。整合了 CPU、RAM、GPU (NVIDIA) 以及 SSD 的關鍵指標監控。

## 🚀 快速啟動

### 前置準備
- 已安裝 **Docker** & **Docker Compose**。
- 已安裝 **NVIDIA Drivers**。
- 已安裝 **NVIDIA Container Toolkit**。

### 啟動監控堆疊
```bash
docker compose up -d
```

### 訪問服務
- **Grafana**: [http://localhost:3000](http://localhost:3000) (預設帳密: `admin` / `admin`)
- **Prometheus**: [http://localhost:9090](http://localhost:9090)

## 📊 監控指標對照表

| 硬體目標 | 監控指標 | 資料來源 | 關鍵技術指標名稱 (PromQL) | 備註 |
| :--- | :--- | :--- | :--- | :--- |
| **CPU** | 使用率 | Node Exporter | `node_cpu_seconds_total` | 需過濾 mode="idle" |
| | 溫度 | Node Exporter | `node_hwmon_temp_celsius` | 需主機板驅動支援 |
| | 系統負載 | Node Exporter | `node_load1` | 觀察排程佇列長度 |
| **RAM** | 使用率 | Node Exporter | `node_memory_MemTotal_bytes` | (Total - Available) / Total |
| | 分頁錯誤 | Node Exporter | `node_vmstat_pgmajfault` | 數值高代表發生 Disk Swap |
| **GPU** | 整體使用率 | DCGM Exporter | `DCGM_FI_DEV_GPU_UTIL` | 包含 CUDA 計算 |
| | Tensor Core | DCGM Exporter | `DCGM_FI_PROF_PIPE_TENSOR_ACTIVE` | AI 算力活躍度指標 |
| | 顯存使用量 | DCGM Exporter | `DCGM_FI_DEV_FB_USED` | 監控 OOM (Out of Memory) |
| | 即時功耗 | DCGM Exporter | `DCGM_FI_DEV_POWER_USAGE` | 單位：瓦特 (W) |
| | GPU 溫度 | DCGM Exporter | `DCGM_FI_DEV_GPU_TEMP` | 監控熱降頻 (Throttling) |
| **SSD** | IOPS | Node Exporter | `node_disk_reads_completed_total` | 每秒讀寫次數 |
| | 吞吐量 | Node Exporter | `node_disk_read_bytes_total` | 監控 MB/s |
| | I/O 延遲 | Node Exporter | `node_disk_io_time_seconds_total` | 觀察 SSD 是否過熱變慢 |
| | 硬碟溫度 | Node Exporter | `node_hwmon_temp_celsius` | 過濾 `chip=~"nvme.*"` |

## 🛠️ 開發與同步 (PR 流程)

1. **更新儀表板**：
   修改 `generate_dashboard_v2.py` 後執行：
   ```bash
   uv run generate_dashboard_v2.py
   cp ai_burn_in_dashboard_v2.json grafana/dashboards/dashboards.json
   ```

2. **推送與 PR**：
   ```bash
   git add .
   git commit -m "update: sync monitoring metrics and split gpu panels"
   git push origin main
   ```
   推送後請至 GitHub [jfphi/moniter-1](https://github.com/jfphi/moniter-1) 發起 Pull Request 給 `phisonaistar/moniter`。

## 📋 疑難排解
- **GPU 數據顯示 No Data**：
  - 檢查環境是否安裝 NVIDIA Container Toolkit。
  - 執行 `docker exec -it dcgm-exporter dcgmi group -l` 檢查 GPU 狀態。
- **溫度消失**：
  - 部分硬體需安裝 `lm-sensors` 並執行 `sudo sensors-detect` 才能由 Node Exporter 抓取。
