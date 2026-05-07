"""
Utilitaires NLP pour le nettoyage et l'enrichissement des articles.
"""
import re
import string
from langdetect import detect, LangDetectException
from sklearn.feature_extraction.text import TfidfVectorizer
from loguru import logger


# Stop words multilingues (mots à ignorer dans l'extraction)
STOPWORDS_FR = {
    'le', 'la', 'les', 'un', 'une', 'des', 'de', 'du', 'et', 'à', 'a', 'au', 'aux',
    'ce', 'cette', 'ces', 'son', 'sa', 'ses', 'leur', 'leurs', 'pour', 'par', 'sur',
    'dans', 'avec', 'sans', 'mais', 'ou', 'où', 'donc', 'car', 'ne', 'pas', 'plus',
    'qui', 'que', 'quoi', 'dont', 'est', 'sont', 'était', 'être', 'avoir', 'fait',
    'tout', 'tous', 'toute', 'toutes', 'aussi', 'comme', 'si', 'leur', 'nous', 'vous',
    'ils', 'elles', 'on', 'son', 'mon', 'ton', 'ma', 'ta', 'sa', 'cette', 'ce',
    'lors', 'depuis', 'entre', 'vers', 'chez', 'jusqu', 'alors', 'ainsi', 'encore',
    'déjà', 'très', 'bien', 'aussi', 'même', 'ans', 'jour', 'jours', 'an'
}

STOPWORDS_EN = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of',
    'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
    'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
    'what', 'which', 'who', 'when', 'where', 'why', 'how', 'all', 'each', 'every',
    'both', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'not', 'only',
    'own', 'same', 'so', 'than', 'too', 'very', 'can', 'just', 'said', 'says'
}

STOPWORDS_AR = {
    'في', 'من', 'إلى', 'على', 'عن', 'مع', 'هذا', 'هذه', 'ذلك', 'تلك',
    'التي', 'الذي', 'الذين', 'و', 'أن', 'إن', 'كان', 'كانت', 'يكون',
    'لم', 'لا', 'ما', 'هل', 'قد', 'ثم', 'أو', 'بل', 'بعد', 'قبل',
    'كل', 'بعض', 'غير', 'حتى', 'منذ', 'لكن', 'إذا', 'لو'
}


def clean_html(text: str) -> str:
    """Supprime les balises HTML résiduelles et les caractères invisibles."""
    if not text:
        return ""
    # Supprimer balises HTML
    text = re.sub(r'<[^>]+>', '', text)
    # Supprimer entités HTML (&nbsp;, &amp;, etc.)
    text = re.sub(r'&[a-zA-Z]+;', ' ', text)
    text = re.sub(r'&#\d+;', ' ', text)
    # Espaces multiples
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def normalize_text(text: str) -> str:
    """Normalise le texte : minuscules, suppression accents inutiles."""
    if not text:
        return ""
    # Garder la casse originale mais nettoyer les espaces
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def detect_language(text: str) -> str:
    """Détecte la langue du texte. Retourne 'fr', 'en', 'ar', ou 'unknown'."""
    if not text or len(text) < 20:
        return "unknown"
    try:
        # Prendre les 500 premiers caractères pour la détection
        sample = text[:500]
        lang = detect(sample)
        return lang
    except LangDetectException:
        return "unknown"


def extract_keywords(text: str, language: str = "fr", top_n: int = 10) -> list:
    """
    Extrait les top_n mots-clés via TF-IDF.
    Retourne une liste de (mot, score).
    """
    if not text or len(text) < 50:
        return []

    # Choisir les stopwords selon la langue
    if language == "fr":
        stopwords = STOPWORDS_FR
    elif language == "en":
        stopwords = STOPWORDS_EN
    elif language == "ar":
        stopwords = STOPWORDS_AR
    else:
        stopwords = set()

    try:
        # Vectoriseur TF-IDF
        vectorizer = TfidfVectorizer(
            stop_words=list(stopwords),
            max_features=top_n * 3,
            ngram_range=(1, 2),  # mots seuls + bigrammes
            min_df=1,
            token_pattern=r'\b[a-zA-ZÀ-ÿ\u0600-\u06FF]{3,}\b'  # mots latins + arabe, min 3 chars
        )
        tfidf_matrix = vectorizer.fit_transform([text])
        feature_names = vectorizer.get_feature_names_out()
        scores = tfidf_matrix.toarray()[0]

        # Trier par score décroissant
        keyword_scores = sorted(
            zip(feature_names, scores),
            key=lambda x: x[1],
            reverse=True
        )[:top_n]

        # Retourner liste de mots (sans les scores)
        return [kw for kw, score in keyword_scores if score > 0]

    except Exception as e:
        logger.warning(f"Erreur extraction mots-clés : {e}")
        return []


