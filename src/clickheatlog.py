'''
Created on Oct 4, 2012
python vertion 2.7.3
@author: hungtd
'''
import io
import os
import re
import fileinput
#import sys

class ParserLine(object):
    '''
    Create client class which will parse log line 
    Line parse example 
    GET /clickempty.html?s=mimo&g=homenonlogin&x=998&y=32&w=1265&b=chrome&c=1&random=Tue%20Oct%2002%202012%2017:20:56%20GMT+0700%20(ICT) HTTP/1.1 http://cms.local:8080/index/varnish 2012-10-02
    '''
    def __init__(self, lineContent=None, pattern='s=(.*)&g=(.*)&x=([0-9]*)&y=([0-9]*)&w=([0-9]*)&b=(.*)&c=([0-9])&random=(.*) (http.*) (\d{4}-\d{2}-\d{2})'):
        self.line = lineContent
        self.pattern = pattern
    
    def getTrackPoint(self,lineContent=None):
        if lineContent:
            line = lineContent
        else:
            line = self.line
        '''
        @return: TrackPoint
        '''
        match = re.search(self.pattern, line)
        if not match:
            return None
        site = match.group(1)
        group = match.group(2)
        x = match.group(3)
        y = match.group(4)
        width = match.group(5)
        browser = match.group(6)
        c = match.group(7)
        fromSite = match.group(9)
        dateString = match.group(10)
        
        return TrackPoint(x, y, width, browser, c, fromSite, dateString, site, group)
    
    def getTrackPoints(self,linesContent):
        result = []
        for line in linesContent:
            trackPoint = self.getTrackPoint(line)
            if trackPoint:
                result.append(trackPoint)
        return result
    
class TrackPoint(object):
    '''
    Entity store tracker point meta data
    '''
    def __init__(self, x, y, width, browser, c, referUrl, day, site, group):
        self.x = x
        self.y = y
        self.width = width
        self.browser = browser
        self.c = c
        self.referUrl = referUrl
        self.day = day
        self.site = site
        self.group = group
        
    def __eq__(self, other): 
        return self.__dict__ == other.__dict__
    
    def __str__(self, *args, **kwargs):
        return object.__str__(self, *args, **kwargs) + "\n x=" + self.x + ", y=" + self.y + ", width=" + self.width + ", browser=" + self.browser + ", c=" + self.c + ", referUrl=" + self.referUrl + ", day=" + self.day + ", site=" + self.site + ", group=" + self.group

class TrackPointException(IOError): pass    

class TrackPointFileStore(object):
    '''
    save tracpoint to file store at descDir
    '''
    
    def __init__(self, descDir): 
        self.descDir = descDir
        self.fileDirCache = {}
        
    def __getFileWritableOpenedObject(self, filePath):     
        '''
        cache fileinput open multifile with mode append content
        @return: file
        ''' 
        if self.fileDirCache.has_key(filePath): 
            return self.fileDirCache[filePath]
        
        fileDayLogWrite = io.FileIO(filePath, 'a')
       
        self.fileDirCache[filePath] = fileDayLogWrite
        return fileDayLogWrite
    
    def __closeFileWritableOpened(self):
        '''
        close all fileinput opened
        '''
        for fileName in self.fileDirCache.keys():
            fileObj = self.fileDirCache.pop(fileName)
            if fileObj:
                fileObj.close()

    def __saveTrackPoint (self, trackPoint):
        '''
        @var trackPoint: TrackPoint
        '''
        folderDesc = self.descDir + "/" + trackPoint.site + "," + trackPoint.group
        folderDesc = os.path.abspath(folderDesc)
        fileUrlTxt = folderDesc + "/url.txt"     
        fileUrlContent = trackPoint.referUrl + ">0>0>0"
        fileDayLog = folderDesc + "/" + trackPoint.day + '.log'
        fileDayLineContent = trackPoint.x + '|' + trackPoint.y + '|' + trackPoint.width + '|' + trackPoint.browser + '|' + trackPoint.c + '\n'
        
        if not os.path.isdir(folderDesc):
            os.mkdir(folderDesc)
             
        if not os.path.isfile(fileUrlTxt):
            fileUrlTxtWrite = io.FileIO(fileUrlTxt, 'w+')
            fileUrlTxtWrite.write(fileUrlContent)
            fileUrlTxtWrite.close()
        
        fileDayLogWrite = self.__getFileWritableOpenedObject(fileDayLog)
#        fileDayLogWrite = io.open(fileDayLog,'a+')
        fileDayLogWrite.write(fileDayLineContent)
#        fileDayLogWrite.close()
        
    def saveTrackPoint(self, trackPoint):
        if not os.path.isdir(self.descDir):
            raise TrackPointException('No found directory ' + self.descDir)
        self.__saveTrackPoint(trackPoint)
        self.__closeFileWritableOpened()
    
    def saveTrackPoints(self, trackPoints):
        if not os.path.isdir(self.descDir):
            raise TrackPointException('No found directory ' + self.descDir)

        for trackPoint in trackPoints:
            self.__saveTrackPoint(trackPoint)
        self.__closeFileWritableOpened()

class ClickHeatLogError(Exception): pass

class ClickHeatLog(object):
    def __init__(self,fileLog=None,trackPointLineParseStrategy=None,trackPointStoreStrategy=None):
        '''
        @fileLog: string
        @trackPointLineParseStrategy: ParserLine
        @trackPointStoreStrategy: TrackPointFileStore
        '''
        self.fileLog = fileLog
        self.lineParser = trackPointLineParseStrategy
        self.trackPointStore = trackPointStoreStrategy
        self.hash = {}

    def parserFileLog(self):
        
        '''
        @self.lineParser: ParserLine
        @self.trackPointStore: TrackPointFileStore
        '''
        processLogFilePath = self.trackPointStore.descDir + '/logproccesed.txt'
        fileLogProccesed = io.FileIO(processLogFilePath,'a+')
        lines = fileLogProccesed.readlines()
        
        
        if (any(self.fileLog in item for item in lines)):
            fileLogProccesed.close()
            return None
        
        fileLogProccesed.write(self.fileLog)
        fileLogProccesed.close()
        
        return self.__parserFileLogImprovePerformance()
        
#        fileLogOpen = io.open(self.fileLog)
        fileLogOpen = fileinput.input(self.fileLog)
        for line in fileLogOpen:
            trackPoint = self.lineParser.getTrackPoint(line)
            if not trackPoint:
                continue
            self.trackPointStore.saveTrackPoint(trackPoint)
        fileLogOpen.close()
        
#        fileWriter = io.open(processLogFilePath,'a+')
#        fileWriter.write(unicode(self.fileLog))
#        fileWriter.close()
        
    def __parserFileLogImprovePerformance(self):
        fileLogOpen = open(self.fileLog,'r')
        BUFFER = int(1E6)
        while True:
            lines = fileLogOpen.readlines()
            if lines == []:
                break
            trackPoints = self.lineParser.getTrackPoints(lines)
            self.trackPointStore.saveTrackPoints(trackPoints)
#            del trackPoints
#            del lines
        fileLogOpen.close()
