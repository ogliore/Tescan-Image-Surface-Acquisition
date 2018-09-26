#
# SharkSEM Script
# version 2.0.2
#
# Requires Python 2.x or 3.x
#
# Copyright (c) 2010 TESCAN, s.r.o.
# http://www.tescan.com
#

#
# main SEM interface class
#

import sem_conn

class Sem:
    """Tescan SEM Control Class
    
    Main purpose is to provide a wrapper which allows any Python application 
    to control Tescan SEM. Internaly, there is a wrapper around the SharkSEM
    remote control protocol.
    
    Your Python script requires only this class.
    
    See SharkSEM documentation for more information.
    """
    
    def __init__(self):
        """Constructor"""
        self.connection = sem_conn.SemConnection()
        
    def _CInt(self, arg):
        return (sem_conn.ArgType.Int, int(arg))
        
    def _CUnsigned(self, arg):
        return (sem_conn.ArgType.UnsignedInt, int(arg))

    def _CFloat(self, arg):
        return (sem_conn.ArgType.Float, float(arg))
    
    def _CString(self, arg):
        return (sem_conn.ArgType.String, str(arg))
        
#
# session management
#    

    def Connect(self, address, port):
        """ Connect to SEM
        
        Connection must be established before the first call of a SharkSEM function.
        
        == 0        ok
        < 0         error occured
        """
        return self.connection.Connect(address, port)
        
    def Disconnect(self):
        """ Disconnect SEM
        
        Opposite to Connect()
        """
        self.connection.Disconnect()
        
    def SetWaitFlags(self, flags):
        """ Set wait condition 
        
        SharkSEM request header contains set of flags, which specify 
        conditions to execute the request.
        
        bit 0       Wait A (SEM scanning)
        bit 1       Wait B (SEM stage)
        bit 2       Wait C (SEM optics)
        bit 3       Wait D (SEM automatic procedure)
        bit 4       Wait E (FIB scanning)
        bit 5       Wait F (FIB optics)
        bit 6       Wait G (FIB automatic procedure)
        """
        self.connection.wait_flags = flags
        
    def FetchImage(self, channel, size):
        """ Read single image
        
        channel     input video channel
        size        number of image pixels (bytes)        
        
        Scanning should be initiated first. Then, call this blocking function. During
        the call, messages from data connection are collected, decoded and image is
        stored as a 'bytes' type. The resulting image is passed as a return value.
        """
        return self.connection.FetchImage('ScData', channel, size)

    def FetchCameraImage(self, channel):
        """ Read single image from camera (wait till it comes)
        
        channel     input video channel
        
        Camera must be activated first. Then, call this blocking function, which
        returns the image as a return value. The value has three components -
        width, height, data.
        """
        return self.connection.FetchCameraImage(channel)
        
################################################################################
#
# Electron Optics
#    

    def AutoColumn(self, channel):
        self.connection.Send('AutoColumn', self._CInt(channel))

    def AutoGun(self, channel):
        self.connection.Send('AutoGun', self._CInt(channel))
        
    def AutoWD(self, channel):
        self.connection.Send('AutoWD', self._CInt(channel))

    def Degauss(self):
        self.connection.Send('Degauss')

    def EnumCenterings(self):
        return self.connection.RecvString('EnumCenterings')
        
    def EnumGeometries(self):
        return self.connection.RecvString('EnumGeometries')

    def EnumPCIndexes(self):
        return self.connection.RecvString('EnumPCIndexes')

    def Get3DBeam(self):
        return self.connection.Recv('Get3DBeam', (sem_conn.ArgType.Float, sem_conn.ArgType.Float))

    def GetCentering(self, index):
        return self.connection.Recv('GetCentering', (sem_conn.ArgType.Float, sem_conn.ArgType.Float), self._CInt(index))

    def GetGeometry(self, index):
        return self.connection.Recv('GetGeometry', (sem_conn.ArgType.Float, sem_conn.ArgType.Float), self._CInt(index))
    
    def GetIAbsorbed(self):
        return self.connection.RecvFloat('GetIAbsorbed')
        
    def GetImageShift(self):
        return self.connection.Recv('GetImageShift', (sem_conn.ArgType.Float, sem_conn.ArgType.Float))

    def GetPCFine(self):
        return self.connection.RecvFloat('GetPCFine')

    def GetPCContinual(self):
        return self.connection.RecvFloat('GetPCContinual')

    def GetPCIndex(self):
        return self.connection.RecvInt('GetPCIndex')

    def GetSpotSize(self):
        return self.connection.RecvFloat('GetSpotSize')

    def GetViewField(self):
        return self.connection.RecvFloat('GetViewField')
        
    def GetWD(self):
        return self.connection.RecvFloat('GetWD')
    
    def Set3DBeam(self, alpha, beta):
        self.connection.Send('Set3DBeam', self._CFloat(alpha), self._CFloat(beta))
        
    def SetCentering(self, index, x, y):
        self.connection.Send('SetCentering', self._CInt(index), self._CFloat(x), self._CFloat(y))

    def SetGeometry(self, index, x, y):
        self.connection.Send('SetGeometry', self._CInt(index), self._CFloat(x), self._CFloat(y))
        
    def SetImageShift(self, x, y):
        self.connection.Send('SetImageShift', self._CFloat(x), self._CFloat(y))
    
    def SetPCIndex(self, index):
        self.connection.Send('SetPCIndex', self._CInt(index))

    def SetPCContinual(self, pc_continual):
        self.connection.Send('SetPCContinual', self._CFloat(pc_continual))

    def SetViewField(self, vf):
        self.connection.Send('SetViewField', self._CFloat(vf))

    def SetWD(self, wd):
        self.connection.Send('SetWD', self._CFloat(wd))

