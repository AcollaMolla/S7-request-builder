from src import S7RequestBuilder

def PrintSignals(signals):
	for s in signals:
		print(str(s.regionLetterCode) + str(s.db) + "." + str(s.offset) + ":" + str(s.datatype) + "\t\t\t.")

signals = S7RequestBuilder.RequestBuilder("address.txt")

print("###############################")
for s in signals:
	i = 0
	print("....................PDU......" + str(S7RequestBuilder.GetPDUSize(s)) + " Bytes(including item header)......." + str(len(s)) + " items.........")
	for sig in s:
		i = i + 1
		print("----------ITEM " + str(i) + "---------------.")
		PrintSignals(sig)
		print("--------------------------------.")