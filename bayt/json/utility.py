# -*- coding: utf-8 -*-
"""
Created on Wed Oct 14 15:23:48 2020
"""

from pyodbc import connect

def Sfrogs_database_connect():
    """
    conncet Sfrogs Databse 
    """
    con1 = connect('Driver={SQL Server};'
              'Server= '
              'Database= '
              'uid= '
              'pwd= '
              'Trusted_Connection=no;')
    return con1


def Training_database_connect():
    """
    conncet Training Databse 
    """
    con = connect('Driver={SQL Server};'
                  'Server= '
                  'Database= '
                  'uid= '
                  'pwd= '
                  'Trusted_Connection=no;')
    return con
