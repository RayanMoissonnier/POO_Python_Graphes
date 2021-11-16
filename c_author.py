# -*- coding: utf-8 -*-
"""
Created on Tue Jan  5 15:49:45 2021

@author: nlebr
"""


class Author():
    
    #Constructeur de la classe Auteur    
    def __init__(self,name):
      self.name = name
      self.production = {}
      self.ndoc = 0

    #Ajout d'auteur
    def add(self, doc):
      self.production[self.ndoc] = doc
      self.ndoc += 1

    #Affichage
    def __str__(self):
      return "Auteur: " + str(self.name) + ", Number of docs: "+ str(self.ndoc)+", production : " + str(self.production)