################################################################################
#
# Manipulators - enumeration, configuration
#

    def ManipGetCount(self):
        return self.connection.RecvInt('ManipGetCount')

    def ManipGetCurr(self):
        return self.connection.RecvInt('ManipGetCurr')

    def ManipSetCurr(self, index):
        self.connection.Send('ManipSetCurr', self._CInt(index))
        
    def ManipGetConfig(self, index):
        return self.connection.RecvString('ManipGetConfig', self._CInt(index))

################################################################################
#
# Stage Control
#

    def StgCalibrate(self):
        self.connection.Send('StgCalibrate')

    def StgGetPosition(self):
        return self.connection.Recv('StgGetPosition', (sem_conn.ArgType.Float, sem_conn.ArgType.Float, sem_conn.ArgType.Float, sem_conn.ArgType.Float, sem_conn.ArgType.Float))

    def StgIsBusy(self):
        return self.connection.RecvInt('StgIsBusy')

    def StgIsCalibrated(self):
        return self.connection.RecvInt('StgIsCalibrated')

    def StgMoveTo(self, *arg):
        f_arg = []
        for p in arg:
            f_arg.append(self._CFloat(p))
        self.connection.Send('StgMoveTo', *f_arg)

    def StgStop(self):
        self.connection.Send('StgStop')

################################################################################
#
# Input Channels And Detectors
#

    def DtAutoSignal(self, channel):
        self.connection.Send('DtAutoSignal', self._CInt(channel))
    
    def DtEnable(self, channel, enable, bpp = -1):
        if (bpp == -1):
            self.connection.Send('DtEnable', self._CInt(channel), self._CInt(enable))
        else:
            self.connection.Send('DtEnable', self._CInt(channel), self._CInt(enable), self._CInt(bpp))

    def DtEnumDetectors(self):
        return self.connection.RecvString('DtEnumDetectors')

    def DtGetChannels(self):
        return self.connection.RecvInt('DtGetChannels')

    def DtGetEnabled(self, channel):
        return self.connection.Recv('DtGetEnabled', (sem_conn.ArgType.Int, sem_conn.ArgType.Int), self._CInt(channel))

    def DtGetGainBlack(self, detector):
        return self.connection.Recv('DtGetGainBlack', (sem_conn.ArgType.Float, sem_conn.ArgType.Float), self._CInt(detector))

    def DtGetSelected(self, channel):
        return self.connection.RecvInt('DtGetSelected', self._CInt(channel))
        
    def DtSelect(self, channel, detector):
        self.connection.Send('DtSelect', self._CInt(channel), self._CInt(detector))

    def DtSetGainBlack(self, detector, gain, black):
        self.connection.Send('DtSetGainBlack', self._CInt(detector), self._CFloat(gain), self._CFloat(black))

################################################################################
#
# Scanning
#

    def ScEnumSpeeds(self):
        return self.connection.RecvString('ScEnumSpeeds')

    def ScGetBlanker(self):
        return self.connection.RecvInt('ScGetBlanker')

    def ScGetExternal(self):
        return self.connection.RecvInt('ScGetExternal')
    
    def ScGetSpeed(self):
        return self.connection.RecvInt('ScGetSpeed')

    def ScScanLine(self, frameid, width, height, x0, y0, x1, y1, dwell_time, pixel_count, single):
        return self.connection.RecvInt('ScScanLine', self._CInt(0), self._CInt(width), self._CInt(height), self._CInt(x0), self._CInt(y0), self._CInt(x1), self._CInt(y1), self._CInt(dwell_time), self._CInt(pixel_count), self._CInt(single))

    def ScScanXY(self, frameid, width, height, left, top, right, bottom, single):
        return self.connection.RecvInt('ScScanXY', self._CInt(0), self._CInt(width), self._CInt(height), self._CInt(left), self._CInt(top), self._CInt(right), self._CInt(bottom), self._CInt(single))

    def ScSetBlanker(self, mode):
        self.connection.Send('ScSetBlanker', self._CInt(mode))

    def ScSetExternal(self, enable):
        self.connection.Send('ScSetExternal', self._CInt(enable))

    def ScSetSpeed(self, speed):
        self.connection.Send('ScSetSpeed', self._CInt(speed))

    def ScStopScan(self):
        self.connection.Send('ScStopScan')
        
    def ScSetBeamPos(self, x, y):
        self.connection.Send('ScSetBeamPos', self._CFloat(x), self._CFloat(y))

