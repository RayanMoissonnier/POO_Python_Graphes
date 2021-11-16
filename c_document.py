# -*- coding: utf-8 -*-
"""
Created on Tue Jan  5 15:49:42 2021

@author: nlebr
"""


class Document():
    
    #Constructeur de la classe Document
    def __init__(self, title,url,author,date,text):
        self.title = title
        self.url = url
        self.author = author
        self.date = date
        self.text = text

    # getters
    
    def get_author(self):
        return self.author

    def get_title(self):
        return self.title
    
    def get_date(self):
        return self.date
           
    def get_text(self):
        return self.text

    def __str__(self):
        return "Document " + self.getType() + " : " + self.title

    