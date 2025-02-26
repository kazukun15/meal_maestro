import streamlit as st
from google import genai

# --- 初期設定 ---
# secrets ファイルの [gemini] セクションから API_KEY を取得する
try:
    api_key = st.secrets["gemini"]["API_KEY"]
except KeyError:
    st.error("Error: secrets ファイルの [gemini] セクションに 'API_KEY' が設定されていません。")
    st.stop()

# クライアントの初期化
client = genai.Client(api_key=api_key, http_options={'api_version': 'v1alpha'})

# --- 献立生成関数 ---
def generate_meal_plan(num_residents, allergy_info, budget_per_day, cooking_equipment, preferences, day):
    prompt = f"""
以下の条件に基づき、{day}日分の献立（朝食、昼食、夕食）を作成してください。各日の献立は異なる内容で、栄養バランスを重視してください。

【条件】（必ず守ること）
1. 各日の献立には、朝食、昼食、夕食のメニューと、各メニューの栄養価（カロリー、たんぱく質、脂質、炭水化物）を明記する。
2. 栄養バランス：男子は1日2800キロカロリー、女子は1日2400キロカロリーを目安とし、必要に応じて栄養素の補正案を提示する。
3. 同じ献立が繰り返されないようにする。
4. 寮生が食べやすく、喜ぶ内容にする。
5. 季節の食材を優先する。
6. 1日あたりの予算 {budget_per_day} 円以内で収める。
7. 献立作成日数は、{day}日分のみ作成する。
8. リクエスト「{preferences}」を必ず考慮する。
9. 一日に同じ種類の食事が複数回出ないようにする（例：昼に牛丼、夜に豚丼は避ける）。

【入力情報】
- 寮生人数：{num_residents}
- アレルギー情報：{allergy_info}
- 1日の予算：{budget_per_day} 円
- 調理設備：{cooking_equipment}
- リクエスト：{preferences}
- 作成日数：{day}

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

# --- サイドバーによるコントロールパネル ---
st.sidebar.title("コントロールパネル")
st.sidebar.markdown("以下の項目を入力して献立を生成します。")

num_residents = st.sidebar.number_input("寮生人数", min_value=1, value=15, step=1)
allergy_info = st.sidebar.text_area("アレルギー情報", value="大豆・牛乳アレルギー対応")
budget_per_day = st.sidebar.number_input("1日の予算 (円)", min_value=100, value=900, step=50)
cooking_equipment = st.sidebar.text_input("調理設備", value="ガスコンロ, 電子レンジ, 炊飯器")
preferences = st.sidebar.text_input("リクエスト", value="和食中心、週に1回洋食も入れたい")
day = st.sidebar.number_input("作成日数", min_value=1, max_value=30, value=7, step=1)

# --- メイン画面 ---
st.title("MealPlan Maestro")
st.markdown("""
このアプリは、Google Gemini 2.0 Flash を活用して、栄養バランスに優れた献立を自動生成します。  
**ユーザー重視のデザイン（UD）** を意識し、シンプルで直感的な操作性を実現しています。
""")

if st.button("献立を生成する"):
    with st.spinner("献立を生成中..."):
        meal_plan = generate_meal_plan(num_residents, allergy_info, budget_per_day, cooking_equipment, preferences, day)
    st.subheader("生成された献立")
    st.text_area("献立詳細", value=meal_plan, height=400)
