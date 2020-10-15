#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 10 14:36:34 2020

@author: joaquin
"""
import os, sys, re

###HELP - recorded class
# 51:13
#https://web.microsoftstream.com/video/c29a9a52-ca3d-4f20-b968-c05cdaefbbdc


def redirect(symbol, args):
    indexOfSymbol = args.index(symbol)
    leftArg = args[:indexOfSymbol] 
    rightArg = args[indexOfSymbol + 1:] 

    if symbol == '>':  #send left side to right side
        # os.write(1, rightArg[0].encode() )
        os.close(1)   #prepare to change output, instead of sending to stdout
        sys.stdout = open(rightArg[0], 'w' )  #write
        os.set_inheritable(1, True)
        sendToPath(leftArg )  #send the left side
    else:
        # os.write(1, leftArg[0].encode() )
        os.close(0)  #prepare to read-in
        sys.stdin = open(rightArg[0], 'r')
        os.set_inheritable(0, True)
        sendToPath(leftArg )  #send the left side

def sendToPath(args):
    print('new new')
    for dir in re.split(":", os.environ['PATH']): # try each directory in path
        program = "%s/%s" % (dir, args[0])
        try:
            os.execve(program, args, os.environ) # try to exec program            
        except FileNotFoundError:             # ...expected
            pass                           # ...fail quietly 
    # os.write(2, ("Could not exec %s\n" % args[0]).encode() )
    sys.exit(1)                    

while True:
    #if ps1 is in os enviorment, then set to custom ps1
    if 'PS1' in os.environ:
        os.write(1, (os.environ['PS1']).encode() )
    else: #set to default
        os.write(1, ('$').encode() )
                
    #Get user input
    try:
        userInput = os.read(0, 128) #read 128 bytes from fd 0
        # os.write(1, userInput)     #echo
    except EOFError as Eoferror:
        print(Eoferror)
        os.write(1, 'did not read any data before reading of input stream... exit 1'.encode() )
        sys.exit(1)
    
    # userInput = uInput.decode()
    userInput = userInput.decode().split()
    
    if len(userInput) == 0:
        os.write(1, "User Input is length of 0, try again...\n".encode() )
        continue
    
    if 'exit' in userInput:
        os.write(1, "EXIT: goodbye...\n".encode() )
        sys.exit(0)
        
    if 'cd' in userInput:
        indexOfCd = userInput.index('cd')
        try:
            os.chdir( userInput[indexOfCd+1] )
        except FileNotFoundError:
            os.write(1, "Could not change file directory\n".encode() )
            pass
        continue
    
    # pPID = os.getpid()
    rc = os.fork()
    
    #error - fork
    if rc< 0:
        os.write(1, 'Error fork\n'.encode() )
        sys.exit(1) #error exit
    
    #child - success fork
    elif rc ==0:
        
        if '|' in userInput:
            indexOfPipe = userInput.index('|')
            pipe1 = userInput[:indexOfPipe]
            pipe2 = userInput[indexOfPipe+1:]
            
            pr, pw = os.pipe() #returns fd for read and write
            
            #obtain the file descriptors for the new pipes being done and set inhertiable to true
            for fd in (pr,pw):
                os.set_inheritable(fd, True)
            
            pipeFork = os.fork()
            
            #Error - fork
            if pipeFork < 0:
                sys.exit(1)
            
            #child fork - success
            if pipeFork == 0:
                os.close(1) #close std-out so we can write into pipe
                #connects the cuurent pipe to pw
                os.dup(pw)  #copies fd table for the old entry
                os.set_inheritable(1, True)
                for f in (pr,pw):
                    os.close(f)
                sendToPath(pipe1 )
            
            #parent fork
            else:
                os.close(0) # close the std-in 
                os.dup(pr) #put together the pipe with pr
                os.set_inheritable(0, True)
                for f in (pw,pr):
                    os.close(f) # close b/c we already put together
                sendToPath(pipe2)
                
        if '&' in userInput:
            indexOfAmber = userInput.index('&')
            arg = userInput[:indexOfAmber ]
        
        if '>' in userInput:
            redirect('>', userInput)
            
        if '<' in userInput:
            redirect('<', userInput)
            
        else:
            if '/' in userInput[0]:
                dirProg = userInput[0]
                try:
                    os.execve(dirProg, userInput, os.environ)
                except FileNotFoundError:
                    pass
            else:
                sendToPath(userInput)
            
    #parent fork
    else:
        if not '&' in userInput:
            # os.write(1, 'parent forking..\n'.encode() )
            os.wait()

########################################

    
