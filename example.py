from src import S7RequestBuilder

def PrintSignals(signals):
	for s in signals:
		print(str(s.regionLetterCode) + str(s.db) + "." + str(s.offset) + ":" + str(s.datatype))

signals = S7ResponseBuilder.RequestBuilder("test")

print("###############################")
for s in signals:
	print("....................PDU......" + str(GetPDUSize(s)) + " Bytes(including item header)......." + str(len(s)) + " items.........")
	for sig in s:
		print("--------------")
		PrintSignals(sig)