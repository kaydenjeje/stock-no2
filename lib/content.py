"""정적 학습 콘텐츠 및 규칙 기반(비 AI) 텍스트 생성."""

from datetime import date

ONBOARD_QUESTIONS = [
    {"q": "이동평균선이 뭔지 아세요?", "options": ["잘 알아요", "들어는 봤어요", "처음 들어요"]},
    {"q": "RSI 지표를 들어보셨나요?", "options": ["잘 알아요", "들어는 봤어요", "처음 들어요"]},
    {"q": "외국인·기관 수급이 무슨 뜻인지 아세요?", "options": ["잘 알아요", "들어는 봤어요", "처음 들어요"]},
    {"q": "주식 계좌를 개설한 지 얼마나 되셨나요?", "options": ["6개월 미만", "6개월~2년", "2년 이상"]},
    {"q": "시장 정보를 얼마나 자주 확인하고 싶으세요?", "options": ["매일 확인하고 싶어요", "가끔 확인해요", "잘 모르겠어요"]},
]

LEARN_TERMS = {
    "이동평균선": "일정 기간 종가의 평균을 이은 선입니다. 5일선은 최근 5거래일, 20일선은 최근 20거래일 흐름을 보여줍니다.",
    "RSI": "최근 상승폭과 하락폭을 비교해 0~100으로 나타낸 지표입니다. 70을 넘으면 최근 상승 강도가 세다는 뜻이고, 30 아래면 하락 강도가 세다는 뜻입니다.",
    "PER": "주가를 주당순이익(EPS)으로 나눈 값입니다. 같은 업종 안에서 상대적으로 비교할 때 참고합니다.",
    "외국인·기관 수급": "외국인과 기관 투자자가 특정 기간 동안 순매수했는지 순매도했는지를 나타냅니다.",
    "거래량 비율": "오늘 거래량이 최근 20일 평균 거래량 대비 몇 배인지 나타냅니다. 비율이 높을수록 평소보다 관심이 몰렸다는 뜻입니다.",
    "52주 신고가": "최근 1년 동안의 최고가를 의미합니다. 현재가가 여기 가까울수록 신고가 경신에 가깝다는 뜻입니다.",
}

QUIZ_BANK = [
    {
        "q": "RSI가 70을 넘으면 무슨 뜻일까요?",
        "options": ["거래가 뜸하다는 뜻", "최근 상승 강도가 세다는 뜻", "무조건 떨어진다는 뜻"],
        "answer": 1,
    },
    {
        "q": "거래량 비율이 200%라면?",
        "options": ["평소보다 거래량이 2배 많다는 뜻", "평소보다 거래량이 절반이라는 뜻", "의미 없는 숫자"],
        "answer": 0,
    },
    {
        "q": "외국인·기관 동반 순매수는 무엇을 뜻하나요?",
        "options": ["개인 투자자만 사고 있다는 뜻", "외국인과 기관이 동시에 순매수했다는 뜻", "아무도 안 사고 있다는 뜻"],
        "answer": 1,
    },
]


def today_term():
    items = list(LEARN_TERMS.items())
    idx = date.today().timetuple().tm_yday % len(items)
    return items[idx]


def build_market_brief(scores, temp, temp_label):
    if not scores:
        return "오늘은 데이터를 불러오지 못했어요. 잠시 후 다시 확인해주세요."

    hot = [s for s in scores if s["score"] >= 75]
    sector_counts = {}
    for s in scores[:10]:
        sector_counts[s["sector"]] = sector_counts.get(s["sector"], 0) + 1
    top_sector = max(sector_counts, key=sector_counts.get) if sector_counts else None

    lines = [f"오늘 시장 온도는 {temp}도, '{temp_label}' 구간이에요."]
    if hot:
        lines.append(f"스코어 75점 이상인 종목이 {len(hot)}개 있어요.")
    if top_sector:
        lines.append(f"상위권에는 {top_sector} 업종이 가장 많이 보여요.")
    return " ".join(lines)
