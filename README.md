# 政大通後端組主機手冊

公開教學版。所有 IP、網域、主機路徑、服務名稱、資料庫識別與網路配置均為示例，不代表正式環境。

## 維護內容

編輯 `build.py`，執行 `python build.py` 產生六章 HTML 與目錄首頁。樣式與互動位於 `dist/style.css`、`dist/app.js`。可直接開啟 `dist/index.html`。

## GitHub Pages

Settings → Pages → Source 選擇 GitHub Actions。推送至 main 或手動執行 workflow 時，自動產生網站並部署 `dist/`。相對連結支援 repository 子路徑。

請勿加入正式憑證、使用者資料或內部主機配置。例子應明確標明示範用途。
