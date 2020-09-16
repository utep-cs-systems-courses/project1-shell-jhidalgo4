#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 10 14:36:34 2020

@author: joaquin
"""
import os, sys

def main():
    while True:
        # if ps1 is in os enviorment, then set to custom ps1
        if 'PS1' in os.environ:
            os.write(1, (os.environ['PS1']).encode())
        else: #set to default
            os.write(1, ('$').encode())
            
        try:
            userInput = input()
        except EOFError as Eoferror:
            sys.exit(1)
        
        if len(userInput) == 0:
            continue
        if userInput.strip().lower() == 'exit':
            os.write(1, ('exiting....\n').encode())
            sys.exit(1)
            break
        
        args = userInput.split()
        if 'cd' in args[0]:
            try:
                os.chdir(args[1]) # change directory 
            except FileNotFoundError:
                os.write(1, ("%s: directory file not found...\n" %args[1] ).encode() )
                pass 
            
        #elif '|' in args:
            #pipe()
            
        #elif '>' in userInput:
            #do this action
            
        #elif '<' in userInput:  
            #do this action
            
        #else:
            #fork(args) 
        

if __name__ == "__main__":
    main()

