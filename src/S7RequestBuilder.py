import re
import time
import json
import time

datablocks = []

class Signal:
	def __init__(self, region, db, offset, datatype):
		self.regionLetterCode = region
		self.db = db
		self.offset = offset
		self.datatype = datatype
		self.size = self.GetSizeInBytes()
		self.value = -1
		self.name = self.SetName()

	def GetSizeInBytes(self):
		if self.datatype == "REAL":
			return 4
		if self.datatype == "BOOL":
			return 1
		if self.datatype == "INT":
			return 2
		return 1
	def SetName(self):
		return str(self.regionLetterCode) + str(self.db) + "." + str(self.offset)
	def GetName(self):
		return self.name
	def GetValueType(self):
		if self.datatype == "REAL":
			return util.get_real
	def SetValue(self, value):
		self.value = value
	def GetValue(self):
		return self.value


def FetchSignals():
	lines = []
	signals = []
	f = open("address.txt")
	for x in f:
		if x.strip() == "//":
			print("EOF, stop further reading")
			break
		lines.append(x.strip().strip("%"))
	for l in lines:
		mem = re.findall(r'[\d+]+', l)
		signals.append(Signal(re.search(r'[A-Z]+', l).group(), mem[0], mem[1], re.search(r'[^:]*$', l).group()))
		RegisterDB(re.search(r'[A-Z]+', l).group(), mem[0])
	return signals

def SortSignalsByDB(signals):
	signals.sort(key=lambda line: int(line.db))
	return signals

def PrintSignals(signals):
	for s in signals:
		print(str(s.regionLetterCode) + str(s.db) + "." + str(s.offset) + ":" + str(s.datatype))

def RegisterDB(region, db):
	d = region + db
	if not d in datablocks:
		datablocks.append(d)

def SplitSignalsByRegion(signals):
	signals_s = []
	for d in datablocks:
		signals_s.append(Split(d, signals))
	return signals_s

def Split(datablock, signals):
	l = []
	for s in signals:
		if (str(s.regionLetterCode) + str(s.db)) == datablock:
			l.append(s)
	l.sort(key=lambda line: int(line.offset))
	return l

def SplitSignalsByContinousSpace(signals):
	signals_s = []
	for chunk in signals:
		temp = []
		if len(chunk) > 1:
			signals_s.append(SplitChunk(chunk))
		else:
			temp.append(chunk)
			signals_s.append(temp)
	return signals_s

def SplitChunk(chunk):
	t = []
	for i in range(1, len(chunk)):
		if int(chunk[i].offset) - int(chunk[i-1].offset) > 4:
			if len(t) > 0:
				index = len([ele for sub in t for ele in sub])
				t.append(chunk[index:i])
			else:
				t.append(chunk[:i])
	index = len([ele for sub in t for ele in sub])
	t.append(chunk[index:])
	print("Splitting " + str(len([ele for sub in t for ele in sub])) + " of " + str(len(chunk)) + " signals on " + str(chunk[0].regionLetterCode) + str(chunk[0].db))
	return t

def AddToPDUList(signals):
	chunks = [x for y in signals for x in y]
	print("Lengths")
	print(len(signals))
	print(len(chunks))
	test = CreatePDU(chunks, 224)
	return test


def CreatePDU(signals, sizeleft):
	smallList = []
	bigList = []
	for chunk in signals:
		sizeleft = sizeleft - (GetChunkSize(chunk)+4)
		print("Size left: " + str(sizeleft))
		if sizeleft > 0:
			print("appending " + str(chunk[0].name))
			smallList.append(chunk)
		elif sizeleft <= 0:
			print("Create new PDU at " + str(chunk[0].regionLetterCode) + str(chunk[0].db) + "." + str(chunk[0].offset) + "-" + str(chunk[len(chunk)-1].offset))
			bigList.append(smallList[:])
			smallList.clear()
			sizeleft = 224
			smallList.append(chunk)
	print("done loping")
	if smallList:
		bigList.append(smallList)
	return bigList

def GetChunkSize(chunk):
	firstitem = chunk[0]
	lastitem = chunk[len(chunk)-1]
	return (int(lastitem.offset) + int(lastitem.size)) - int(firstitem.offset)

def GetPDUSize(pdu):
	sum = 0
	for chunk in pdu:
		sum = sum + (GetChunkSize(chunk)+4)
	return	sum


def RequestBuilder(source):
	signals = FetchSignals()
	signals = SortSignalsByDB(signals)
	signals = SplitSignalsByRegion(signals)
	signals = SplitSignalsByContinousSpace(signals)
	signals = AddToPDUList(signals)

	print("###############################")
	for s in signals:
		print("....................PDU......" + str(GetPDUSize(s)) + " Bytes(including item header)......." + str(len(s)) + " items.........")
		for sig in s:
			print("--------------")
			PrintSignals(sig)

