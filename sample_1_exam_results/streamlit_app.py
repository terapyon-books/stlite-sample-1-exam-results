import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


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


def get_defult_threshold(ser: pd.Series) -> tuple[float, float, float, float]:
    """
    教科の平均値と標準偏差から5段階の閾値を算出

    Parameters:
        ser (pd.Series): 教科のSeries

    Returns:
        tuple: 閾値のタプル
    """
    # subject_std = ser.std()
    # subject_mean = ser.mean()
    subject_q1 = ser.quantile(0.25)
    subject_median = ser.median()
    subject_q3 = ser.quantile(0.75)
    subject_iqr = subject_q1 - subject_q3
    thresholds = (
        # subject_q1 - 1.5 * subject_iqr,
        subject_median - 2 * (subject_median - subject_q1),
        subject_q1,
        subject_median,
        # subject_q3 + 1.5 * subject_iqr
        subject_q3 + 2 * (subject_q3 - subject_median)
    )
    return thresholds


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
    subject_list = selected_subjects.to_list()

    graph_option = st.selectbox(
        "グラフの選択", ("個人別", "クラス別", "教科別分布", "全体分布", "教科別レベル")
    )

    # 各種グラフの描画
    if graph_option == "個人別":
        chart_cols = [name_col] + subject_list
        chart_data = filterd_df.loc[:, chart_cols]
        st.bar_chart(
            chart_data,
            x=name_col,
            y=subject_list,
            use_container_width=True,
        )
    elif graph_option == "クラス別":
        col_name = "クラス"
        if st.toggle("教科別に表示"):
            chart_data = filterd_df.groupby(col_name).mean(numeric_only=True)
            st.bar_chart(chart_data, y=subject_list, use_container_width=True)
        else:
            df_groupby_class = filterd_df.groupby(col_name)
            chart_data = df_groupby_class[subject_list].mean().sum(axis=1)
            st.bar_chart(chart_data, use_container_width=True)
            st.write(chart_data)
    elif graph_option == "教科別分布":
        fig_box = px.box(
            filterd_df.loc[:, subject_list],
            labels={"variable": "教科", "value": "得点"},
        )
        st.plotly_chart(fig_box)

        fig_violin = px.violin(
            filterd_df.loc[:, subject_list],
            y=subject_list,
            labels={"variable": "教科", "value": "得点"},
        )
        st.plotly_chart(fig_violin)
    elif graph_option == "全体分布":
        fig = px.scatter_matrix(filterd_df, dimensions=subject_list, color="クラス")
        st.plotly_chart(fig)
    elif graph_option == "教科別レベル":
        st.write("教科別のレベルを表示します。")
        for subject in subject_list:
            thresholds = get_defult_threshold(filterd_df.loc[:, subject])
            st.subheader(subject)
            fig_hist = px.histogram(
                filterd_df,
                x=subject,
                nbins=10,
                marginal="box",
                # color=class_col,
                # barmode="overlay",
            )

            # 閾値の追加
            for i, threshold in enumerate(thresholds):
                fig_hist.add_shape(
                    go.layout.Shape(
                        type="line",
                        x0=threshold,
                        x1=threshold,
                        y0=0,
                        y1=1,
                        yref="paper",
                        line=dict(
                            color="Red",
                            width=1.5,
                            dash="dot",
                        ),
                    )
                )
                fig_hist.add_annotation(
                    x=threshold,
                    y=0.95,
                    yref="paper",
                    text=f"Threshold {i+1}",
                    showarrow=False,
                )
            st.plotly_chart(fig_hist)
            st.write(filterd_df.loc[:, [name_col, class_col, subject]].sort_values(subject))

    st.write(filterd_df)
