import streamlit as st
import datetime
import calendar
import jpholiday
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import gspread_formatting as gsf
import unicodedata

# --- 1. 【デザイン設定】白背景・視認性重視CSS ---
st.set_page_config(page_title="シフト申請", layout="centered")

st.markdown("""
<style>
/* ===== ダークモード完全無効化 ===== */
:root { color-scheme: light only !important; }
html  { color-scheme: light only !important; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"],
[data-testid="stMain"],
.stApp,
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
.main .block-container {
    background-color: #FFFFFF !important;
    color: #1A1A1A !important;
}
@media (prefers-color-scheme: dark) {
    html, body,
    [data-testid="stAppViewContainer"],
    [data-testid="stApp"],
    [data-testid="stMain"],
    .stApp,
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    .main .block-container {
        background-color: #FFFFFF !important;
        color: #1A1A1A !important;
    }
}

/* ===== レイアウト：横並び固定 ===== */
div[data-testid="stHorizontalBlock"] {
    display: flex !important;
    align-items: center !important;
}
[data-testid="stColumns"] > div:first-child {
    flex: 1 1 0% !important;
    min-width: 0 !important;
    padding-right: 5px !important;
}
[data-testid="stColumns"] > div:last-child {
    flex: 3 1 0% !important;
    min-width: 0 !important;
}
div[data-testid="stVerticalBlock"] > div { gap: 0.5rem !important; }

div[data-testid="stSegmentedControl"],
div[data-testid="stSegmentedControl"] *,
div[data-testid="stSegmentedControl"] label,
div[data-testid="stSegmentedControl"] label * {
    forced-color-adjust: none !important;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
}

div[data-testid="stSegmentedControl"] {
    background-color: #F0F4FF !important;
    border: 1px solid #D0D0D0 !important;
    border-radius: 8px !important;
}
div[data-testid="stSegmentedControl"] label {
    background-color: #BBDEFB !important;
    border-radius: 6px !important;
}
div[data-testid="stSegmentedControl"] label * {
    background-color: #BBDEFB !important;
    color: #1565C0 !important;
    font-weight: 600 !important;
}
div[data-testid="stSegmentedControl"] [aria-checked="true"] {
    background-color: #1565C0 !important;
    border-radius: 6px !important;
}
div[data-testid="stSegmentedControl"] [aria-checked="true"] * {
    background-color: #1565C0 !important;
    color: #FFFFFF !important;
    font-weight: bold !important;
}
@media (prefers-color-scheme: dark) {
    div[data-testid="stSegmentedControl"] {
        background-color: #F0F4FF !important;
        border: 1px solid #D0D0D0 !important;
    }
    div[data-testid="stSegmentedControl"] label {
        background-color: #BBDEFB !important;
    }
    div[data-testid="stSegmentedControl"] label * {
        background-color: #BBDEFB !important;
        color: #1565C0 !important;
        font-weight: 600 !important;
    }
    div[data-testid="stSegmentedControl"] [aria-checked="true"] {
        background-color: #1565C0 !important;
    }
    div[data-testid="stSegmentedControl"] [aria-checked="true"] * {
        background-color: #1565C0 !important;
        color: #FFFFFF !important;
        font-weight: bold !important;
    }
}

/* ===== テキスト入力欄（備考欄）===== */
div[data-baseweb="input"],
div[data-baseweb="input"] *,
[data-testid="stTextInput"] input {
    background-color: #FFFFFF !important;
    color: #1A1A1A !important;
    border-color: #D0D0D0 !important;
}
@media (prefers-color-scheme: dark) {
    div[data-baseweb="input"],
    div[data-baseweb="input"] *,
    [data-testid="stTextInput"] input {
        background-color: #FFFFFF !important;
        color: #1A1A1A !important;
        border-color: #D0D0D0 !important;
    }
}

h1, h2, h3 { color: #1A237E !important; }
@media (prefers-color-scheme: dark) {
    h1, h2, h3 { color: #1A237E !important; }
}

label[data-testid="stWidgetLabel"] p,
label[data-testid="stWidgetLabel"] {
    color: #333333 !important;
    font-weight: 600 !important;
}
[data-testid="stSelectbox"] div[data-baseweb="select"] * {
    background-color: #FFFFFF !important;
    color: #1A1A1A !important;
}
@media (prefers-color-scheme: dark) {
    label[data-testid="stWidgetLabel"] p { color: #333333 !important; }
    [data-testid="stSelectbox"] div[data-baseweb="select"] * {
        background-color: #FFFFFF !important;
        color: #1A1A1A !important;
    }
}

div[data-testid="stAlert"] {
    background-color: #E8F4FD !important;
    border-left: 4px solid #1565C0 !important;
    color: #1A237E !important;
}
@media (prefers-color-scheme: dark) {
    div[data-testid="stAlert"] {
        background-color: #E8F4FD !important;
        color: #1A237E !important;
    }
}

hr { border-color: #E0E0E0 !important; }

button[kind="primary"],
[data-testid="stBaseButton-primary"] {
    background-color: #1565C0 !important;
    color: #FFFFFF !important;
    font-weight: bold !important;
    border-radius: 8px !important;
    border: none !important;
}
button[kind="primary"]:hover,
[data-testid="stBaseButton-primary"]:hover {
    background-color: #0D47A1 !important;
}
@media (prefers-color-scheme: dark) {
    button[kind="primary"],
    [data-testid="stBaseButton-primary"] {
        background-color: #1565C0 !important;
        color: #FFFFFF !important;
    }
}
</style>
""", unsafe_allow_html=True)


