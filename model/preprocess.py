from PyPDF2 import PdfReader
import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from dotenv import load_dotenv
from openai import OpenAI
import pdfplumber
import json
import openai
import os
from transformers import pipeline
import gensim
from gensim import corpora
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import ujson



class Preprocessor:
    def pdf_to_jsonl(self, file_path):

        title = ""
        content = ""

        reader = PdfReader(file_path)

        metadata = reader.metadata
        if metadata != None:
            title = metadata.get('/Title', 'Unknown Title')

            for page in reader.pages:
                content += page.extract_text() + "\n"

        
            json_data = {
                "prompt": f"{title}",
                "completion": content
            }

            

            return json_data
        else:
            return None

    def write_jsonl_file(self, output_file, json_data):
        output_path = os.path.splitext(output_file.replace("dataset", "new_ds"))[0] + ".jsonl"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(json_data) + "\n")

    def combine_jsonl_files(self, input_directory, output_file):
        with open(output_file, "w", encoding="utf-8") as outfile:
            for filename in os.listdir(input_directory):
                if filename.endswith(".jsonl"):
                    file_path = os.path.join(input_directory, filename)
                    
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as infile:
                        for line in infile:
                            outfile.write(line)


    def jsonl_generate(self, directory):
        files = os.listdir(directory)

        for file in files:
            if self.pdf_to_jsonl(os.path.join(directory, file)) != None and os.path.exists(f"new_ds/{os.path.splitext(file)[0]}"+".jsonl") == False:
                try:
                    self.write_jsonl_file(f"new_ds/{os.path.splitext(file)[0]}"+".jsonl", self.pdf_to_jsonl(os.path.join(directory, file)))
                except:
                    pass
        
        self.combine_jsonl_files("new_ds", "pdf_contents.jsonl")
    
    def generate_topics_jsonl(self, file_path):
        stop_words = set(stopwords.words("english"))
        
        data = []

        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    tokens = [word.lower() for word in word_tokenize(text) if word.isalnum() and word.lower() not in stop_words]
                    
                    dictionary = corpora.Dictionary([tokens])
                    corpus = [dictionary.doc2bow(tokens)]

                    lda_model = gensim.models.LdaModel(corpus, num_topics=3, id2word=dictionary, passes=10)

                    topic_probs = lda_model.get_document_topics(corpus[0])
                    dominant_topic_id, dominant_weight = max(topic_probs, key=lambda x: x[1])
                    dominant_topic_words = lda_model.show_topic(dominant_topic_id, topn=1)
                    dominant_word = dominant_topic_words[0][0] 

                    entry = {
                        "prompt": f"{dominant_word}",
                        "completion": text.strip()
                    }
                    data.append(entry)


        with open(os.path.splitext(file_path.replace("dataset", "new_ds"))[0] + ".jsonl", "w") as f:
            for entry in data:
                f.write(json.dumps(entry) + "\n")

def generate_topics_jsonl_for_all(self):
    files = os.listdir("dataset")

    for file in files:
        self.generate_topics_jsonl(os.path.join("dataset", file))


class Parser:
    def get_products(self):
        driver = webdriver.Firefox()

        driver.get("https://gymbeam.com/protein")

        j = 0
        tabs = []
        while True:
            i = 0
            j += 1

            try:
                tabs.append(driver.find_element(By.CSS_SELECTOR, f".sidebar-navigation > ul:nth-child(1) > li:nth-child(1) > ul:nth-child(3) > li:nth-child({j}) > a:nth-child(1)").get_property("href"))
            except Exception:
                break


        entities = []

        for tab in tabs:
            driver.get(tab)

            i = 0
            while True:
                i += 1
                try:
                    myElem = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, f"/html/body/div[4]/main/div[2]/div[1]/div[4]/div[3]/ol/li[{i}]/div/a")))
                    entities.append(myElem.get_property("href"))
                except Exception:
                    break

        json = []

        for entity in entities:
            driver.get(entity)

            try:
                myElem = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div[3]/div[2]/div[1]/div[1]/h1")))
                desc = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div[3]/div[2]/div[1]/div[3]/span/p")))

                json.append({"name": myElem.text, "description": desc.text})
            except Exception:
                continue

        print(json)
        with open("result.json", 'w') as fw:
            ujson.dump(json, fw)