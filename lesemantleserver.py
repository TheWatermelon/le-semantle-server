#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import csv
import json
import logging
from flask import Flask, request, render_template, make_response, flash, url_for, redirect
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from gensim.models import KeyedVectors


from environ import *
from game import Game


# configure the logger
logging.basicConfig(format='%(asctime)s - %(name)s::%(funcName)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# load the model
model = KeyedVectors.load_word2vec_format(WORD2VEC_MODEL, binary=True, unicode_errors="ignore")

# load the dictionary
csv_reader = csv.reader(open(LEXIQUE_CSV), delimiter='\t')
lexique = list(filter(lambda c: ((c[3] == 'NOM' or c[3] == 'ADJ' or c[3] == 'VER') and
                                    (c[4] == '' or c[4] == 'm') and
                                    (c[5] == '' or c[5] == 's') and
                                    (float(c[6]) >= 1.0) and
                                    (c[10] == '' or c[10][:3] == 'inf') and
                                    (c[0] in model.key_to_index)),
                        csv_reader))

game = Game(lexique, model)

app = Flask(__name__)

# Flask-WTF requires an encryption key - the string can be anything
app.config['SECRET_KEY'] = 'EncrYpt1onK3Y'

# Flask-Bootstrap requires this line
Bootstrap(app)

app.config["JSONIFY_PRETTYPRINT_REGULAR"] = False

if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
    game.start()


def convert_namedtuple_to_dict(nt):
    return dict(filter(lambda item: item[1] is not None, nt._asdict().items()))


class WordForm(FlaskForm):
    word = StringField('', validators=[DataRequired()], render_kw={'autofocus': True, 'style': '', 'class': 'form-control'})
    submit = SubmitField('Envoyer', render_kw={'class': 'btn btn-primary'})


def getScoreFrom(elem):
    return elem['score']


def addWordToList(word, list):
    if 'error' in word:
        return False
    for item in list:
        if word['word'] == item['word']:
            return False
    list.append(word)
    list[len(list)-1]['num']=len(list)
    return True


# controller
@app.route('/score', methods=['POST'])
def score():
    form = request.form

    result = game.score(form.get('word'))
    result_dict = convert_namedtuple_to_dict(result)

    return result_dict


@app.route('/nearby', methods=['GET'])
def nearby():
    result = game.nearby(request.args.get('word'))

    return result


@app.route('/stats', methods=['GET'])
def stats():
    return game.stats()


@app.route('/history', methods=['GET'])
def hist():
    return game.history


@app.route('/new', methods=['GET'])
def new_game():
    game.game_over()
    resp = make_response("")
    resp.set_cookie("current", "", max_age=0)
    resp.set_cookie("words", "", max_age=0)
    resp.set_cookie("message", "", max_age=0)
    resp.headers['location'] = url_for('main_page')
    return resp, 302


# vue
@app.route("/", methods=['GET', 'POST'])
def main_page():
    form = WordForm(request.form)
    message = request.cookies.get("message")
    word_score = request.cookies.get("current")
    words = []

    if request.cookies.get('words') is not None:
        words_string = request.cookies.get('words')
        words_string = words_string.replace("'", '"')
        words = json.loads(words_string)

    if request.method == 'POST':
        word_score = score()

        addWordToList(word_score, words)

        resp = make_response("")
        resp.set_cookie("current", f"{word_score}",max_age=3)
        resp.set_cookie("words", f"{words}")

        if 'error' in word_score:
            resp.set_cookie("message",word_score['error'],max_age=3)
        elif word_score['percentile'] == 1000:
            resp.set_cookie("message","Bravo ! Vous avez trouvé en "+str(len(words))+" coups ! <a href='/new'>Cliquez ici</a> pour obtenir un nouveau mot.")

        resp.headers['location'] = url_for('main_page')
        return resp, 302
        
    if words:
        words.sort(key=getScoreFrom, reverse=True)
    if word_score is not None:
        word_score = word_score.replace("'", '"')
        word_score = json.loads(word_score)

    resp = render_template('mainpage.html', form=form, words=words, current=word_score, msg=message)
    
    return resp