# --- ★ 不可視文字も完全に除去するクリーニング関数 ---
def aggressive_clean(text):
    if not text:
        return ""
    text = unicodedata.normalize('NFKC', str(text))
    text = text.replace(" ", "").replace("　", "").replace("\n", "").replace("\r", "").replace("\xa0", "").strip()
    return text


# --- JS：MutationObserver でインラインスタイルを直接書き込み（ダークモード完全対策） ---
st.markdown("""
<script>
(function () {
    function applySegmentStyles() {
        document.querySelectorAll('[data-testid="stSegmentedControl"]').forEach(function (ctrl) {
            ctrl.style.setProperty('background-color', '#F0F4FF', 'important');
            ctrl.style.setProperty('border', '1px solid #D0D0D0', 'important');
            ctrl.style.setProperty('border-radius', '8px', 'important');

            ctrl.querySelectorAll('label').forEach(function (label) {
                var isChecked = !!label.querySelector('[aria-checked="true"]');
                var bg  = isChecked ? '#1565C0' : '#BBDEFB';
                var col = isChecked ? '#FFFFFF'  : '#1565C0';
                var fw  = isChecked ? 'bold'     : '600';

                label.style.setProperty('background-color', bg,    'important');
                label.style.setProperty('border-radius',    '6px', 'important');
                label.querySelectorAll('*').forEach(function (el) {
                    el.style.setProperty('background-color', bg,  'important');
                    el.style.setProperty('color',            col, 'important');
                    el.style.setProperty('font-weight',      fw,  'important');
                });
            });
        });
    }

    var observer = new MutationObserver(applySegmentStyles);
    observer.observe(document.body, { childList: true, subtree: true, attributes: true });
    applySegmentStyles();
})();
</script>
""", unsafe_allow_html=True)


# --- 2. スプレッドシート接続設定 ---
# ★【修正①】スプレッドシートIDで開く（同名ファイルが複数ある場合の誤開きを防止）
# secrets.toml に以下を追加してください：
#   [spreadsheet]
#   id = "（スプレッドシートURLの /d/〇〇〇/ の部分）"
SPREADSHEET_ID = st.secrets["spreadsheet"]["id"]


def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    return gspread.authorize(creds)


@st.cache_data(ttl=60)
def load_staff_master():
    client = get_gspread_client()
    # ★【修正②】open_by_key でIDを使って開く
    spreadsheet = client.open_by_key(SPREADSHEET_ID)
    master_sheet = spreadsheet.worksheet("スタッフ一覧")
    data = master_sheet.get_all_records()
    staff_dict = {}
    for row in data:
        store = str(row["店舗名"])
        staff = str(row["スタッフ名"])
        cleaned_staff = aggressive_clean(staff)
        if cleaned_staff:
            if store not in staff_dict:
                staff_dict[store] = []
            staff_dict[store].append(staff)  # 表示用には元の名前を使う
    return staff_dict


# --- 3. 画面の作成 ---
st.title("📅 シフト申請")

try:
    staff_data = load_staff_master()
    stores = list(staff_data.keys())
except Exception as e:
    st.error(f"名簿読み込みエラー: {e}")
    st.stop()

st.subheader("👤 あなたの情報を選択してください")
selected_store = st.selectbox("所属店舗", stores)
selected_staff = st.selectbox("スタッフ名", staff_data[selected_store])

st.write("---")

today = datetime.date.today()
if today.month == 12:
    year, month = today.year + 1, 1
else:
    year, month = today.year, today.month + 1

st.subheader(f"📅 【{year}年{month}月分】のシフト")

