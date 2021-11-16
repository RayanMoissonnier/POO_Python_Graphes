# -*- coding: utf-8 -*-
"""
Created on Tue Jan  5 15:49:45 2021

@author: nlebr
"""

#Importation des librairies et des classes c_document et c_auteur
import c_author as au
import re
import pandas as pd
from nltk.corpus import stopwords
from pyvis.network import Network
import networkx as nx
import datetime 
import praw
import c_document as dc



class Corpus:
    
    #Constructeur de la classe Corpus
    def __init__(self,name):
        self.name = name
        self.collection = {}
        self.authors = {}
        self.id2doc = {}
        self.id2aut = {}
        self.ndoc = 0
        self.naut = 0
            
    #Fonction permettant d'ajouter des documents et des elements relatifs aux documents à l'objet Corpus 
    def add_doc(self, doc):
        self.collection[self.ndoc] = doc
        self.id2doc[self.ndoc] = doc.get_title()
        self.ndoc += 1
        aut_name = doc.get_author()
        aut = self.get_aut2id(aut_name)
        if aut is not None:
            self.authors[aut].add(doc)
        else:
            self.add_aut(aut_name,doc)
            
    #Fonction permettant d'ajouter des auteurs et des elements relatifs aux auteurs à l'objet Corpus  
    def add_aut(self, aut_name,doc):
        aut_temp = au.Author(aut_name)
        aut_temp.add(doc)
        self.authors[self.naut] = aut_temp
        self.id2aut[self.naut] = aut_name
        self.naut += 1

    #Fonction verifiant l'existance d'un auteur à partir de son nom
    def get_aut2id(self, author_name):
        aut2id = {v: k for k, v in self.id2aut.items()}
        id_aut = aut2id.get(author_name)
        return id_aut

    #Affichage informations Corpus
    def __str__(self):
        return "Corpus: " + self.name + ", Number of docs: "+ str(self.ndoc)+ ", Number of authors: "+ str(self.naut)
    
    #Fonction qui alimente le corpus avec un certain nombre de post (nb_post)
    def alimentation_corpus(self,nb_post):
        #Connexion a reddit
        reddit = praw.Reddit(client_id='u7waJDHmKt0Jcg', client_secret='wiBBETggffhKoAWfseX4uaEQiOY', user_agent='Reddit WebScraping')
        #Selection de "nb_post" publication sur le mot clé "Coronavirus"
        hot_posts = reddit.subreddit('Coronavirus').hot(limit=nb_post)
        i=0
        #Recuperation des données de tous les posts et insertion dans le Corpus (self)
        for post in hot_posts:
            datet = datetime.datetime.fromtimestamp(post.created)
            txt = post.title + ". "+ post.selftext
            txt = txt.replace('\n', ' ')
            txt = txt.replace('\r', ' ')
            doc = dc.Document(post.title,
                           post.url,
                           post.author_fullname,
                           datet,
                           txt)
            
            self.add_doc(doc)
            i+=1 
        
    #Fonction qui nettoie les documents du corpus sur le Coronavirus
    def nettoyer_texte(self):
        temp = []
        for i in range(0,self.ndoc):
            temp=(self.collection[i].text)
            #passage en minuscule
            temp = temp.lower()
            #regroupement des appelations du coronavirus
            temp = temp.replace('covid-19','covid')
            temp = temp.replace('coronavirus','covid')
            temp = temp.replace('rcovid','covid')
            #regroupement du mot "vaccine" avec son pluriel (mot très fréquent)
            temp = temp.replace('vaccines','vaccine')        
            #suppression des caractères spéciaux ainsi que les chiffres grâce à une expression regulière
            temp = re.sub('[^A-z -]', '',temp)
            temp = temp.replace('[',' ')
            temp = temp.replace(']',' ')
            #Transformation du texte du document en liste de mots
            temp = list(temp.split())
            #filtrage des stopword et des liens
            temp2=[w for w in temp if not w in stopwords.words('english') and "http" not in w and w not in ["-","--"]]
            #suppression des doublons au sein d'un document
            temp2 = list(set(temp2))
            #la liste de mot prend la place du texte dans le corpus
            self.collection[i].text = temp2
     
    #Fonction qui crée un dataframe ayant un format spéciale (pour la création de graphe)
    def formatage_data(self):
        #Initiatialisation d'un dataframe
        edge = pd.DataFrame(columns=['word1', 'word2'])
        n = 0
        #boucle permettant de relier tous les mots d'un même texte deux par deux
        for x in range(0,self.ndoc):
            #recupération de l'element text du corpus (liste de mot)
            c = self.collection[x].text
            for i in range(0,len(c)):
                #on utilise i au lieu de 0 dans le range pour pas avoir les liaisons de mots symétriques
                for j in range(i,len(c)):
                    if (i != j) :
                        #insertion dans le dataframe edge
                        edge.loc[n,'word1'] = c[i]
                        edge.loc[n,'word2'] = c[j]
                        n = n + 1
        #concaténation du dataframe permettant d'obtenir les poids de chaque liaisons de mots                
        resultat = edge.groupby(edge.columns.tolist(),as_index=False).size()
        #recuperation des index (word1 word2) dans l'objets series "resultat"
        namecol=resultat.index.tolist()
        word1=[]
        word2=[]
        for i in range (len(namecol)):
            word1.append(namecol[i][0])
            word2.append(namecol[i][1])
            
        #creation du dataframe final ayant le format souhaité
        data_word=pd.DataFrame(list(zip(word1,word2,resultat)),columns=["word1","word2","nb_lien"])
        #suppresion des liaisons ayant une pondération de 1 (jugée comme non représentative)
        temp= data_word[data_word["nb_lien"]<2].index.tolist()
        data_word = data_word.drop(temp)
        return data_word
     
    #fonction creant un graphe, en indique les mesures de centralité, l'enregistre et l'affiche sur un navigateur           
    def creation_graphe(self,data):
        #initialisation d un graphe avec la librarie networkx (pour les calculs de centralité)
        graphe = nx.from_pandas_edgelist(data, source="word1",target="word2", edge_attr="nb_lien")
        #calcul des mesures de centralité
        centralite = nx.degree_centrality(graphe)
        centralite_ind = list(centralite.keys())
        centralite_val = list(centralite.values())
        max_centralite = max(centralite_val)
        #recherche du mot central
        for i in range(len(graphe.nodes)):
            if centralite_val[i]== max_centralite:
                motcentral = centralite_ind[i]
        #creation du graphe
        word_network = Network(height = "800px",width="100%", bgcolor="#222222",font_color = "white",heading="Graphe des liens entre les mots d'un corpus portant sur le coronavirus (provenant de Reddit)")
        word_network.barnes_hut()
        #divise les données dans différente variables 
        word1 = data['word1']
        word2 = data['word2']
        poids = data['nb_lien']
        edge_data = zip(word1,word2,poids)
        #alimentation du graphe (word_networks) : sommets et aretes
        for i in edge_data: 
            key1 = i[0]
            key2 = i[1]
            w = i[2]
            word_network.add_node(key1, key1, title = key1)
            word_network.add_node(key2, key2, title = key2)
            word_network.add_edge(key1, key2 , value = w)         
        neighbor_map = word_network.get_adj_list()
        #ajouts du mot le plus central
        word_network.add_node(motcentral, size = 25)
        #ajout d'étiquettes sur les mots du graphe
        for node in word_network.nodes:
            id = node["id"] 
            #pour le mot central, on ajoute une phrase spécifique
            if id == motcentral: 
                node["title"] = "Mot ayant le degré de centralité le plus élevé<br>" 
                #affichage le degré de centralité du mot
                node['title'] += "Degres de centralité  : "+ str(centralite[id])+" <br> <br>"
                #affiche les mots ayant une liaison avec le mot
                node["title"] += "Voisins : <br>"+"<br>".join(neighbor_map[node["id"]])
                #ajustement de l'affichage du sommet en fonction de son importance dans le graphe
                node["value"] = len(neighbor_map[node["id"]])
            else :
                node['title'] = "Degres de centralité : "+ str(centralite[id])+" <br> <br>"
                node["title"] += "Voisins : <br>"+"<br>".join(neighbor_map[node["id"]])
                node["value"] = len(neighbor_map[node["id"]])
        #affiche le graphe et enregistre celui-ci dans le repertoire courant 
        word_network.show("word_links.html")

