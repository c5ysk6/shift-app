import streamlit as st
import datetime
import calendar
import jpholiday
import gspread
from oauth2client.service_account import ServiceAccountCredentials
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
# スタッフ一覧は毎年共通の別ファイル（master）を使用
# シフト用SPREADSHEET_IDは月選択後に年ごとに動的にセットされます
MASTER_SPREADSHEET_ID = st.secrets["spreadsheet"]["master"]

# セルの値 → segmented_control の選択肢 への変換マップ
CELL_TO_STATUS = {
    "":  "出勤",
    "希": "希望休",
    "休": "確定休",
}
# segmented_control の選択肢 → 書き込む値 への変換マップ
STATUS_TO_CELL = {
    "出勤":  "",
    "希望休": "希",
    "確定休": "休",
}


def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    return gspread.authorize(creds)


@st.cache_data(ttl=60)
def load_staff_master(spreadsheet_id: str):
    """スタッフ一覧シートから {店舗名: [スタッフ名, ...]} の辞書を返す"""
    client = get_gspread_client()
    spreadsheet = client.open_by_key(spreadsheet_id)
    master_sheet = spreadsheet.worksheet("スタッフ一覧")
    data = master_sheet.get_all_records()
    staff_dict = {}
    for row in data:
        store = str(row["店舗名"])
        staff = str(row["スタッフ名"])
        if aggressive_clean(staff):
            if store not in staff_dict:
                staff_dict[store] = []
            staff_dict[store].append(staff)
    return staff_dict


@st.cache_data(ttl=30)
def load_existing_shift(staff_name: str, sheet_name: str, num_days: int, spreadsheet_id: str) -> dict:
    """
    指定シートから staff_name の行を探し、
    {1: "出勤", 2: "希望休", ...} の形式で返す。
    シートが存在しない・スタッフが見つからない場合は全日「出勤」を返す。
    """
    default = {day: "出勤" for day in range(1, num_days + 1)}
    try:
        client = get_gspread_client()
        ss = client.open_by_key(spreadsheet_id)

        try:
            shift_ws = ss.worksheet(sheet_name)
        except gspread.exceptions.WorksheetNotFound:
            return default

        a_col_values = shift_ws.col_values(1)
        clean_target = aggressive_clean(staff_name)
        target_row = None

        for i, cell_val in enumerate(a_col_values):
            clean_cell = aggressive_clean(cell_val)
            if not clean_cell:
                continue
            if clean_target == clean_cell or clean_target in clean_cell or clean_cell in clean_target:
                target_row = i + 1
                break

        if target_row is None:
            return default

        # 該当行を一括取得（2列目〜 が各日のデータ）
        row_values = shift_ws.row_values(target_row)
        result = {}
        for day in range(1, num_days + 1):
            col_index = day + 1          # 2列目〜
            list_index = col_index - 1   # リストは0始まり
            if list_index < len(row_values):
                cell_val = row_values[list_index]
                result[day] = CELL_TO_STATUS.get(cell_val, "出勤")
            else:
                result[day] = "出勤"
        return result

    except Exception:
        # 読み込み失敗時もアプリを止めず全日「出勤」で続行
        return default


# --- 3. 画面の作成 ---
st.title("📅 シフト申請")

# --- まず月を選択（年のIDを決めるために最初に行う）---
today = datetime.date.today()

# 選択肢：当月から3ヶ月先まで（年をまたいでもOK）
month_options = []
for i in range(4):
    m = today.month + i
    y = today.year + (m - 1) // 12
    m = ((m - 1) % 12) + 1
    month_options.append((y, m))

month_labels = [f"{y}年{m}月" for y, m in month_options]

st.subheader("📆 提出する月を選択してください")
selected_label = st.selectbox("対象月", month_labels, index=1)  # デフォルトは翌月
selected_index = month_labels.index(selected_label)
year, month = month_options[selected_index]

# 選択した年に対応するスプレッドシートIDを自動で切り替え
SPREADSHEET_ID = st.secrets["spreadsheet"][str(year)]

st.write("---")

# --- 年のIDが決まったのでスタッフ一覧を読み込む ---
try:
    staff_data = load_staff_master(MASTER_SPREADSHEET_ID)
    stores = list(staff_data.keys())