st.markdown("""
<div style="background-color:#F0F4FF; border-radius:8px; padding:12px 16px; margin-bottom:8px; font-size:0.9em; color:#1A1A1A;">
　🟡 <b>希望休</b>：休み希望（1日前後ずれても良い）<br>
　🔴 <b>確定休</b>：確実に取りたいお休み
</div>
""", unsafe_allow_html=True)

st.info("💡 シフトを入力してください。")

# --- 4. カレンダーデータ作成 ---
num_days = calendar.monthrange(year, month)[1]
selections = {}
date_strings = {}

for day in range(1, num_days + 1):
    date_obj = datetime.date(year, month, day)
    weekday_str = ["月", "火", "水", "木", "金", "土", "日"][date_obj.weekday()]
    is_holiday = jpholiday.is_holiday(date_obj)

    if is_holiday or date_obj.weekday() == 6:
        text_color = "#C62828"
    elif date_obj.weekday() == 5:
        text_color = "#1565C0"
    else:
        text_color = "#1A1A1A"

    date_str = f"{day}日({weekday_str})"
    date_strings[day] = date_str

    col1, col2 = st.columns([1, 3], vertical_alignment="center")

    with col1:
        st.markdown(
            f"<div style='color: {text_color}; font-weight: bold; white-space: nowrap;'>{date_str}</div>",
            unsafe_allow_html=True
        )
    with col2:
        selections[day] = st.segmented_control(
            f"{day}日の状態",
            options=["出勤", "希望休", "確定休"],
            default="出勤",
            key=f"btn_{day}",
            label_visibility="collapsed"
        )

    st.markdown(
        "<hr style='margin: 0px; padding: 0px; border-top: 1px solid #E0E0E0;'>",
        unsafe_allow_html=True
    )

st.write("")
memo = st.text_input("備考（任意）", placeholder="例：希望休の連休は翌週でも可能です")
st.write("---")


# --- 5. 【送信 ＆ 即時転記】 ---
if st.button("この内容でシフトを確定する", type="primary"):
    with st.spinner('シフト表を更新中...（約10秒お待ちください）'):
        try:
            client = get_gspread_client()
            # ★【修正③】ここも open_by_key に統一
            ss = client.open_by_key(SPREADSHEET_ID)

            # 受信シートへの追記
            reception_ws = ss.worksheet("シフト申請受信")
            k_list = [date_strings[day] for day, status in selections.items() if status == "希望休"]
            c_list = [date_strings[day] for day, status in selections.items() if status == "確定休"]
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            reception_ws.append_row([now, selected_store, selected_staff, f"{year}年{month}月", "、".join(k_list), "、".join(c_list), memo])

            # シフトシートへの転記
            shift_ws = ss.worksheet("シフト")
            a_col_values = shift_ws.col_values(1)

            target_row = None
            clean_target = aggressive_clean(selected_staff)
            debug_list = []

            for i, cell_val in enumerate(a_col_values):
                clean_cell = aggressive_clean(cell_val)
                if not clean_cell:
                    continue

                # ★【修正④】repr() で不可視文字を可視化してデバッグリストに記録
                debug_list.append(f"{i+1}行目: {clean_cell}  (生の値: {repr(cell_val)})")

                if clean_target == clean_cell or clean_target in clean_cell or clean_cell in clean_target:
                    target_row = i + 1
                    break

            if target_row is None:
                st.error(f"⚠️ スプレッドシートの『シフト』シートに『{selected_staff}』さんが見つかりませんでした。")
                st.info(f"🔍 探している名前（クリーニング後）: {repr(clean_target)}")

                if not debug_list:
                    st.warning(
                        "🔍 A列を読み取りましたが、文字が1つも入っていませんでした。\n\n"
                        "名前が入っているのはB列だったり、A列とB列がセルの結合でくっついていたりしませんか？"
                    )
                else:
                    st.warning("🔍 プログラムが読み取ったA列のデータ（生の値も含む）:\n\n" + "\n".join(debug_list))

                st.stop()

            # 見つかった行に1ヶ月分を書き込む
            for day in range(1, num_days + 1):
                status = selections[day] or "出勤"
                col = day + 1

                if status == "希望休":
                    val, bg_color = "", gsf.Color(1, 1, 0)
                elif status == "確定休":
                    val, bg_color = "", gsf.Color(1, 0.6, 0.6)
                else:
                    val, bg_color = "○", gsf.Color(1, 1, 1)

                shift_ws.update_cell(target_row, col, val)
                fmt = gsf.CellFormat(backgroundColor=bg_color)
                gsf.format_cell_range(shift_ws, gspread.utils.rowcol_to_a1(target_row, col), fmt)

            st.success(f"✅ {selected_staff}さんのシフトを更新しました！")
            st.balloons()

        except Exception as e:
            st.error(f"システムエラー: {e}")