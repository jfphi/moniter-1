# AI Hardware Burn-in Monitor (Full Stack)

一套基於 Docker Compose 的自動化監控方案，專為 AI 訓練與燒機測試設計。整合了 CPU、RAM、GPU (NVIDIA) 以及 SSD 的關鍵指標監控。

## 🚀 快速啟動

### 前置準備
- 已安裝 **Docker** & **Docker Compose**。
- 已安裝 **NVIDIA Drivers**。
- 已安裝 **NVIDIA Container Toolkit** (確保 Docker 能存取 GPU)。

### 啟動監控堆疊
在專案根目錄下執行：
```bash
docker-compose up -d
```

### 訪問服務
- **Grafana**: [http://localhost:3000](http://localhost:3000) (預設帳密: `admin` / `admin`)
- **Prometheus**: [http://localhost:9090](http://localhost:9090)

> **注意**: 啟動後 Grafana 已自動匯入資料來源與專屬 Dashboard，您只需登入即可查看。

## 📊 監控指標說明

### 1. CPU & 記憶體
- **CPU Usage**: 總體使用率。
- **RAM Usage**: 實時記憶體佔用。
- **Page Faults**: 監控是否有磁碟置換 (Swap)，頻繁發生會嚴重拖慢 AI 效能。

### 2. GPU (NVIDIA DCGM)
- **GPU & Tensor Core Util**: AI 算力核心活躍度。
- **GPU Power & Temp**: 功耗與溫度，預防熱降頻 (Throttling)。
- **Fan Speed**: 風扇轉速百分比。

### 3. SSD / 儲存
- **Disk Throughput**: 讀寫吞吐量 (MB/s)。
- **Hardware Temperatures**: SSD 與晶片組溫度。

## 🛠️ 專案開發與維護

### 更新儀表板
本專案使用 Python 腳本生成 Grafana Dashboard JSON。若需修改佈局或指標，請修改 `generate_dashboard_v2.py` 後執行：

```bash
# 使用 uv 執行
uv run generate_dashboard_v2.py

# 同步至 Grafana 配置目錄
cp ai_burn_in_dashboard_v2.json grafana/dashboards/dashboards.json

# 重啟 Grafana 使其加載新配置
docker-compose restart grafana
```

### 專案結構
```text
.
├── docker-compose.yml           # 定義 Prometheus, Grafana, Exporters
├── generate_dashboard_v2.py     # Dashboard 生成腳本
├── ai_burn_in_dashboard_v2.json # 儀表板定義檔
├── prometheus/
│   └── prometheus.yml           # Prometheus 採集配置
└── grafana/                     # Grafana 自動配置
    ├── dashboards/              # 存放 JSON 儀表板
    └── provisioning/            # 自動加載資料來源與目錄配置
```

## 📋 疑難排解
- **看不到 GPU 數據**：請確認 `nvidia-smi` 可運作，且執行 `docker run --rm --gpus all ubuntu nvidia-smi` 能看到 GPU 資訊。
- **資料來源未連接**：Grafana 在啟動時會自動讀取 `grafana/provisioning/datasources/datasource.yml`，請確認其 URL 設定為 `http://prometheus:9090`。