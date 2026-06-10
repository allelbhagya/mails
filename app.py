import streamlit as st
from gmail_fetch import get_emails
from classifier import classify_email, summarize_email, DEFAULT_TAGS

st.set_page_config(page_title="email tagger", layout="wide")

st.markdown("""
    <style>
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .block-container { padding: 2rem 3rem; }
    .tag-chip {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 500;
        margin-bottom: 4px;
    }
    .email-row {
        border: 1px solid #e5e5e5;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 10px;
        background: #ffffff;
    }
    .email-subject { font-weight: 600; font-size: 15px; color: #1a1a1a; }
    .email-meta { font-size: 12px; color: #888; margin-top: 2px; }
    .email-summary { font-size: 13px; color: #444; margin-top: 8px; }
    </style>
""", unsafe_allow_html=True)

TAG_COLORS = {
    "newsletter": "#9fdc9d",
    "learning": "#83b7de",
    "general": "#b8aaf4",
}

def tag_color(tag):
    return TAG_COLORS.get(tag.lower(), "#e8f0fe")


if "tags" not in st.session_state:
    st.session_state.tags = DEFAULT_TAGS.copy()

with st.sidebar:
    st.markdown("### 🏷 tags")
    for tag, desc in st.session_state.tags.items():
        color = tag_color(tag)
        st.markdown(f'<span class="tag-chip" style="background:{color}">{tag}</span>', unsafe_allow_html=True)
        st.caption(desc)

    st.divider()
    st.markdown("### + create new tag")
    new_tag = st.text_input("tag name", placeholder="e.g. finance")
    new_desc = st.text_input("description", placeholder="bills, invoices, bank statements")
    if st.button("add tag") and new_tag and new_desc:
        st.session_state.tags[new_tag] = new_desc
        TAG_COLORS[new_tag] = "#fff7e6"
        st.success(f"added: {new_tag}")

st.markdown("## email tagger 🏷️")
st.caption("inspired by notion mail; tagging mails based on description - cosine similarity; create new tags too :) ")
st.divider()

if st.button("fetch and classify last 10 mails", type="primary"):
    with st.spinner("fetching from gmail beep beep"):
        emails = get_emails(10)

    results = []
    for email in emails:
        text = f"{email['subject']} {email['body']}"
        tag, score = classify_email(text, st.session_state.tags)
        summary = summarize_email(email["subject"], email["body"])
        results.append({
            "from": email["sender"],
            "subject": email["subject"],
            "tag": tag,
            "score": score,
            "summary": summary
        })

    for r in results:
        color = tag_color(r["tag"])
        st.markdown(f"""
        <div class="email-row">
            <span class="tag-chip" style="background:{color}">{r['tag']}</span>
            <div class="email-subject">{r['subject'][:80]}</div>
            <div class="email-meta">From: {r['from']} &nbsp;·&nbsp; Confidence: {r['score']}</div>
        </div>
        """, unsafe_allow_html=True)