################################################################################
#
# Scanning Mode
#

    def SMEnumModes(self):
        return self.connection.RecvString('SMEnumModes')
    
    def SMGetMode(self):
        return self.connection.RecvInt('SMGetMode')
        
    def SMSetMode(self, mode):
        self.connection.Send('SMSetMode', self._CInt(mode))

################################################################################
#
# Vacuum
#

    def VacGetPressure(self, gauge):
        return self.connection.RecvFloat('VacGetPressure', self._CInt(gauge))

    def VacGetStatus(self):
        return self.connection.RecvInt('VacGetStatus')

    def VacGetVPMode(self):
        return self.connection.RecvInt('VacGetVPMode')

    def VacGetVPPress(self):
        return self.connection.RecvFloat('VacGetVPPress')

    def VacPump(self):
        self.connection.Send('VacPump')

    def VacSetVPMode(self, vpmode):
        self.connection.Send('VacSetVPMode', self._CInt(vpmode))

    def VacSetVPPress(self, pressure):
        self.connection.Send('VacSetVPPress', self._CFloat(pressure))

    def VacVent(self):
        self.connection.Send('VacVent')
        
################################################################################
#
# Airlock
#

    def ArlGetStatus(self):
        return self.connection.RecvInt('ArlGetStatus')
    
    def ArlPump(self):
        self.connection.Send('ArlPump')
    
    def ArlVent(self):
        self.connection.Send('ArlVent')

    def ArlOpenValve(self):
        self.connection.Send('ArlOpenValve')

    def ArlCloseValve(self):
        self.connection.Send('ArlCloseValve')
        
################################################################################
#
# High Voltage
#
    def HVAutoHeat(self, channel):
        self.connection.Send('HVAutoHeat', self._CInt(channel))

    def HVBeamOff(self):
        self.connection.Send('HVBeamOff')
    
    def HVBeamOn(self):
        self.connection.Send('HVBeamOn')

    def HVEnumIndexes(self):
        return self.connection.RecvString('HVEnumIndexes')

    def HVGetBeam(self):
        return self.connection.RecvInt('HVGetBeam')

    def HVGetEmission(self):
        return self.connection.RecvFloat('HVGetEmission')

    def HVGetFilTime(self):
        return self.connection.RecvInt('HVGetFilTime')

    def HVGetHeating(self):
        return self.connection.RecvFloat('HVGetHeating')

    def HVGetIndex(self):
        return self.connection.RecvInt('HVGetIndex')

    def HVGetVoltage(self):
        return self.connection.RecvFloat('HVGetVoltage')

    def HVSetIndex(self, index):
        self.connection.Send('HVSetIndex', self._CInt(index))

    def HVSetVoltage(self, voltage):
        self.connection.Send('HVSetVoltage', self._CFloat(voltage))

################################################################################
#
# SEM GUI Control
#

    def GUIGetScanning(self):
        return self.connection.RecvInt('GUIGetScanning')
    
    def GUISetScanning(self, enable):
        self.connection.Send('GUISetScanning', self._CInt(enable))

################################################################################
#
# Camera
#
    def CameraEnable(self, channel, zoom, fps, compression):
        return self.connection.Send('CameraEnable', self._CInt(channel), self._CFloat(zoom), self._CFloat(fps), self._CInt(compression))

    def CameraDisable(self):
        return self.connection.Send('CameraDisable')

    def CameraGetStatus(self, channel):
        return self.connection.Recv('CameraGetStatus', (sem_conn.ArgType.Int, sem_conn.ArgType.Float, sem_conn.ArgType.Float, sem_conn.ArgType.Int), self._CInt(channel))

################################################################################
#
# Miscellaneous
#

    def TcpGetVersion(self):
        return self.connection.RecvString('TcpGetVersion')

    def ChamberLed(self, onoff):
        self.connection.Send('ChamberLed', self._CInt(onoff))

    def Delay(self, delay):
        self.connection.Send('Delay', self._CInt(delay))

    def TcpGetDevice(self):
        return self.connection.RecvString('TcpGetDevice')
