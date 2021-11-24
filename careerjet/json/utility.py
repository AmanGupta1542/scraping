# -*- coding: utf-8 -*-
"""
Created on Thu Oct  7 12:14:47 2021

@author: demofrogs
"""

import pyodbc

def Sfrogs_database_connect():
    """
    conncet Sfrogs Databse 
    """
    con1 = pyodbc.connect('Driver={SQL Server};'
              'Server='
              'Database='
              'uid='
              'pwd='
              'Trusted_Connection=no;')
    return con1


def Training_database_connect():
    """
    conncet Training Databse 
    """
    con = pyodbc.connect('Driver={SQL Server};'
                  'Server= '
                  'Database= '
                  'uid= '
                  'pwd= '
                  'Trusted_Connection=no;')
    return con