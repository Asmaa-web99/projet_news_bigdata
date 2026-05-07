"""
Dashboard Streamlit pour la plateforme d'analyse News.
Visualisations interactives basées sur le Data Warehouse PostgreSQL.
"""
import os
from datetime import datetime
from collections import Counter

import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

# ================== CONFIGURATION ==================

st.set_page_config(
    page_title="📰 News Analytics Platform",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def get_engine():
    dwh_url = (
        f"postgresql://{os.getenv('DWH_USER', 'dwh_admin')}:"
        f"{os.getenv('DWH_PASSWORD', 'dwh_password')}"
        f"@{os.getenv('DWH_HOST', 'localhost')}:{os.getenv('DWH_PORT', '5433')}"
        f"/{os.getenv('DWH_DATABASE', 'news_warehouse')}"
    )
    return create_engine(dwh_url)

engine = get_engine()


@st.cache_data(ttl=60)
def load_data(query: str) -> pd.DataFrame:
    return pd.read_sql(query, engine)


# ================== HEADER ==================

st.title("📰 Plateforme d'Analyse de Médias")
st.markdown("**Architecture Big Data : Bronze → Silver → Gold → DWH → Dashboard**")
st.markdown("---")

# ================== SIDEBAR FILTRES ==================

st.sidebar.header("🔍 Filtres")

sources_df = load_data("SELECT source_name FROM dim_source ORDER BY source_name")
selected_sources = st.sidebar.multiselect(
    "Sources",
    sources_df['source_name'].tolist(),
    default=sources_df['source_name'].tolist()
)

languages_df = load_data("SELECT language_code, language_name FROM dim_language WHERE language_code != 'unknown'")
selected_langs = st.sidebar.multiselect(
    "Langues",
    languages_df['language_code'].tolist(),
    default=languages_df['language_code'].tolist(),
    format_func=lambda x: dict(zip(languages_df['language_code'], languages_df['language_name'])).get(x, x)
)

# Sécurité : éviter les listes vides dans le SQL
sources_filter = ','.join([f"'{s}'" for s in selected_sources]) if selected_sources else "''"
langs_filter = ','.join([f"'{l}'" for l in selected_langs]) if selected_langs else "''"

# ================== KPIs GLOBAUX ==================

kpi_query = f"""
SELECT 
    COUNT(*) AS total_articles,
    COUNT(DISTINCT f.source_id) AS total_sources,
    COUNT(DISTINCT f.language_id) AS total_languages,
    SUM(f.word_count) AS total_words,
    AVG(f.word_count)::INT AS avg_words
FROM fact_articles f
JOIN dim_source s ON f.source_id = s.source_id
JOIN dim_language l ON f.language_id = l.language_id
WHERE s.source_name IN ({sources_filter})
  AND l.language_code IN ({langs_filter})
"""
kpi = load_data(kpi_query).iloc[0]

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("📰 Articles", f"{int(kpi['total_articles']):,}")
col2.metric("🌐 Sources", int(kpi['total_sources']))
col3.metric("🗣️ Langues", int(kpi['total_languages']))
col4.metric("📝 Mots totaux", f"{int(kpi['total_words'] or 0):,}")
col5.metric("📊 Moy. mots/article", f"{int(kpi['avg_words'] or 0):,}")

st.markdown("---")

# ================== GRAPHIQUES ==================

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📊 Articles par source")
    df_source = load_data(f"""
        SELECT s.source_name, s.country, COUNT(*) AS articles
        FROM fact_articles f
        JOIN dim_source s ON f.source_id = s.source_id
        WHERE s.source_name IN ({sources_filter})
        GROUP BY s.source_name, s.country
        ORDER BY articles DESC
    """)
    if not df_source.empty:
        fig = px.bar(df_source, x='source_name', y='articles',
                     color='country', text='articles',
                     labels={'articles': "Nombre d'articles", 'source_name': 'Source'})
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("🗣️ Distribution par langue")
    df_lang = load_data(f"""
        SELECT l.language_name, COUNT(*) AS articles
        FROM fact_articles f
        JOIN dim_language l ON f.language_id = l.language_id
        WHERE l.language_code IN ({langs_filter})
        GROUP BY l.language_name
        ORDER BY articles DESC
    """)
    if not df_lang.empty:
        fig = px.pie(df_lang, values='articles', names='language_name',
                     hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig, use_container_width=True)

# --- Articles par pays ---
st.subheader("🌍 Articles par pays")
df_country = load_data("""
    SELECT s.country, COUNT(*) AS articles, 
           STRING_AGG(DISTINCT s.source_name, ', ') AS sources
    FROM fact_articles f
    JOIN dim_source s ON f.source_id = s.source_id
    GROUP BY s.country
    ORDER BY articles DESC
""")
if not df_country.empty:
    fig = px.bar(df_country, x='country', y='articles',
                 hover_data=['sources'], text='articles',
                 color='articles', color_continuous_scale='Blues')
    fig.update_traces(textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

# ================== ANALYSE DE SENTIMENT ==================

st.markdown("---")
st.subheader("😊 Analyse de sentiment des articles")

col_s1, col_s2, col_s3 = st.columns(3)

# Sentiment global
df_sentiment = load_data(f"""
    SELECT 
        sentiment_label,
        COUNT(*) AS articles,
        ROUND(AVG(sentiment_score)::NUMERIC, 3) AS avg_score
    FROM fact_articles f
    JOIN dim_source s ON f.source_id = s.source_id
    JOIN dim_language l ON f.language_id = l.language_id
    WHERE s.source_name IN ({sources_filter})
      AND l.language_code IN ({langs_filter})
    GROUP BY sentiment_label
    ORDER BY articles DESC
""")

if not df_sentiment.empty:
    with col_s1:
        # Camembert sentiment
        color_map = {'positive': '#10B981', 'negative': '#EF4444', 'neutral': '#6B7280'}
        fig = px.pie(df_sentiment, values='articles', names='sentiment_label',
                     hole=0.4,
                     color='sentiment_label',
                     color_discrete_map=color_map,
                     title="Distribution globale")
        st.plotly_chart(fig, use_container_width=True)

# Sentiment par source
df_sent_source = load_data(f"""
    SELECT 
        s.source_name,
        sentiment_label,
        COUNT(*) AS articles
    FROM fact_articles f
    JOIN dim_source s ON f.source_id = s.source_id
    JOIN dim_language l ON f.language_id = l.language_id
    WHERE s.source_name IN ({sources_filter})
      AND l.language_code IN ({langs_filter})
    GROUP BY s.source_name, sentiment_label
""")

if not df_sent_source.empty:
    with col_s2:
        fig = px.bar(df_sent_source, x='source_name', y='articles',
                     color='sentiment_label',
                     color_discrete_map={'positive': '#10B981', 'negative': '#EF4444', 'neutral': '#6B7280'},
                     title="Sentiment par source",
                     barmode='stack')
        st.plotly_chart(fig, use_container_width=True)

# Score moyen par source
df_score_source = load_data(f"""
    SELECT 
        s.source_name,
        ROUND(AVG(f.sentiment_score)::NUMERIC, 3) AS avg_sentiment
    FROM fact_articles f
    JOIN dim_source s ON f.source_id = s.source_id
    JOIN dim_language l ON f.language_id = l.language_id
    WHERE s.source_name IN ({sources_filter})
      AND l.language_code IN ({langs_filter})
    GROUP BY s.source_name
    ORDER BY avg_sentiment DESC
""")

if not df_score_source.empty:
    with col_s3:
        df_score_source['color'] = df_score_source['avg_sentiment'].apply(
            lambda x: '#10B981' if x > 0.1 else ('#EF4444' if x < -0.1 else '#6B7280')
        )
        fig = px.bar(df_score_source, x='avg_sentiment', y='source_name', orientation='h',
                     title="Score moyen par source",
                     color='avg_sentiment',
                     color_continuous_scale=['#EF4444', '#FFFFFF', '#10B981'],
                     range_color=[-1, 1])
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)

# Articles les plus négatifs et positifs
col_neg, col_pos = st.columns(2)

with col_neg:
    st.subheader("📉 Top 5 articles les plus négatifs")
    df_neg = load_data(f"""
        SELECT title, s.source_name AS source, sentiment_score, l.language_code AS lang
        FROM fact_articles f
        JOIN dim_source s ON f.source_id = s.source_id
        JOIN dim_language l ON f.language_id = l.language_id
        WHERE s.source_name IN ({sources_filter})
          AND l.language_code IN ({langs_filter})
        ORDER BY sentiment_score ASC
        LIMIT 5
    """)
    st.dataframe(df_neg, use_container_width=True, hide_index=True)

with col_pos:
    st.subheader("📈 Top 5 articles les plus positifs")
    df_pos = load_data(f"""
        SELECT title, s.source_name AS source, sentiment_score, l.language_code AS lang
        FROM fact_articles f
        JOIN dim_source s ON f.source_id = s.source_id
        JOIN dim_language l ON f.language_id = l.language_id
        WHERE s.source_name IN ({sources_filter})
          AND l.language_code IN ({langs_filter})
        ORDER BY sentiment_score DESC
        LIMIT 5
    """)
    st.dataframe(df_pos, use_container_width=True, hide_index=True)

# --- Top mots-clés ---
st.subheader("🔥 Mots-clés tendance")
df_kw = load_data("""
    SELECT keywords_str FROM fact_articles
    WHERE keywords_str IS NOT NULL AND keywords_str != ''
""")
if not df_kw.empty:
    all_kws = []
    for kws in df_kw['keywords_str']:
        all_kws.extend([k.strip().lower() for k in kws.split(',') if k.strip()])
    
    top_kws = pd.DataFrame(Counter(all_kws).most_common(20), columns=['Mot-clé', 'Fréquence'])
    fig = px.bar(top_kws, x='Fréquence', y='Mot-clé', orientation='h',
                 color='Fréquence', color_continuous_scale='Reds')
    fig.update_layout(yaxis={'categoryorder': 'total ascending'}, height=600)
    st.plotly_chart(fig, use_container_width=True)

# ================== TABLE DES ARTICLES ==================

st.markdown("---")
st.subheader("📑 Détail des articles")

df_articles = load_data(f"""
    SELECT 
        f.title,
        s.source_name AS source,
        l.language_code AS lang,
        f.category,
        f.author,
        f.word_count AS words,
        f.sentiment_label,
        f.sentiment_score,
        f.url
    FROM fact_articles f
    JOIN dim_source s ON f.source_id = s.source_id
    JOIN dim_language l ON f.language_id = l.language_id
    WHERE s.source_name IN ({sources_filter})
      AND l.language_code IN ({langs_filter})
    ORDER BY f.word_count DESC
""")
st.dataframe(df_articles, use_container_width=True, hide_index=True)

st.markdown("---")
st.caption(f"💡 Dashboard généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')} | "
           f"Architecture Big Data : MinIO + PostgreSQL + Streamlit")