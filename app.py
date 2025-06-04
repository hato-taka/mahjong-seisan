import streamlit as st
import pandas as pd

st.set_page_config(page_title="麻雀精算ツール", layout="centered")
st.title("🀄 麻雀 精算ツール")
st.markdown("25000点持ち 30000点返し・ウマ5-10・レート50 の精算ツール")

# プレイヤー人数選択
num_players = st.radio("プレイヤー人数", [3, 4], index=1, horizontal=True)

# 点数設定
start_score = 25000
base_score = 30000  # 返し点（オカ）
rate = 50  # 1点 = 50円

# プレイヤー情報初期化
st.markdown("### 順位順に得点を入力")
rank_labels = ["1位", "2位", "3位", "4位"][:num_players]
expected_total = start_score * num_players
player_names = []
player_scores = [0] * num_players

# 2位～の得点を保持（非表示）
for i, rank in enumerate(rank_labels[1:], start=1):
    key = f"score_{i}"
    if key not in st.session_state:
        st.session_state[key] = start_score
    player_scores[i] = st.session_state[key]
    player_names.append(rank)

# 1位の得点を計算
remaining_total = expected_total - sum(player_scores[1:])
player_scores[0] = remaining_total
player_names.insert(0, "1位")

# 1位の得点を上に表示
st.number_input("1位の得点", value=remaining_total, disabled=True, key="display_score_0")

# 2位～の得点を表示
for i, rank in enumerate(rank_labels[1:], start=1):
    st.session_state[f"score_{i}"] = st.number_input(
        f"{rank}の得点", min_value=0, max_value=100000, step=100,
        key=f"display_score_{i}", value=st.session_state[f"score_{i}"]
    )

# ルール表示
with st.expander("ルール詳細（変更不可）"):
    st.markdown(f"""
    - **持ち点**：{start_score}点  
    - **返し点（オカ）**：{base_score}点  
    - **ウマ**：1位 +10 / 2位 +5 / 3位 -5 / 4位 -10  
    - **レート**：{rate}点 = 1円
    """)

# 精算ロジック
def calculate_results(names, scores):
    uma = [10, 5, -5, -10]  # ウマ5-10
    players = list(zip(names, scores))
    players.sort(key=lambda x: x[1], reverse=True)

    results = []
    for idx, (name, score) in enumerate(players):
        diff = (score - base_score) / 1000  # 千点単位
        final = diff + uma[idx]
        results.append({
            "name": name,
            "score": score,
            "rank": idx + 1,
            "diff": diff,
            "uma": uma[idx],
            "total": final,
        })
    return results

# 計算ボタン
if st.button("精算を実行"):
    total_score = sum(player_scores)
    if total_score != expected_total:
        st.error(f"合計得点が{expected_total}点ではありません（現在: {total_score}点）")
    else:
        results = calculate_results(player_names, player_scores)

        st.markdown("### 🔢 結果表示")
        df = pd.DataFrame([
            {
                "得点": int(r["score"]),
                "精算点": f"{r['total']:+.1f}",
                "支払い金額": f"{int(r['total'] * 1000):+d}点",
                "支払い金額（円）": f"{int(r['total'] * 1000 * rate):+d}円"
            }
            for r in results
        ])
        st.dataframe(df, hide_index=True)

        st.markdown("### 💸 支払い結果（概算・未実装）")
        st.info("※誰が誰に支払うかの個別計算は今後実装予定です")