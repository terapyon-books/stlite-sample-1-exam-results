# Streamlitデモアプリ

- 名称: stlite-sample-1-exam-results
- 目的: Streamlitの最小限のサンプル用デモアプリ
- 機能: Excelファイルからグラフ表示や結果のダウンロード

このレポジトリは、XXXX用のサンプルデモアプリです。
PythonスクリプトやJupyterLabで実行できるものをStreamlitでGUI化を行います。
さらに、stlite/@desktopに対応させ、OSにインストール可能なアプリです。


## 機能詳細

- Excelで、試験結果（例えば、20人分、5教科）をファイルアップロード
- グラフで分布や標準偏差などを表示。表示をラジオボタンとかで切り替えできる。
- 相対評価の結果をリスト表示
- 結果のダウンロード


## セットアップ

### 必須条件

- Python 3.8以上
- Streamlit 1.31以上
- npm or yarn (node v18以降)

### 仮想環境

venvを用いてインストールを行います。
venvは、Pythonの標準ライブラリです。

https://docs.python.org/ja/3/tutorial/venv.html


```sh
% cd (任意のフォルダ)
% python3 -m venv venv
% source venv/bin/activate
```

### インストール

単体インストール

```sh
(venv) % pip install streamlit
```

GitHubからパッケージをダウンロードしてインストール（推奨）

```sh
(venv) % git clone git@github.com:terapyon-books/stlite-sample-1-exam-results.git
(venv) % stlite-sample-1-exam-results
(venv) % pip install -r requirements.txt -c constraints.txt
```

### node

```sh
% nvm use v20
% npm install
```

## 起動方法

```
(venv) % streamlit run sample_1_exam_results/streamlit_app.py
```

## 表示確認

起動すると、デフォルトブラウザが立ち上がり表示確認ができる。

もし、ブラウザが立ち上がらない場合は、コンソールに表示されるポート付URLをブラウザで呼び出す。



# LICENCE

This package is under MIT License.
Please see [LICENSE](LICENSE) file.