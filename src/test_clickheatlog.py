'''
Created on Oct 4, 2012
python vertion 2.7.3

@author: hungtd
'''
import unittest
import os
import io
import shutil
import linecache

from clickheatlog import ParserLine, TrackPoint, TrackPointFileStore, ClickHeatLog

class TestParseLine(unittest.TestCase):
    
    def testGetTrackPointReturnExpectedResult(self):
        fixtureLine = 'GET /clickempty.html?s=mimo&g=homenonlogin&x=998&y=32&w=1265&b=chrome&c=1&random=Tue%20Oct%2002%202012%2017:20:56%20GMT+0700%20(ICT) HTTP/1.1 http://cms.local:8080/index/varnish 2012-10-02'
        trackPointResult = ParserLine(fixtureLine).getTrackPoint()
        trackPointExpected = TrackPoint(x='998', y='32', width='1265', browser='chrome', c='1', referUrl='http://cms.local:8080/index/varnish', day='2012-10-02', site='mimo', group='homenonlogin')
        self.assertEqual(trackPointExpected, trackPointResult)
        
    def testGetTrackPointReturnNone(self):
        fixtureLine = 'GET /clickempty.html?g=homenonlogin&x=998&y=32&w=1265&b=chrome&c=1&random=Tue%20Oct%2002%202012%2017:20:56%20GMT+0700%20(ICT) HTTP/1.1 http://cms.local:8080/index/varnish 2012-10-02'
        trackPointResult = ParserLine(fixtureLine).getTrackPoint()
        self.assertIsNone(trackPointResult)
        
        trackPointResult = ParserLine('').getTrackPoint()
        self.assertIsNone(trackPointResult)

class TestTrackPointFileStoreSuccess(unittest.TestCase):

    def setUp(self):
        if not os.path.isdir('descStoreTest'): 
            os.makedirs('descStoreTest');
        self.descDir = os.path.abspath('descStoreTest')
        self.trackPointStore = TrackPointFileStore(self.descDir)
        
    def tearDown(self):
        #remove all content in folder 
        shutil.rmtree(self.descDir)
#        pass
    
    def testSaveTrackPointMakeDescFolderBySiteNameAndGroupName(self):
        trackPoint = TrackPoint(x='1',y='2',width='1024',browser='firefox',c='1',referUrl='http://www.dantri.com',day='2012-10-07',site='mimo',group='home')
       
        self.assertFalse(os.path.exists(self.descDir+'/mimo,home'))
        self.trackPointStore.saveTrackPoint(trackPoint)
        self.assertTrue(os.path.isdir(self.descDir+'/mimo,home'))
    
    def testSaveTrackPointMakeFileLogDatabaseByDay(self):
        trackPoint = TrackPoint(x='1',y='2',width='1024',browser='firefox',c='1',referUrl='http://www.dantri.com',day='2012-10-07',site='mimo',group='home')
        self.trackPointStore.saveTrackPoint(trackPoint)
        self.assertTrue(os.path.isfile(self.descDir+'/mimo,home/2012-10-07.log'))
        self.assertTrue(os.path.isfile(self.descDir+'/mimo,home/url.txt'))
    
    def testSaveTrackPointToSameDescDataIntegrity(self):
        trackPoint = TrackPoint(x='1',y='2',width='1024',browser='firefox',c='1',referUrl='http://www.dantri.com',day='2012-10-07',site='mimo',group='home')
        trackPoint2 = TrackPoint(x='2',y='2',width='1024',browser='firefox',c='1',referUrl='http://www.dantri.com',day='2012-10-07',site='mimo',group='home')
        self.trackPointStore.saveTrackPoint(trackPoint)
        self.trackPointStore.saveTrackPoint(trackPoint2)
        
        fileUrlOpen = io.open(self.descDir+'/mimo,home/url.txt', 'r')
        self.assertEqual('http://www.dantri.com>0>0>0', fileUrlOpen.readline()) 
        fileUrlOpen.close()
        
        fileDayLogOpen = io.open(self.descDir+'/mimo,home/2012-10-07.log', 'r')
        self.assertEqual('1|2|1024|firefox|1\n',  fileDayLogOpen.readline())
        self.assertEqual('2|2|1024|firefox|1\n',  fileDayLogOpen.readline())
        fileDayLogOpen.close()
        
    def testSaveTrackPointDataIntegrityWithMultiTrackPointMultiFolder(self):
        trackPoint = TrackPoint(x='1',y='2',width='1024',browser='firefox',c='1',referUrl='http://www.dantri.com',day='2012-10-07',site='mimo',group='home')
        trackPoint2 = TrackPoint(x='2',y='2',width='1024',browser='chrome',c='1',referUrl='http://www.vnexpress.com',day='2012-10-07',site='mimo',group='profile')
        self.trackPointStore.saveTrackPoint(trackPoint)
        self.trackPointStore.saveTrackPoint(trackPoint2)
        
        fileUrlOpen = io.open(self.descDir+'/mimo,home/url.txt', 'r')
        self.assertEqual('http://www.dantri.com>0>0>0', fileUrlOpen.readline()) 
        fileUrlOpen.close()
        
        fileUrlOpen = io.open(self.descDir+'/mimo,profile/url.txt', 'r')
        self.assertEqual('http://www.vnexpress.com>0>0>0', fileUrlOpen.readline()) 
        fileUrlOpen.close()
        
        fileDayLogOpen = io.open(self.descDir+'/mimo,home/2012-10-07.log', 'r')
        self.assertEqual('1|2|1024|firefox|1\n', fileDayLogOpen.readline())
        fileDayLogOpen.close()
        
        fileDayLogOpen = io.open(self.descDir+'/mimo,profile/2012-10-07.log', 'r')
        self.assertEqual('2|2|1024|chrome|1\n', fileDayLogOpen.readline())
        fileDayLogOpen.close()
            
    def testSaveTrackPointsDataIntegrityWithMultiTrackPointMultiFolder(self):
        trackPoint = TrackPoint(x='1',y='2',width='1024',browser='firefox',c='1',referUrl='http://www.dantri.com',day='2012-10-07',site='mimo',group='home')
        trackPoint2 = TrackPoint(x='2',y='2',width='1024',browser='chrome',c='1',referUrl='http://www.vnexpress.com',day='2012-10-07',site='mimo',group='profile')
        self.trackPointStore.saveTrackPoints([trackPoint,trackPoint2])
        
        fileUrlOpen = io.open(self.descDir+'/mimo,home/url.txt', 'r')
        self.assertEqual('http://www.dantri.com>0>0>0', fileUrlOpen.readline()) 
        fileUrlOpen.close()
        
        fileUrlOpen = io.open(self.descDir+'/mimo,profile/url.txt', 'r')
        self.assertEqual('http://www.vnexpress.com>0>0>0', fileUrlOpen.readline()) 
        fileUrlOpen.close()
        
        fileDayLogOpen = io.open(self.descDir+'/mimo,home/2012-10-07.log', 'r')
        self.assertEqual('1|2|1024|firefox|1\n', fileDayLogOpen.readline())
        fileDayLogOpen.close()
        
        fileDayLogOpen = io.open(self.descDir+'/mimo,profile/2012-10-07.log', 'r')
        self.assertEqual('2|2|1024|chrome|1\n', fileDayLogOpen.readline())
        fileDayLogOpen.close()
    