def compute_text_stats(text: str) -> dict:
    """Calcule des statistiques sur le texte."""
    if not text:
        return {"word_count": 0, "char_count": 0, "sentence_count": 0}
    
    words = text.split()
    sentences = re.split(r'[.!?]+', text)
    
    return {
        "word_count": len(words),
        "char_count": len(text),
        "sentence_count": len([s for s in sentences if s.strip()])
    }


def is_valid_article(article: dict, min_words: int = 30) -> bool:
    """Vérifie si un article a un contenu suffisant pour être traité."""
    content = article.get('content', '')
    title = article.get('title', '')
    
    if not title or title == "Sans titre":
        return False
    if not content or len(content.split()) < min_words:
        return False
    return True

# ============================================================
# SENTIMENT ANALYSIS (Approche lexicale multilingue)
# ============================================================

# Lexiques de mots positifs/négatifs (FR/EN/AR)
POSITIVE_WORDS = {
    'fr': {
        'excellent', 'magnifique', 'formidable', 'fantastique', 'merveilleux',
        'succès', 'réussir', 'gagner', 'victoire', 'progrès', 'amélioration',
        'positif', 'bénéfique', 'avantage', 'opportunité', 'croissance',
        'innovation', 'découverte', 'célébration', 'félicitations', 'paix',
        'accord', 'soutien', 'encourager', 'récompense', 'développement',
        'prospérité', 'espoir', 'optimisme', 'amélioration', 'collaboration'
    },
    'en': {
        'excellent', 'wonderful', 'fantastic', 'amazing', 'great', 'success',
        'win', 'victory', 'progress', 'improve', 'positive', 'benefit',
        'advantage', 'opportunity', 'growth', 'innovation', 'discovery',
        'celebrate', 'achievement', 'peace', 'agreement', 'support',
        'encourage', 'reward', 'development', 'prosperity', 'hope',
        'optimism', 'collaboration', 'breakthrough', 'praise', 'happy'
    },
    'ar': {
        'ممتاز', 'رائع', 'نجاح', 'فوز', 'انتصار', 'تقدم', 'تحسن', 'إيجابي',
        'فائدة', 'فرصة', 'نمو', 'ابتكار', 'اكتشاف', 'احتفال', 'سلام', 'اتفاق',
        'دعم', 'تشجيع', 'تطوير', 'ازدهار', 'أمل', 'تعاون', 'سعادة', 'فرحة'
    }
}

NEGATIVE_WORDS = {
    'fr': {
        'mort', 'mourir', 'tué', 'tuer', 'guerre', 'conflit', 'crise', 'attaque',
        'attentat', 'tragédie', 'catastrophe', 'désastre', 'pire', 'terrible',
        'horrible', 'échec', 'échouer', 'perdre', 'défaite', 'problème',
        'danger', 'menace', 'violence', 'destruction', 'ruine', 'pauvreté',
        'famine', 'maladie', 'pandémie', 'effondrement', 'récession', 'chômage',
        'controverse', 'scandale', 'accuser', 'condamner', 'arrêter', 'blesser',
        'victime', 'urgence', 'inquiétant', 'critique', 'protester'
    },
    'en': {
        'death', 'die', 'killed', 'kill', 'war', 'conflict', 'crisis', 'attack',
        'tragedy', 'disaster', 'worst', 'terrible', 'horrible', 'failure',
        'fail', 'lose', 'defeat', 'problem', 'danger', 'threat', 'violence',
        'destruction', 'poverty', 'famine', 'disease', 'pandemic', 'collapse',
        'recession', 'unemployment', 'controversy', 'scandal', 'accuse',
        'condemn', 'arrest', 'injured', 'victim', 'emergency', 'concerning',
        'critical', 'protest', 'fear', 'angry', 'sad'
    },
    'ar': {
        'موت', 'قتل', 'حرب', 'صراع', 'أزمة', 'هجوم', 'مأساة', 'كارثة', 'فشل',
        'خسارة', 'هزيمة', 'مشكلة', 'خطر', 'تهديد', 'عنف', 'دمار', 'فقر',
        'مجاعة', 'مرض', 'وباء', 'انهيار', 'ركود', 'بطالة', 'فضيحة', 'اعتقال',
        'إصابة', 'ضحية', 'طوارئ', 'احتجاج', 'خوف', 'حزن'
    }
}


