FROM python:3.10.8-bullseye

RUN mkdir /storage
RUN wget https://embeddings.net/embeddings/frWac_no_postag_no_phrase_500_cbow_cut100.bin -P /storage
RUN wget http://www.lexique.org/databases/Lexique383/Lexique383.tsv -P /storage

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY templates/ templates/
COPY app.py environ.py game.py .

ENV APP_STORAGE=/storage
ENV WORD2VEC_MODEL="frWac_no_postag_no_phrase_500_cbow_cut100.bin"
ENV LEXIQUE_CSV="Lexique383.tsv"

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
