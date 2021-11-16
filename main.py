# -*- coding: utf-8 -*-
"""
Created on Tue Jan  5 15:46:20 2021

@author: nlebr
"""

#changement du repertoire courant(ne pas executer ligne par ligne sinon __file__ ne marchera pas)
import os

os.chdir(os.path.dirname(__file__))


 #importation de la classe c_corpus
import c_corpus as co


#creation du corpus sur le corona depuis reddit

corpus = co.Corpus("Corona")

corpus.alimentation_corpus(nb_post=200)
#nettoyage des textes des documents du corpus
corpus.nettoyer_texte()

#liaison entre les mots des documents
data_word = corpus.formatage_data()

#création du graphe/affichage du graphe et enregistrement dans le répertoire courant
corpus.creation_graphe(data_word)














































