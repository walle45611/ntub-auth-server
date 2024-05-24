# ntub-no-google-auth

這是一個使用 Django + restframework 框架的 Python 專案。

## 環境設定

首先，請確保你的系統已經安裝了 Python 和 Django。然後，你需要設定環境變數。你可以在 `env.yml` 文件中找到需要設定的環境變數。
```
conda env create -f env.yml
```

## 啟動伺服器

要啟動伺服器，請在終端機中輸入以下指令：

```sh
python src/manage.py runserver