class TestClickHeatLog(unittest.TestCase):
    def setUp(self):
        self.fileLog = fileLog = os.path.abspath('1msource.log')
        self.descDir = descDir = os.path.abspath('../test')
        
        trackPointStoreStrategy = TrackPointFileStore(descDir)
        trackPointLineParseStrategy = ParserLine()
        self.heatClickLog = ClickHeatLog(fileLog, trackPointLineParseStrategy, trackPointStoreStrategy)

    def testCreateDescDirByDayFromSourceLog(self):
        dailyLogFilePath = self.descDir + '/mimo,homenonlogin/2012-10-02.log'
        urlFilePath = self.descDir + '/mimo,homenonlogin/url.txt'
        urlProfileFilePath = self.descDir + '/mimo,profile/url.txt'
        processLogFilePath = self.descDir + '/logproccesed.txt'
        dailyProfileLogFilePath = self.descDir + '/mimo,profile/2012-10-03.log'
        
        self.assertFalse(os.path.exists(self.descDir+'/mimo,homenonlogin'))
        self.assertFalse(os.path.exists(self.descDir+'/mimo,profile'))
        
        self.heatClickLog.parserFileLog()

        self.assertTrue(os.path.isdir(self.descDir+'/mimo,homenonlogin'))
        self.assertTrue(os.path.isdir(self.descDir+'/mimo,profile'))
        self.assertTrue(os.path.isfile(dailyLogFilePath))
        self.assertTrue(os.path.isfile(dailyProfileLogFilePath))

        self.assertTrue(os.path.isfile(urlProfileFilePath))
        self.assertTrue(os.path.isfile(urlFilePath))
        
        self.assertTrue(os.path.isfile(processLogFilePath))
       
        fileUrlOpen = io.open( urlFilePath, 'r')
        self.assertEqual('http://cms.local:8080/index/varnish>0>0>0', fileUrlOpen.readline()) 
        fileUrlOpen.close()
        
        fileUrlOpen = io.open( urlProfileFilePath, 'r')
        self.assertEqual('http://dantri.com>0>0>0', fileUrlOpen.readline()) 
        fileUrlOpen.close()
        
        fileLogProccesed = io.open(processLogFilePath)
        lines = fileLogProccesed.readlines()
        fileLogProccesed.close()
        self.assertTrue(any(self.fileLog in item for item in lines))
        
        lastLine = linecache.getline(dailyLogFilePath, 100)
        firstLine = linecache.getline(dailyLogFilePath, 1)
        self.assertEqual('1001|456|1265|chrome|1\n', lastLine)
        self.assertEqual('1001|456|1265|chrome|1\n', firstLine)
        
        lastLine = linecache.getline(dailyProfileLogFilePath, 100)
        firstLine = linecache.getline(dailyProfileLogFilePath, 1)
        self.assertEqual('998|512|1265|chrome|1\n', lastLine)
        self.assertEqual('998|512|1265|chrome|1\n', firstLine)
        
    def tearDown(self):
        shutil.rmtree(self.descDir + '/mimo,homenonlogin')
        shutil.rmtree(self.descDir + '/mimo,profile')
        os.remove(self.descDir + '/logproccesed.txt')
        pass

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
