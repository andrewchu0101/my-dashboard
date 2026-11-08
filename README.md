# 🛡️ Operation Shield — 電商營運利潤止血與退貨風控中心

這是一個基於 Streamlit 與 Plotly 建構的電商退貨歸因與風控決策儀表板。

## 📊 專案架構 (輕量部署版)
```
my-dashboard/
├── data/                       # 瘦身聚合後的精簡資料 (僅 1.6MB，取代 90MB 原始檔)
│   ├── daily_cube.csv          # 日層級動態聯動表 (支援日期/國家/客群/材質篩選)
│   ├── sku_profiles.csv        # 4,931 筆商品銷退與帕累托指標
│   ├── customer_profiles.csv   # 5,939 筆客戶 RFM-R 分群資料
│   ├── country_summary.csv     # 跨國航線退貨率排行
│   └── material_summary.csv    # 陶瓷易碎材質對照數據
├── app.py                      # Streamlit 應用程式主程式
├── requirements.txt            # Python 依賴清單
├── .gitignore                  # Git 忽略設定
└── README.md                   # 專案說明文件
```

---

## 🚀 部署至 Streamlit Cloud 指南

### 步驟 1：在 GitHub 建立新公開倉庫 (Public Repo)
1. 前往 [GitHub.com](https://github.com/) 登入。
2. 點擊右上角 `+` $\rightarrow$ `New repository`。
3. 倉庫名稱填入：`retail-returns-dashboard`（或自訂）。
4. 設定為 **Public**，不要勾選加入 README 或 .gitignore（本機已有）。
5. 點擊 `Create repository`。

### 步驟 2：推送到 GitHub
在 `my-dashboard` 目錄下開啟終端機 (PowerShell 或 Git Bash)，依序執行：
```bash
# 1. 初始化 Git
git init

# 2. 加入所有檔案
git add .

# 3. 提交版本
git commit -m "feat: initial commit for Operation Shield Dashboard"

# 4. 指定主分支為 main
git branch -M main

# 5. 連接遠端倉庫 (請將 <YourUsername>/<RepoName> 替換為您的 GitHub 帳號與倉庫名)
git remote add origin https://github.com/<YourUsername>/<RepoName>.git

# 6. 推送至 GitHub
git push -u origin main
```

### 步驟 3：在 Streamlit Cloud 一鍵上線
1. 前往 [share.streamlit.io](https://share.streamlit.io/) 並使用 GitHub 帳號授權登入。
2. 點擊右上角 **"New app"**。
3. 在設定面板填入：
   - **Repository**: 選擇剛剛建立的倉庫（例如 `<YourUsername>/retail-returns-dashboard`）
   - **Branch**: `main`
   - **Main file path**: `app.py`
4. 點擊 **"Deploy!"**。
5. 等待約 1~2 分鐘，儀表板即可正式上線，獲得一個所有人皆可瀏覽的公開網址！

