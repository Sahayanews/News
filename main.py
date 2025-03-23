import streamlit as st
import requests
import json
from textblob import TextBlob
from bs4 import BeautifulSoup
from gtts import gTTS
import os
from deep_translator import GoogleTranslator

def fetch_news(company):
    url = f"https://www.bing.com/news/search?q={company}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    articles = []
    for item in soup.find_all("a", {"class": "title"}, limit=10):  # Increased limit to 10
        title = item.get_text()
        link = item["href"]
        articles.append({"title": title, "link": link})
    
    return articles

def analyze_sentiment(text):
    analysis = TextBlob(text)
    if analysis.sentiment.polarity > 0:
        return "Positive"
    elif analysis.sentiment.polarity < 0:
        return "Negative"
    else:
        return "Neutral"

def generate_hindi_audio(text):
    tts = gTTS(text=text, lang='hi')
    audio_file = "title_audio.mp3"
    tts.save(audio_file)
    return audio_file

def wrap_text(text, width=80):
    words = text.split()
    lines = []
    while words:
        line = []
        while words and sum(len(word) for word in line) + len(line) - 1 < width:
            line.append(words.pop(0))
        lines.append(" ".join(line))
    return "\n".join(lines)

def main():
    st.title("News Sonic: News Summarization and Text-to-Speech App")
    company = st.text_input("Enter Company Name:")
    if st.button("Analyze"):
        articles = fetch_news(company)
        if not articles:
            st.write("No news articles found.")
            return
        
        report = {"Company": company, "Articles": []}
        sentiment_counts = {"Positive": 0, "Negative": 0, "Neutral": 0}
        
        # Process first article separately for audio playback
        if articles:
            first_article = articles[0]
            translated_title = GoogleTranslator(source='auto', target='hi').translate(first_article["title"])
            wrapped_title = wrap_text(translated_title, width=40)  # Wrap text to 40 characters per line
            audio_file = generate_hindi_audio(wrapped_title)
            st.audio(audio_file)
        
        for article in articles:
            sentiment = analyze_sentiment(article["title"])
            sentiment_counts[sentiment] += 1
            wrapped_title = wrap_text(article["title"], width=80)  # Wrap text to 80 characters per line
            report["Articles"].append({
                "Title": wrapped_title,
                "Sentiment": sentiment,
                "Link": article["link"]
            })
        
        report["Sentiment Distribution"] = sentiment_counts
        
        # Coverage Differences and Impact Analysis
        if len(articles) > 1:
            comparison = []
            comparison.append({
                "Comparison": f"Article 1 highlights {articles[0]['title']}, while Article 2 discusses {articles[1]['title']}",
                "Impact": "The first article may boost confidence, while the second could highlight risks or challenges."
            })
            report["Coverage Differences"] = comparison
        
        st.json(report)

if __name__ == "__main__":
    main()