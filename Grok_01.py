# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║   🌍 AGENT GÉOPOLITIQUE SAHEL                                               ║
# ║   Déploiement : share.streamlit.io                                          ║
# ║   Modèle      : llama-3.3-70b via Groq (gratuit, clé dans Secrets)         ║
# ║   Utilisateur : aucune configuration requise — tout est automatique         ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import pytz
import re

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="🌍 Agent Géopolitique Sahel",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════════════════
# CSS
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
  .stApp { background: #0e1117; color: #cdd6f4; }
  p, li, div { color: #cdd6f4; }

  .hero {
    background: linear-gradient(135deg, #11111b 0%, #1e1e2e 60%, #181825 100%);
    border-left: 5px solid #f38ba8;
    border-radius: 10px;
    padding: 24px 32px 20px;
    margin-bottom: 28px;
  }
  .hero h1 { color: #cba6f7; font-size: 2rem; margin: 0 0 6px; }
  .hero p  { color: #a6adc8; margin: 0; font-size: 0.93rem; }

  .bulletin {
    background: #181825;
    border: 1px solid #313244;
    border-radius: 10px;
    padding: 30px 36px;
    font-family: 'Georgia', serif;
    font-size: 0.97rem;
    line-height: 1.85;
    margin-top: 20px;
  }
  .bulletin-stamp {
    display: inline-block;
    background: #f38ba8;
    color: #11111b;
    font-weight: 800;
    font-size: 0.72rem;
    letter-spacing: .14em;
    text-transform: uppercase;
    border-radius: 4px;
    padding: 4px 12px;
    margin-bottom: 20px;
  }

  [data-testid="stSidebar"] { background: #11111b; border-right: 1px solid #1e1e2e; }
  [data-testid="metric-container"] {
    background: #1e1e2e; border-radius: 8px; padding: 14px;
    border: 1px solid #313244;
  }
  [data-testid="stExpander"] { background: #1e1e2e; border-radius: 8px; margin-bottom: 8px; }

  .stButton > button {
    background: #cba6f7 !important;
    color: #11111b !important;
    font-weight: 800 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 12px 28px !important;
    font-size: 1rem !important;
    width: 100%;
  }
  .stButton > button:hover { opacity: 0.88 !important; }
  .stButton > button:disabled { opacity: 0.4 !important; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════════════════════════
PARIS_TZ = pytz.timezone("Europe/Paris")
TARGET_HOUR = 7

REGIONS_DISPO = [
    "Afrique de l'Ouest & Sahel central",
    "Afrique Centrale",
    "Afrique de l'Est & Corne de l'Afrique",
    "Bassin du lac Tchad",
    "Interface Maghreb-Sahel",
]

SYSTEM_PROMPT = (
    "Tu es un analyste géopolitique senior spécialisé dans le Sahel et l'Afrique subsaharienne. "
    "Tu rédiges des bulletins de renseignement stratégique rigoureux, factuellement ancrés, "
    "en français professionnel. Tu croises les dimensions sécuritaires, diplomatiques, "
    "humanitaires et économiques. Tu classes les signaux : 🔴 CRITIQUE · 🟠 IMPORTANT · 🟡 À SURVEILLER. "
    "Style journalistique sobre, paragraphes développés, jamais de listes à puces."
)

USER_PROMPT = """Produis un bulletin géopolitique daté du {date} à 07h00 pour les zones : {regions}.

STRUCTURE EXACTE à respecter :

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌍 BULLETIN GÉOPOLITIQUE SAHEL · {date} · 07H00
Veille stratégique · Afrique subsaharienne
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CONTEXTE MACRO
[2 phrases de cadrage sur la dynamique régionale dominante]

──────────────────────────────────────────
SIGNAL 1 · 🔴 · [TITRE EN MAJUSCULES]
──────────────────────────────────────────
[Analyse de 150 mots : acteurs, faits, rapports de force, implications régionales]
Lecture stratégique : [2 phrases prospectives]

──────────────────────────────────────────
SIGNAL 2 · 🟠 · [TITRE]
──────────────────────────────────────────
[Même format]
Lecture stratégique : [...]

──────────────────────────────────────────
SIGNAL 3 · 🟠 · [TITRE]
──────────────────────────────────────────
[Même format]
Lecture stratégique : [...]

──────────────────────────────────────────
SIGNAL 4 · 🟡 · [TITRE]
──────────────────────────────────────────
[Même format]
Lecture stratégique : [...]

──────────────────────────────────────────
SIGNAL 5 · 🟡 · [TITRE]
──────────────────────────────────────────
[Même format]
Lecture stratégique : [...]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 SYNTHÈSE — VECTEURS DES 72 HEURES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[120 mots sur les dynamiques structurelles et événements à surveiller]

─ Sources : AFP, Reuters, RFI, Jeune Afrique, ACLED, ISS Africa, Crisis Group, ONU OCHA, IFRI ─

Longueur totale : environ {word_count} mots."""

# ═══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════════════════════
for k, v in {
    "bulletins": [],
    "regions": REGIONS_DISPO[:3],
    "word_count": 800,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ═══════════════════════════════════════════════════════════════════════════════
# GROQ CLIENT — clé lue depuis st.secrets (stockée dans Streamlit Cloud)
# ═══════════════════════════════════════════════════════════════════════════════
@st.cache_resource
def get_groq_client():
    return Groq(api_key=st.secrets["GROQ_API_KEY"])

# ═══════════════════════════════════════════════════════════════════════════════
# RENDU DU BULLETIN
# ═══════════════════════════════════════════════════════════════════════════════
def colorize(text: str) -> str:
    text = re.sub(r"(SIGNAL \d+\s*·\s*🔴[^\n]*)", r'<span style="color:#f38ba8;font-weight:700">\1</span>', text)
    text = re.sub(r"(SIGNAL \d+\s*·\s*🟠[^\n]*)", r'<span style="color:#fab387;font-weight:700">\1</span>', text)
    text = re.sub(r"(SIGNAL \d+\s*·\s*🟡[^\n]*)", r'<span style="color:#f9e2af;font-weight:700">\1</span>', text)
    text = re.sub(r"(🌍 BULLETIN[^\n]*)",          r'<span style="color:#89b4fa;font-size:1.05rem;font-weight:700">\1</span>', text)
    text = re.sub(r"(📊 SYNTHÈSE[^\n]*)",          r'<span style="color:#89b4fa;font-weight:700">\1</span>', text)
    text = re.sub(r"(Lecture stratégique\s*:[^\n]*)", r'<em style="color:#a6e3a1">\1</em>', text)
    text = re.sub(r"━+", r'<span style="color:#313244">━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</span>', text)
    text = re.sub(r"─{6,}", r'<span style="color:#313244">──────────────────────────────────────────</span>', text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    return text

_dl_counter = 0

def show_bulletin(b: dict):
    global _dl_counter
    _dl_counter += 1
    html = colorize(b["content"]).replace("\n", "<br>")
    st.markdown(
        f'<div class="bulletin">'
        f'<span class="bulletin-stamp">📡 Bulletin · {b["display_date"]} · {b["display_time"]}</span><br>'
        f'{html}'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.download_button(
        "⬇️ Télécharger (.txt)",
        data=b["content"],
        file_name=f"bulletin_sahel_{b['date']}.txt",
        mime="text/plain",
        key=f"dl_{_dl_counter}",
    )

# ═══════════════════════════════════════════════════════════════════════════════
# GÉNÉRATION — streaming natif avec st.write_stream
# ═══════════════════════════════════════════════════════════════════════════════
def generate():
    now      = datetime.now(PARIS_TZ)
    date_str = now.strftime("%d %B %Y")
    regions  = st.session_state.regions
    wc       = st.session_state.word_count

    client = get_groq_client()

    # Appel API Groq avec stream=True (syntaxe correcte du SDK Groq)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": USER_PROMPT.format(
                date=date_str,
                regions=", ".join(regions),
                word_count=wc,
            )},
        ],
        max_tokens=2800,
        temperature=0.7,
        stream=True,
    )

    # Collecte des chunks dans une liste partagée accessible après le stream
    collected = []

    # Générateur Python consommé par st.write_stream
    def stream_chunks():
        for chunk in response:
            delta = chunk.choices[0].delta.content
            if delta:
                collected.append(delta)
                yield delta

    # Affichage en streaming
    st.markdown("---")
    st.caption("🛰️ Génération en cours — le bulletin s'écrit en temps réel…")
    st.write_stream(stream_chunks())

    # Sauvegarde en session une fois le stream terminé
    full_text = "".join(collected)
    bulletin = {
        "date":         now.strftime("%Y-%m-%d"),
        "display_date": now.strftime("%d/%m/%Y"),
        "display_time": now.strftime("%H:%M"),
        "content":      full_text,
        "regions":      list(regions),
        "words":        len(full_text.split()),
    }
    st.session_state.bulletins = [
        b for b in st.session_state.bulletins if b["date"] != bulletin["date"]
    ]
    st.session_state.bulletins.insert(0, bulletin)
    return bulletin

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## ⚙️ Paramètres")

    st.markdown("### 📡 Régions surveillées")
    selected = []
    for r in REGIONS_DISPO:
        if st.checkbox(r, value=r in st.session_state.regions, key=f"chk_{r}"):
            selected.append(r)
    st.session_state.regions = selected

    st.markdown("---")
    st.markdown("### 📝 Longueur")
    st.session_state.word_count = st.select_slider(
        "Mots cibles",
        options=[500, 600, 700, 800, 900, 1000, 1200],
        value=st.session_state.word_count,
        label_visibility="collapsed",
    )
    st.caption(f"Cible : **{st.session_state.word_count} mots**")

    st.markdown("---")
    now_p   = datetime.now(PARIS_TZ)
    next_07 = now_p.replace(hour=TARGET_HOUR, minute=0, second=0, microsecond=0)
    if next_07 <= now_p:
        next_07 += timedelta(days=1)
    delta   = next_07 - now_p
    h, rem  = divmod(int(delta.total_seconds()), 3600)
    m_left  = rem // 60
    st.markdown(f"⏰ **Prochain 07h00** dans `{h}h{m_left:02d}`")

    st.markdown("---")
    n = len(st.session_state.bulletins)
    st.markdown(f"### 📚 Session : {n} bulletin{'s' if n!=1 else ''}")
    for b in st.session_state.bulletins:
        st.caption(f"• {b['display_date']} {b['display_time']} — {b['words']} mots")

# ═══════════════════════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
  <h1>🌍 Agent Géopolitique Sahel</h1>
  <p>Bulletins de renseignement stratégique · Afrique subsaharienne · Llama 3.3 70B via Groq · Streaming natif</p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# ONGLETS
# ═══════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3 = st.tabs(["📰 Générer", "📚 Historique", "ℹ️ Guide déploiement"])

# ─── ONGLET 1 : GÉNÉRER ──────────────────────────────────────────────────────
with tab1:
    bulletins = st.session_state.bulletins

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📄 Bulletins générés", len(bulletins))
    with col2:
        st.metric("🕐 Dernier bulletin", bulletins[0]["display_date"] if bulletins else "—")
    with col3:
        st.metric("🕖 Heure Paris", datetime.now(PARIS_TZ).strftime("%H:%M"))

    st.markdown("---")

    if not st.session_state.regions:
        st.warning("⚠️ Sélectionnez au moins une région dans le panneau latéral.")
    else:
        st.success(f"✅ Prêt · {', '.join(st.session_state.regions[:2])}{'…' if len(st.session_state.regions)>2 else ''} · {st.session_state.word_count} mots")

    col_btn, col_note = st.columns([1, 2])
    with col_btn:
        go = st.button(
            "⚡ Générer le bulletin",
            disabled=not st.session_state.regions,
        )
    with col_note:
        st.caption("Le texte s'affiche en temps réel grâce au streaming. Durée : 15 à 30 secondes.")

    if go:
        try:
            bulletin = generate()
            st.markdown("---")
            st.markdown("### 📰 Bulletin formaté")
            show_bulletin(bulletin)
        except Exception as e:
            st.error(f"❌ Erreur : {e}")

    elif bulletins:
        today = datetime.now(PARIS_TZ).strftime("%Y-%m-%d")
        if bulletins[0]["date"] == today:
            st.markdown("---")
            st.markdown("### 📰 Bulletin du jour")
            show_bulletin(bulletins[0])
        else:
            st.info("Aucun bulletin généré aujourd'hui. Cliquez sur **⚡ Générer le bulletin**.")

# ─── ONGLET 2 : HISTORIQUE ───────────────────────────────────────────────────
with tab2:
    st.markdown("### 📚 Bulletins de la session")
    if not st.session_state.bulletins:
        st.info("Aucun bulletin dans cette session.")
    else:
        for i, b in enumerate(st.session_state.bulletins):
            label = f"📄 {b['display_date']} · {b['display_time']} · {b['words']} mots · {', '.join(b['regions'][:2])}"
            with st.expander(label, expanded=(i == 0)):
                show_bulletin(b)

    if st.session_state.bulletins:
        st.markdown("---")
        if st.button("🗑️ Vider l'historique"):
            st.session_state.bulletins = []
            st.rerun()

# ─── ONGLET 3 : GUIDE ────────────────────────────────────────────────────────
with tab3:
    st.markdown("""
### 🚀 Déployer sur Streamlit Cloud en 10 minutes

Cette app est **100% autonome** : aucune clé API à saisir par l'utilisateur.
La clé Groq est stockée une seule fois dans les Secrets de Streamlit Cloud par vous (le déployeur).

---

#### Étape 1 — Clé Groq gratuite (2 min)

1. Allez sur [console.groq.com](https://console.groq.com)
2. Créez un compte (email ou GitHub)
3. **API Keys** → **Create API Key**
4. Copiez la clé `gsk_...`

> Groq est **entièrement gratuit** avec des quotas très généreux (14 400 requêtes/jour).
> Aucune carte bancaire requise.

---

#### Étape 2 — GitHub (3 min)

1. Créez un compte sur [github.com](https://github.com) si besoin
2. Cliquez **New repository** → nommez-le `sahel-agent` → **Private** → **Create**
3. Cliquez **Add file → Upload files**
4. Uploadez `app.py` et `requirements.txt`
5. Cliquez **Commit changes**

---

#### Étape 3 — Streamlit Cloud (3 min)

1. Allez sur [share.streamlit.io](https://share.streamlit.io)
2. **Sign in with GitHub**
3. **New app** → choisissez le repo `sahel-agent` → fichier `app.py`
4. Cliquez **Advanced settings** → **Secrets**
5. Collez exactement ceci :

```toml
GROQ_API_KEY = "gsk_votre_clé_ici"
```

6. Cliquez **Save** puis **Deploy**

→ L'app est en ligne en ~2 minutes à une URL publique ou privée.

---

#### Utilisation quotidienne

- Ouvrez l'URL de votre app chaque matin à 07h00
- Ajustez les régions dans le panneau latéral
- Cliquez **⚡ Générer le bulletin**
- Le texte s'affiche en streaming en temps réel
- Téléchargez en `.txt` si besoin

---

#### Architecture technique

| Composant | Détail |
|---|---|
| Modèle IA | Llama 3.3 70B (Meta) |
| Inférence | Groq Cloud (ultra-rapide, gratuit) |
| Streaming | `st.write_stream` natif Streamlit |
| Hébergement | Streamlit Community Cloud |
| Stockage | Session state (mémoire de session) |
| Config utilisateur | Aucune |

---

*Agent géopolitique Sahel · Llama 3.3 70B via Groq · 2026*
    """)
