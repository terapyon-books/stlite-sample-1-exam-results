import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None


@st.cache_data
def get_data(file) -> pd.DataFrame:
    """
    Reads an Excel file and returns a pandas DataFrame.

    Parameters:
        file (file-like object): The Excel file to read.

    Returns:
        pd.DataFrame: The DataFrame containing the data from the Excel file.
    """
    df = pd.read_excel(file, dtype={"生徒番号": str})
    return df


st.title("成績評価の可視化")
st.text("Excelファイルを元に成績評価の可視化とダウンロード")

st.header("入力データ")
if st.session_state.uploaded_file is None:
    st.subheader("Excelファイルをアップロードします。")

    st.markdown("""Excelファイルのフォーマットは以下の通り

    - 1行目はヘッダー行。2行目以降がデータ行。
    - 8列で構成する

    | 生徒番号 | 名前 | クラス | 国語 | 数学 | 社会 | 理科 | 英語 |
    |---------|------|-------|-----|-----|-----|-----|-----|
    | 2024001 | 山田 太郎 | C | 65 | 70 | 72 | 68 | 75 |
    | 2024002 | 佐藤 花子 | B | 91 | 85 | 89 | 92 | 87 |            
    """)
    st.divider()

    uploaded_file = st.file_uploader("成績の入ったExcelファイル", type="xlsx")
    if uploaded_file and st.button("アップロード"):
        st.session_state.uploaded_file = uploaded_file
        st.experimental_rerun()
else:
    st.subheader("アップロード済みのファイル")
    if st.button("ファイルを削除"):
        st.session_state.uploaded_file = None
        st.experimental_rerun()
    df = get_data(st.session_state.uploaded_file)
    df_open_btn = st.toggle("アップロードデータを表示")
    if df_open_btn:
        st.write(st.session_state.uploaded_file.name)
        st.write(df)

    st.header("条件の選択")
    name_col = df.columns[1]
    class_col = df.columns[2]
    subject_names = df.columns[3:]
    class_names = np.sort(df.loc[:, "クラス"].unique())

    filterd_df = df
    class_options = st.multiselect("クラスでフィルター", class_names)
    if class_options:
        filterd_df = filterd_df.loc[df.loc[:, "クラス"].isin(class_options), :]
    subject_options = st.multiselect("教科でフィルター", df.columns[3:])
    if subject_options:
        filterd_df = filterd_df.loc[:, [name_col, class_col] + subject_options]
        selected_subjects = filterd_df.columns[2:]
    else:
        selected_subjects = subject_names

    graph_option = st.selectbox("グラフの選択", ("個人別", "クラス別", "教科別分布"))

    if graph_option == "個人別":
        chart_cols = [name_col] + selected_subjects.to_list()
        chart_data = filterd_df.loc[:, chart_cols]
        st.bar_chart(
            chart_data,
            x=name_col,
            y=selected_subjects.to_list(),
            use_container_width=True,
        )
    elif graph_option == "クラス別":
        col_name = "クラス"
        if st.toggle("教科別に表示"):
            chart_data = filterd_df.groupby(col_name).mean(numeric_only=True)
            st.bar_chart(
                chart_data, y=selected_subjects.to_list(), use_container_width=True
            )
        else:
            df_groupby_class = filterd_df.groupby(col_name)
            chart_data = (
                df_groupby_class[selected_subjects.to_list()].mean().sum(axis=1)
            )
            st.bar_chart(chart_data, use_container_width=True)
            st.write(chart_data)
    elif graph_option == "教科別分布":
        ncols=len(selected_subjects)
        if ncols > 1:
            fig, axex = plt.subplots(1, ncols, figsize=(20, 10))
            for i, subject in enumerate(selected_subjects):
                subject_data = filterd_df.loc[:, subject]
                axex[i].hist(subject_data, bins=5)
        else:
            fig, ax = plt.subplots(1, 1, figsize=(20, 10))
            subject_data = filterd_df.loc[:, selected_subjects[0]]
            ax.hist(subject_data, bins=5)

        if ncols > 1:
            st.text(f"順に {' / '.join(selected_subjects.to_list())} のヒストグラムを表示します。")
        else:
            st.text(f"{' / '.join(selected_subjects.to_list())} のヒストグラムを表示します。")
        st.pyplot(fig)

    
    st.write(filterd_df)
