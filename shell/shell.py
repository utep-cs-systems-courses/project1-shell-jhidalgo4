#! /usr/bin/env python3
"""
#Created on Tue Sep 10 14:36:34 2020

#@author: joaquin
"""
import os, sys, re
homedir = os.path.expanduser('~')


def execute(args):
    if "/" in args[0]:
        try:
            os.execve(args[0], args, os.environ)
        except FileNotFoundError:
            pass
        
    #redirection
    elif ">" in args:
        redirect(">", args)
        
    elif "<" in args:
        redirect("<", args)
        
    #execute
    else:
        for dir in re.split(":", os.environ['PATH']):
            program = "%s/%s" % (dir, args[0] )
            try:
                os.execve(program, args, os.environ)
            except FileNotFoundError:
                pass
    os.write(2, 'Couldnt execute\n'.encode() )
    sys.exit(1)


def redirect(symbol, args):
    if ">" == symbol:
        os.close(1) #close std-out so we can write into pipe
        indexOfRedirect = args.index(">")
        os.open(args[indexOfRedirect + 1], os.O_CREAT, os.O_WRONLY) #opens files with set flags
        os.set_inheritable(1, True)
        args.remove(args[indexOfRedirect + 1])
        args.remove(">") #remove symbol
    else:
        os.close(0)# close the std-in 
        indexOfRedirect = args.index("<")
        os.open(args[indexOfRedirect + 1], os.O_RDONLY) #opens files with set flags
        os.set_inheritable(0, True)
        args.remove(args[indexOfRedirect + 1])
        args.remove("<") #remove symbol
    
    execute(args) #execute
    os.write(2, 'Couldnt find command\n'.encode() )
    sys.exit(1)                    # ...fail quietly 
   

def handleCommand(args):
    if len(args) == 0:
        return
        
    if "cd" == args[0]:
        try:
            #user types just 'cd'
            if len(args) == 1:
                os.chdir(homedir) 
            else:
                os.chdir(args[1])
                
        except FileNotFoundError:
              os.write(1, 'Directory Not Found: '.encode() )
              os.write(1, args[1].encode() )
              os.write(1, '\n'.encode() )
              
    #Piping
    elif "|" in args:
        indexOfPipe = args.index('|')
        pipeLeft = args[: indexOfPipe]
        pipeRight = args[indexOfPipe + 1 :]
        
        pRead, pWrite = os.pipe() # file descriptors for reading and writing
        pipeFork = os.fork()
        
        #error - fork
        if pipeFork < 0:
            os.write(2, 'Error fork\n'.encode() )
            sys.exit(1) #error exit
            
        #child - success fork
        elif pipeFork ==0:
            os.close(1) #close std-out so we can write into pipe
            os.dup(pWrite)  #copies fd table for the old entry
            os.set_inheritable(1, True)
            for f in (pRead, pWrite):
                os.close(f)
                
            # os.write(2, 'pipeLeft'.encode() )
            execute(pipeLeft)
            sys.exit(1)
            
        #parent fork
        else:
            os.close(0) # close the std-in 
            os.dup(pRead) #put together the pipe with pRead
            os.set_inheritable(0, True)
            for f in (pRead, pWrite):
                os.close(f) # close b/c we already put together
            
            #handles multiple pipes
            if '|' in pipeRight:
                handleCommand(pipeRight)
                
            execute(pipeRight)
            # os.write(2, 'pipeRight'.encode() )
            sys.exit(1)

        
    else:
        #fork
        rc = os.fork()
        isAmpersand = False #dont assume
        
        if "&" in args:
            isAmpersand = True
            args.remove('&')
            
        #error - fork
        if rc< 0:
            os.write(1, 'Error fork\n'.encode() )
            sys.exit(1) #error exit
            
        #child - success fork
        elif rc ==0:
            execute(args)
            sys.exit(0)
            
        #parent fork
        else:
            if not isAmpersand:
                os.wait()
                

            
while True:
    #display prompt 
    if 'PS1' in os.environ:
        os.write(1, (os.environ['PS1']).encode() )
    else: 
        os.write(1, ('$').encode() )

    try:
        #Get user input
        userInput = os.read(0, 1024) 
        # os.write(1, userInput)       #echo
        
        if len(userInput) == 0:
            break
        
        userInput = userInput.decode().split("\n") #Splits be new line
        
        #Checks for EXIT
        if userInput[0].lower() == "exit":
            os.write(1, 'EXIT: goodbye...\n'.encode() )
            sys.exit(0)

        for args in userInput:
            # os.write(1, args.encode() )
            handleCommand(args.split() )
            
    except EOFError as Eoferror:
        print(Eoferror)
        sys.exit(1)

