import re
import feedparser
import nltk
from nltk.corpus import wordnet
from deep_translator import GoogleTranslator

nltk.download('wordnet')
nltk.download('omw-1.4')

# Lista di feed RSS
feeds = [
    "https://feeds.bbci.co.uk/news/rss.xml",
    "http://rss.cnn.com/rss/edition.rss",
    "http://feeds.reuters.com/Reuters/worldNews",
    "https://www.aljazeera.com/xml/rss/all.xml",
    "https://apnews.com/rss",
    "https://rss.dw.com/rdf/rss-en-all",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "https://feeds.washingtonpost.com/rss/world",
    "https://www.france24.com/en/rss",
    "https://feeds.npr.org/1004/rss.xml",
    "https://www.theguardian.com/world/rss",
    "https://feeds.feedburner.com/time/world",
    "https://www.repubblica.it/rss/homepage/rss2.0.xml",
    "https://xml.corriereobjects.it/rss/homepage.xml",
    "https://rss.ilsole24ore.com/rss/home.xml",
    "https://www.ansa.it/sito/ansait_rss.xml",
    "https://www.clarin.com/rss/",
    "https://elpais.com/rss/feed.html",
    "https://www.lemonde.fr/rss/en_continu.xml",
    # Puoi aggiungere altri feed qui...
]



# Funzione per ottenere sinonimi in inglese
def get_synonyms(word):
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name().replace("_", " "))
    return list(synonyms)

# Parola/frase principale
keyword = input("Inserisci una parola/frase: ").strip().lower()

# Traduzione della keyword in EN, FR, ES, DE
languages = ["en", "fr", "es", "de"]
translations = {}
for lang in languages:
    try:
        translations[lang] = GoogleTranslator(source='auto', target=lang).translate(keyword)
    except:
        translations[lang] = keyword

# Sinonimi per la versione inglese
english_synonyms = []
for word in translations.get("en", "").split():
    english_synonyms += get_synonyms(word)
english_synonyms = list(set(english_synonyms))

# Lista finale di keyword
keywords_translated_summary = [keyword]
keywords_original_text = list(translations.values()) + english_synonyms
keywords_original_text = [kw.lower() for kw in keywords_original_text]

print(f"Cerco articoli con keyword tradotta per summary: {keywords_translated_summary}")
print(f"Cerco articoli con keyword/sinonimi per titolo e summary originale: {keywords_original_text}\n")

for url in feeds:
    feed = feedparser.parse(url)
    entries = feed.entries or []
    if not entries:
        continue

    print(f"\n--- Notizie da: {url} ---\n")
    count = 0
    for entry in entries[:20]:
        title = entry.get("title", "")
        summary = entry.get("summary", "")
        description = entry.get("description", "")
        link = entry.get("link", "Nessun link")
        pub = entry.get("published", entry.get("updated", "Data non disponibile"))

        # Pulizia HTML da summary/description
        summary = re.sub(r"<[^>]+>", "", summary)
        description = re.sub(r"<[^>]+>", "", description)

        combined_text_original = (title + " " + summary + " " + description).lower()

        # Traduci il summary/description in italiano
        combined_summary_translated = title + " " + summary + " " + description
        try:
            combined_summary_translated = GoogleTranslator(source='auto', target='it').translate(combined_summary_translated)
        except:
            pass
        combined_summary_translated = combined_summary_translated.lower()

        # Controllo se la keyword originale è nel summary tradotto
        if any(kw in combined_summary_translated for kw in keywords_translated_summary) or \
           any(kw in combined_text_original for kw in keywords_original_text):
            count += 1
            print(f"{count}. {title}")
            print(f"   {pub}")
            print(f"   {link}")
            print(f"   {summary[:200]}...\n")

    if count == 0:
        print(" Nessuna notizia trovata con quella parola chiave.\n")
