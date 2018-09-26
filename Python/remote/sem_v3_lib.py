#
# SharkSEM Script
# version 2.0.2
#
# Requires Python 3.x
#
# Copyright (c) 2010 TESCAN, s.r.o.
# http://www.tescan.com
#

def DeclareBytes():
    return b""

def DecodeString(s_in):
    i = 0
    for i in range(0, len(s_in)):
        if s_in[i] == 0:
            break            
    return s_in[0:i].decode()
