import streamlit as st
from google import genai
import matplotlib.pyplot as plt
import pandas as pd
import pyperclip  # クリップボードへのコピー用

# ページレイアウトを Wide に設定
st.set_page_config(page_title="MealPlan Maestro", layout="wide")

# --- 初期設定 ---
try:
    api_key = st.secrets["gemini"]["API_KEY"]
except KeyError:
    st.error("Error: secrets ファイルの [gemini] セクションに 'API_KEY' が設定されていません。")
    st.stop()

client = genai.Client(api_key=api_key, http_options={'api_version': 'v1alpha'})

# --- matplotlib 日本語対応 ---
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["Noto Sans CJK JP", "IPAexGothic", "Arial Unicode MS"]

# --- 献立生成関数 ---
def generate_meal_plan(num_users, allergy_info, budget_per_day, cooking_equipment, preferences, day, region, season, age_min, age_max, user_category):
    prompt = f"""
以下の条件に基づき、{day}日分の献立（朝食、昼食、夕食）を作成してください。各日の献立は異なる内容で、栄養バランスを重視してください。

【対象利用者層】
対象は「{user_category}」で、利用者の年齢は {age_min} 歳から {age_max} 歳と想定します。

【条件】（必ず守ること）
1. 各日の献立には、朝食、昼食、夕食のメニューと、各メニューの栄養価（カロリー、たんぱく質、脂質、炭水化物）を明記する。
2. 栄養バランス：対象利用者層に合わせ、男子は1日2800キロカロリー、女子は1日2400キロカロリーを目安とする。必要に応じて栄養素の補正案を提示する。
3. 同じ献立が繰り返されないようにする。
4. 利用者が食べやすく、喜ぶ内容にする。
5. 季節の旬の食材と、地域（{region}）の伝統料理を優先する。
6. 1日あたりの予算 {budget_per_day} 円以内で収める。
7. 献立作成日数は、{day}日分のみ作成する。
8. リクエスト「{preferences}」を必ず考慮する。
9. 一日に同じ種類の食事が複数回出ないようにする（例：昼に牛丼、夜に豚丼は避ける）。

【入力情報】
- 利用者数：{num_users}
- アレルギー情報：{allergy_info}
- 1日の予算：{budget_per_day} 円
- 調理設備：{cooking_equipment}
- リクエスト：{preferences}
- 作成日数：{day}
- 地域：{region}
- 季節：{season}
- 利用者の年齢：{age_min}歳〜{age_max}歳

【出力内容】
1. {day}日分の献立（朝食、昼食、夕食）
2. 各献立の栄養価（カロリー、たんぱく質、脂質、炭水化物）
3. 必要な食材リスト（食材名と分量）
    """
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=prompt
    )
    return response.text

# --- 買い物リスト生成関数（仮実装） ---
def generate_shopping_list(meal_plan_text):
    """
    献立テキストから必要な食材リストを抽出する（ここではダミーデータを返す）。
    """
    shopping_list = """
【買い物リスト】
- 白米: 5kg
- 鶏肉: 3kg
- 豚肉: 2kg
- 鮭: 1kg
- 野菜各種: 適量
- 豆腐: 2丁
- だしの素: 1パック
    """
    return shopping_list

# --- サイドバーによるコントロールパネル ---
st.sidebar.title("コントロールパネル")
st.sidebar.markdown("以下の項目を入力して献立を生成します。")
num_users = st.sidebar.number_input("利用者数", min_value=1, value=15, step=1)
allergy_info = st.sidebar.text_area("アレルギー情報", value="大豆・牛乳アレルギー対応")
budget_per_day = st.sidebar.number_input("1日の予算 (円)", min_value=100, value=900, step=50)
cooking_equipment = st.sidebar.text_input("調理設備", value="ガスコンロ, 電子レンジ, 炊飯器")
preferences = st.sidebar.text_input("リクエスト", value="和食中心、週に1回洋食も入れたい")
day = st.sidebar.number_input("作成日数", min_value=1, max_value=30, value=7, step=1)
region = st.sidebar.selectbox("地域", ["東京", "大阪", "福岡", "その他"])
season = st.sidebar.selectbox("季節", ["春", "夏", "秋", "冬"])
age_min = st.sidebar.number_input("利用者の最低年齢", min_value=10, max_value=100, value=18, step=1)
age_max = st.sidebar.number_input("利用者の最高年齢", min_value=10, max_value=100, value=25, step=1)
user_category = st.sidebar.selectbox("対象利用者層", ["学生", "一般家庭", "社員寮", "その他"])

# --- メイン画面 ---
st.title("MealPlan Maestro")
st.markdown("""
このアプリは、栄養バランスに優れた献立を自動生成します。  
""")

if st.button("献立を生成する"):
    with st.spinner("献立を生成中..."):
        meal_plan = generate_meal_plan(num_users, allergy_info, budget_per_day, cooking_equipment, preferences, day, region, season, age_min, age_max, user_category)
    st.subheader("生成された献立")
    st.markdown("### 献立詳細")
    st.markdown(f"```\n{meal_plan}\n```")
    
    # 献立をコピーする機能
    if st.button("献立をコピーする"):
        try:
            pyperclip.copy(meal_plan)
            st.success("献立のテキストがクリップボードにコピーされました。")
        except Exception as e:
            st.error("クリップボードへのコピーに失敗しました。手動でコピーしてください。")
    
    # 買い物リストの生成
    shopping_list = generate_shopping_list(meal_plan)
    st.subheader("生成された買い物リスト")
    st.markdown(f"```\n{shopping_list}\n```")