def analyze_sentiment(text: str, language: str = "fr") -> dict:
    """
    Analyse le sentiment d'un texte avec une approche lexicale.
    Retourne un score entre -1 (très négatif) et +1 (très positif).
    TOUJOURS retourne un dict valide (fallback neutre si erreur).
    
    Returns:
        dict avec 'score' (float), 'label' (str), 'positive_count', 'negative_count'
    """
    try:
        # Défaut: texte vide ou invalide
        if not text or not isinstance(text, str):
            return {'score': 0.0, 'label': 'neutral', 'positive_count': 0, 'negative_count': 0}

        # Choisir le lexique selon la langue
        pos_words = POSITIVE_WORDS.get(language, POSITIVE_WORDS['en'])
        neg_words = NEGATIVE_WORDS.get(language, NEGATIVE_WORDS['en'])

        # Tokenizer simple en gardant les caractères spéciaux (arabe, accents)
        text_lower = text.lower()
        words = re.findall(r'\b[\w\u0600-\u06FF]+\b', text_lower)

        pos_count = sum(1 for w in words if w in pos_words)
        neg_count = sum(1 for w in words if w in neg_words)

        total_emotional = pos_count + neg_count
        if total_emotional == 0:
            score = 0.0
            label = 'neutral'
        else:
            # Score normalisé entre -1 et +1
            score = (pos_count - neg_count) / total_emotional
            # Clamp score entre -1 et +1 (sécurité)
            score = max(-1.0, min(1.0, score))
            
            if score > 0.2:
                label = 'positive'
            elif score < -0.2:
                label = 'negative'
            else:
                label = 'neutral'

        return {
            'score': round(score, 3),
            'label': label,
            'positive_count': pos_count,
            'negative_count': neg_count,
        }
    
    except Exception as e:
        # Fallback absolu en cas d'erreur
        logger.warning(f"Sentiment analysis exception: {e} - Using neutral fallback")
        return {'score': 0.0, 'label': 'neutral', 'positive_count': 0, 'negative_count': 0}


# ===== TEST =====
if __name__ == "__main__":
    sample_fr = """
    Le gouvernement français a annoncé aujourd'hui une nouvelle réforme 
    économique majeure visant à stimuler la croissance et à réduire le chômage.
    Cette réforme inclut des mesures fiscales et des investissements dans 
    les infrastructures et les technologies vertes.
    """
    
    print("=== Test détection de langue ===")
    print(f"Langue : {detect_language(sample_fr)}")
    
    print("\n=== Test extraction mots-clés ===")
    keywords = extract_keywords(sample_fr, language="fr", top_n=5)
    print(f"Mots-clés : {keywords}")
    
    print("\n=== Test statistiques ===")
    print(compute_text_stats(sample_fr))

    print("\n=== Test sentiment analysis ===")
    sample_negative = "La guerre en Iran continue avec des morts et des conflits violents."
    sample_positive = "Le développement économique apporte de la prospérité et de la croissance."
    print(f"Sentiment négatif : {analyze_sentiment(sample_negative, 'fr')}")
    print(f"Sentiment positif : {analyze_sentiment(sample_positive, 'fr')}")