#
# SharkSEM Script
# version 2.0.2
#
# Requires Python 2.x or 3.x
#
# Copyright (c) 2010 TESCAN, s.r.o.
# http://www.tescan.com
#

import socket
import string
import struct
import sys

if sys.version_info[0] == 2:
    from sem_v2_lib import *
     
if sys.version_info[0] == 3:
    from sem_v3_lib import *

#
# SharkSEM data types
#
class ArgType:
    """SharkSEM data types

    Contains the common types used in the client-server communication.
    """
    Int, UnsignedInt, String, Float = range(4)
    

#
# SharkSEM connection
#
class SemConnection:
    """SEM Connection Class

    This object keeps the connection context, ie. the communication sockets,
    scannig buffers and other context variables. There are also methods for 
    argument marshaling (packing / unpacking).
    """
    
    def __init__(self):
        """ Constructor """
        self.socket_c = 0       # control connection
        self.socket_d = 0       # data connection
        self.wait_flags = 0     # wait flags (bits 5:0)
        
    def _SendStr(self, s):
        """ Blocking send """
        size = len(s)
        start = 0
        while start < size:
            res = self.socket_c.send(s[start:size])
            start = start + res
            
    def _RecvFully(self, sock, size):
        """ Blocking receive - wait for all data """
        received = 0
        str = DeclareBytes()
        while received < size:
            s = sock.recv(size - received)
            received = received + len(s)
            str = str + s
        return str
            
    def _RecvStrC(self, size):
        """ Blocking receive - control connection """
        return self._RecvFully(self.socket_c, size)
    
    def _RecvStrD(self, size):
        """ Blocking receive - data connection """
        return self._RecvFully(self.socket_d, size)
    
    def _TcpRegDataPort(self, port):
        """ Register data portn in the SharkSEM server """
        return self.RecvInt('TcpRegDataPort', (ArgType.Int, port))

    def Connect(self, address, port):
        """ Connect to the server """
        try:
            self.socket_c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_c.connect((address, port))
            self.socket_d = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_d.bind(('', 0))
            loc_ep = self.socket_d.getsockname()
            loc_port = loc_ep[1]
            self._TcpRegDataPort(loc_port)
            self.socket_d.connect((address, port + 1))
            return 0
        
        except:
            self.Disconnect()
            return -1
        
    def Disconnect(self):
        """ Close the connection(s) """
        try:
            if self.socket_c != 0:
                socket.close(self.socket_c)
                self.socket_c = 0
            if self.socket_d != 0:
                socket.close(self.socket_d)
                self.socket_d = 0
        except:
            pass
        
    def FetchImage(self, fn_name, channel, size):
        """ Fetch image. See Sem.FetchImage for details """
        img = DeclareBytes()
        img_sz = 0
        while img_sz < size:
            # receive, parse and verify the message header
            msg_name = self._RecvStrD(16)
            hdr = self._RecvStrD(16)
            v = struct.unpack("<IIHHI", hdr)
            body_size = v[0]
            
            # get fn name
            s = DecodeString(msg_name)
            
            # receive and parse the body
            body = self._RecvStrD(body_size)
            if s != fn_name:
                continue
            if body_size < 20:
                continue
            body_params = body[0:20]
            body_data = body[20:]
            v = struct.unpack("<IIIII", body_params)
            arg_frame_id = v[0]
            arg_channel = v[1]
            arg_index = v[2]
            arg_bpp = v[3]
            arg_data_size = v[4]
            if arg_channel != channel:
                continue
            if arg_index < img_sz:         # correct, can be sent more than once
                img = img[0:arg_index]
                img_sz = arg_index
            if arg_index > img_sz:         # data packet lost
                continue
            if arg_bpp != 8:
                continue
            
            # append data
            img = img + body_data
            img_sz = img_sz + arg_data_size
            
        # when we have complete image, terminate
        return img
      
    def FetchCameraImage(self, channel):
        """ Fetch camera image. See Sem.FetchCameraImage for details """
        img = DeclareBytes()
        img_received = 0
        while not img_received:
            # receive, parse and verify the message header
            msg_name = self._RecvStrD(16)
            hdr = self._RecvStrD(16)
            v = struct.unpack("<IIHHI", hdr)
            body_size = v[0]
            
            # get fn name
            s = DecodeString(msg_name)
                                        
            # receive and parse the body
            body = self._RecvStrD(body_size)
            if s != 'CameraData':
                continue
            if body_size < 20:
                continue
            body_params = body[0:20]
            body_data = body[20:]
            v = struct.unpack("<IIIII", body_params)
            arg_channel = v[0]
            arg_bpp = v[1]
            arg_width = v[2]
            arg_height = v[3]
            arg_data_size = v[4]
            if arg_channel != channel:
                continue
            if arg_bpp != 8:
                continue
            
            img_received = 1
            
            # append data
            arg_img = body_data
            
        # when we have complete image, terminate
        return (arg_width, arg_height, arg_img)

    def Send(self, fn_name, *args):
        """ Send simple message (header + data), no response expected
        
        This call has variable number of input arguments. Wait flags are 
        taken from self.wait_flags.
        
        Following types are supported:
            ArgType.Int
            ArgType.UnsignedInt
            ArgType.String
            ArgType.Float
            
        The Int and UnsignedInt types are mapped to 32-bit int, StringType
        is a variable sized string, FloatType is send as SharkSEM floating
        point value (actually string).
        
        Each argument is a tuple consisting of two items - type and value.
        
        SharkSEM header restrictions:
            - Flags (except for Wait flags) are set to 0
            - Identification = 0
            - Queue = 0
        """
        
        # build message body
        body = DeclareBytes()                           # variable of type 'bytes'
        for pair in args:
            pair_type, pair_value = pair
            
            if pair_type == ArgType.Int:   				# 32-bit integer
                body = body + struct.pack("<i", pair_value)
                
            if pair_type == ArgType.UnsignedInt:   		# 32-bit unsigned integer
                body = body + struct.pack("<I", pair_value)

            if pair_type == ArgType.Float:              # floating point
                s = str(pair_value)
                l = (len(s) + 4) // 4 * 4
                s = s.ljust(l, "\x00")
                body = body + struct.pack("<I", l) + s.encode()
        
            if pair_type == ArgType.String:             # string
                l = (len(pair_value) + 4) // 4 * 4
                var = var.ljust(l, "\x00")
                body = body + struct.pack("<I", l) + pair_value.encode()
                
        # build message header
        s = fn_name.ljust(16, "\x00")                   # pad fn name (string)
        hdr = s.encode()                                # convert to bytes
        hdr = hdr + struct.pack("<IIHHI", len(body), 0, (self.wait_flags << 8), 0, 0)       # arguments
        
        try:
            self._SendStr(hdr)                          # send header
            self._SendStr(body)                         # send body
            
        except:
            pass
    
    def Recv(self, fn_name, retval, *args):
        """ Send message and receive response
        
        This call has variable number of input arguments.

        List containing the output arguments is returned. The output
        argument types are passed in the 'retval' list, which contains
        Python types.

        Following types are supported:
            ArgType.Int
            ArgType.UnsignedInt
            ArgType.String
            ArgType.Float
            
        If TupleType is specified, it must contain single value - (type). This
        indicates that the return value will be an array. In the output list,
        the array appears as a list object.
        """
        
        # send request
        self.Send(fn_name, *args)
        
        try:
            # receive header
            fn_recv = self._RecvStrC(16)
            hdr = self._RecvStrC(16)
            
            # parse header
            v = struct.unpack("<IIHHI", hdr)
            body_size = v[0]
            
            # receive body
            body = self._RecvStrC(body_size)
            
        except:
            return

        # parse return value
        l = []
        start = 0
        
        for t in retval:
                        
            if t == ArgType.Int:   				# 32-bit integer
                stop = start + 4
                v = struct.unpack("<i", body[start:stop])
                l.append(v[0])
                start = stop
                
            if t == ArgType.UnsignedInt:   		# 32-bit unsigned integer
                stop = start + 4
                v = struct.unpack("<I", body[start:stop])
                l.append(v[0])
                start = stop

            if t == ArgType.Float:              # floating point
                stop = start + 4
                v = struct.unpack("<I", body[start:stop])
                fl_size = v[0]
                start = stop
                stop = start + fl_size
                s = DecodeString(body[start:stop])
                l.append(float(s))
                start = stop
                
            if t == ArgType.String:             # string
                stop = start + 4
                v = struct.unpack("<I", body[start:stop])
                fl_size = v[0]
                start = stop
                stop = start + fl_size
                s = DecodeString(body[start:stop])
                l.append(s)
                start = stop

        return l
                
    def RecvInt(self, fn_name, *args):
        """ Simple variant of Recv() - single int value is expected """
        v = self.Recv(fn_name, (ArgType.Int,), *args)
        return v[0]

    def RecvUInt(self, fn_name, *args):
        """ Simple variant of Recv() - single unsigned int value is expected """
        v = self.Recv(fn_name, (ArgType.UnsignedInt,), *args)
        return v[0]

    def RecvFloat(self, fn_name, *args):
        """ Simple variant of Recv() - single float value is expected """
        v = self.Recv(fn_name, (ArgType.Float,), *args)
        return v[0]

    def RecvString(self, fn_name, *args):
        """ Simple variant of Recv() - single string value is expected """
        v = self.Recv(fn_name, (ArgType.String,), *args)
        return v[0]