except Exception as e:
    st.error(f"名簿読み込みエラー: {e}")
    st.stop()

st.subheader("👤 あなたの情報を選択してください")
selected_store = st.selectbox("所属店舗", stores)
selected_staff = st.selectbox("スタッフ名", staff_data[selected_store])

num_days = calendar.monthrange(year, month)[1]

# 動的シート名（例：「4月シフト」）
shift_sheet_name = f"{month}月シフト"

st.subheader(f"📅 【{year}年{month}月分】のシフト")

st.markdown("""
<div style="background-color:#F0F4FF; border-radius:8px; padding:12px 16px; margin-bottom:8px; font-size:0.9em; color:#1A1A1A;">
　🟡 <b>希望休</b>：休み希望（1日前後ずれても良い）<br>
　🔴 <b>確定休</b>：確実に取りたいお休み
</div>
""", unsafe_allow_html=True)

# ★ 既存シフトをスプレッドシートから読み込む
with st.spinner("前回のシフトを読み込み中..."):
    existing_shift = load_existing_shift(selected_staff, shift_sheet_name, num_days, SPREADSHEET_ID)

# 既存データがあれば通知メッセージを切り替える
has_existing = any(v != "出勤" for v in existing_shift.values())
if has_existing:
    st.info("💡 前回提出済みのシフトを反映しています。変更したい日だけ修正してください。")
else:
    st.info("💡 シフトを入力してください。")

# --- 4. カレンダーデータ作成 ---
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
        # ★ default に既存シフトの値をセット
        selections[day] = st.segmented_control(
            f"{day}日の状態",
            options=["出勤", "希望休", "確定休"],
            default=existing_shift[day],
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
    with st.spinner("シフト表を更新中...（約10秒お待ちください）"):
        try:
            client = get_gspread_client()
            ss = client.open_by_key(SPREADSHEET_ID)

            # 受信シートへの追記
            reception_ws = ss.worksheet("シフト申請受信")
            k_list = [date_strings[day] for day, status in selections.items() if status == "希望休"]
            c_list = [date_strings[day] for day, status in selections.items() if status == "確定休"]
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            reception_ws.append_row([
                now, selected_store, selected_staff,
                f"{year}年{month}月",
                "、".join(k_list),
                "、".join(c_list),
                memo
            ])

            # ★ 動的シート名でシフトシートを開く
            try:
                shift_ws = ss.worksheet(shift_sheet_name)
            except gspread.exceptions.WorksheetNotFound:
                st.error(f"⚠️ スプレッドシートに『{shift_sheet_name}』シートが見つかりません。シート名を確認してください。")
                st.stop()

            # 該当スタッフの行を検索
            a_col_values = shift_ws.col_values(1)
            target_row = None
            clean_target = aggressive_clean(selected_staff)
            debug_list = []

            for i, cell_val in enumerate(a_col_values):
                clean_cell = aggressive_clean(cell_val)
                if not clean_cell:
                    continue
                debug_list.append(f"{i+1}行目: {clean_cell}  (生の値: {repr(cell_val)})")
                if clean_target == clean_cell or clean_target in clean_cell or clean_cell in clean_target:
                    target_row = i + 1
                    break

            if target_row is None:
                st.error(f"⚠️ 『{shift_sheet_name}』シートに『{selected_staff}』さんが見つかりませんでした。")
                st.info(f"🔍 探している名前（クリーニング後）: {repr(clean_target)}")
                if not debug_list:
                    st.warning("🔍 A列を読み取りましたが、文字が1つも入っていませんでした。")
                else:
                    st.warning("🔍 読み取ったA列のデータ:\n\n" + "\n".join(debug_list))
                st.stop()

            # 1ヶ月分を書き込む
            for day in range(1, num_days + 1):
                status = selections[day] or "出勤"
                col = day + 1
                val = STATUS_TO_CELL[status]
                shift_ws.update_cell(target_row, col, val)

            # キャッシュをクリアして次回表示時に最新データを反映
            load_existing_shift.clear()

            st.success(f"✅ {selected_staff}さんの{month}月シフトを更新しました！")
            st.balloons()

        except Exception as e:
            st.error(f"システムエラー: {e}")
