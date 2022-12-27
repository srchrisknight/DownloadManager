import os,sys

class FolderWatcher(object):
	def __init__(self, watchDir, **kwargs):
		super().__init__()

		self.watchDir = watchDir
		self.currentContents = os.listdir(watchDir)

	def checkForUpdates(self):
		self.newContents = os.listdir(self.watchDir)

		try:
			result = zip(self.currentContents, self.newContents, strict = True)

			for pair in list(result):
				if pair[0] != pair[1]:
					return True

		except Exception as E:
			print(E)
			return True

	def updateContents(self):
		self.currentContents = os.listdir(self.watchDir)


if __name__ == "__main__":
	FW = FolderWatcher('C:/Users/Chris/Downloads')
	newFile = os.path.join('C:/Users/Chris/Downloads', 'newFile.txt')

	with open(newFile, 'w') as txtFile:
		pass

	if FW.checkForUpdates():
		print('running update')