#! /usr/bin/env python3
"""
#Created on Tue Sep 10 14:36:34 2020

#@author: joaquin
"""
import os, sys, time, re

def path(args):
        for dir in re.split(":", os.environ['PATH']): # try each directory in the path
                program = "%s/%s" % (dir, args[0])
                try:
                        os.execve(program, args, os.environ) # try to exec program
                except FileNotFoundError:             # ...expected
                        pass                              # ...fail quietly
        sys.exit(1)                 # terminate with error
        
        
def redirect(direction, userInput):
        userInput = userInput.split(direction)    #Split user input by direction sign
        if direction == '>':                      #If '>' redirect output into file
                os.close(1)
                sys.stdout = open(userInput[1].strip(), "w")  #open and set to write
                os.set_inheritable(1, True)
                path(userInput[0].split())
        else:
                os.close(0)                       #Redirect input 
                sys.stdin = open(userInput[1].strip(), 'r')   #open and set to read
                os.set_inheritable(0, True)
                path(userInput[0].split())
while True:
        #if ps1 is in os enviorment, then set to custom ps1
        if 'PS1' in os.environ:
                os.write(1, (os.environ['PS1']).encode() )
        else: #set to default
                os.write(1, ('$').encode() )
            
        try:
                userInput = input() #take input
        except EOFError:
                sys.exit(1)

        if userInput == "": # Empty input, will prompt again
                os.write(1, "User Input is length of 0, try again...\n".encode() )
                continue
                
        
        if 'exit' in userInput:
                os.write(1, "EXIT: goodbye...\n".encode() )
                sys.exit(0)
            
        # List of args as command line
        args = userInput.split()
        
        if 'cd' in args[0]:
                try:
                        os.chdir(args[1]) # change directory 
                except FileNotFoundError:
                        os.write(1, "FileNotFoundError: ".encode() )
                        os.write(1, args[1].encode() )
                        os.write(1, "\n".encode() )
                continue
            
        rc = os.fork()
        # os.write(1, "f: ".encode() )
        # os.write(1, str(os.getpid()).encode() )
        # os.write(1, "\n".encode() )
        
        #error
        if rc < 0:
                os.write(1, 'Error fork\n'.encode() )
                sys.exit(1) #error exit
            
        #success child fork
        elif rc == 0:         
                if "|" in args: # Piping command
                        pipe = userInput.split("|")  #cant split list, bug fixed
                        pipeLeft= pipe[0].split()
                        pipeRight = pipe[1].split()

                        pRead, pWrite = os.pipe()  # file descriptors pr, pw for reading and writing
                        
                        for fd in (pRead, pWrite):
                                os.set_inheritable(fd, True)
                                
                        pipeFork = os.fork()
                        # os.write(1, "pf: ".encode() )
                        # os.write(1, str(os.getpid()).encode() )
                        # os.write(1, "\n".encode() )
                        
                        
                        #Error - fork
                        if pipeFork < 0:
                                sys.exit(1)
                        
                        #child fork - success
                        if pipeFork == 0:
                                os.close(1) #close std-out so we can write into pipe
                                os.dup(pWrite)  #copies fd table for the old entry
                                os.set_inheritable(1, True)
                                for f in (pRead,pWrite):
                                        os.close(f)
                                path(pipeLeft)
                        
                        #parent fork
                        else:
                                os.close(0) # close the std-in 
                                os.dup(pRead) #put together 
                                os.set_inheritable(0, True)
                                for f in (pWrite,pRead):
                                        os.close(f) # close b/c we already put together
                                path(pipeRight)
                            
        
                if '&' in userInput: # To run in background
                        userInput = userInput.split('&')
                        userInput = userInput[0]
                        args = userInput.split()
                        
                if '>' in userInput:     #If > in input, send to
                                         #redirect method for output redirection
                        redirect('>', userInput)
                elif '<' in userInput:   #Input redirection
                        redirect('<', userInput)
                else:
                        if '/' in args[0]:  #If '/' in user input, try the given path
                                program = args[0]
                                try:
                                        os.execve(program, args, os.environ )
                                except FileNotFoundError:  #If not found, give error
                                        pass
                        else:
                                path(args)                 
                                
        #parent fork
        else:
                if not '&' in userInput:
                        # os.write(1, 'parent forking done..\n'.encode() )
                        os.wait()
                
                
