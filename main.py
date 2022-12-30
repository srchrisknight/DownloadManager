import os,sys,json,shutil, time, datetime,zipfile

from constants import DOWNLOADS_FOLDER
from folder_watcher import FolderWatcher

with open("sortingMap.json", 'r') as jFile:
	SORTING_MAP = json.load(jFile)

################################################################################
# Methods
################################################################################
def getDefaultFolders():
	defaultFolders = ['_{}'.format(item) for item in SORTING_MAP]
	defaultFolders.extend(['_unsorted'])

	return defaultFolders


def createDefaultFolders():
	for defaultFolder in getDefaultFolders():
		folderPath = os.path.join(DOWNLOADS_FOLDER, defaultFolder)
		if not os.path.isdir(folderPath):
			os.makedirs(folderPath)


def getFilesAndFolders():
	files = []
	folders = []
	for f in os.listdir(DOWNLOADS_FOLDER):
		if f in getDefaultFolders():
			continue

		fPath = os.path.join(DOWNLOADS_FOLDER, f)
		if os.path.isfile(fPath):
			files.append(fPath)
		if os.path.isdir(fPath):
			folders.append(fPath)

	return files,folders


def generateFileManifest(files):
	fileManifest = []
	for file in files:
		fileHasBeenSorted = False
		if file.split('.')[-1] in ['crdownload','tmp']:
			continue

		for subfolder in SORTING_MAP:
			targetDir = os.path.join(DOWNLOADS_FOLDER, '_{}'.format(subfolder))
			if file.split('.')[-1].lower() in SORTING_MAP[subfolder]:
				fileManifest.append((file, os.path.join(targetDir, os.path.basename(file))))
				fileHasBeenSorted = True

		if not fileHasBeenSorted:
			targetDir = os.path.join(DOWNLOADS_FOLDER, '_unsorted')

			fileManifest.append((file,os.path.join(targetDir, os.path.basename(file))))

	return fileManifest


def deArchiveFiles(files):
	result = False
	deArchiveDir = os.path.join(DOWNLOADS_FOLDER, '_archives','_dearchive')
	if not os.path.isdir(deArchiveDir):
		os.makedirs(deArchiveDir)

	for file in files:
		deArchiveName = os.path.basename(file)
		deArchiveName = '.'.join(deArchiveName.split('.')[0:-1])
		ext = file.split('.')[-1]
		deArchivePath = os.path.join(deArchiveDir, deArchiveName)

		if os.path.isdir(deArchivePath):
			continue

		if ext == 'zip':
			with zipfile.ZipFile(file, 'r') as zip_ref:
			    zip_ref.extractall(deArchivePath)
			    result = True

	return result


def runArchiveManager():
	archiveDir = os.path.join(DOWNLOADS_FOLDER, '_archives')
	newArchives = []

	for file in os.listdir(archiveDir):
		filepath = os.path.join(archiveDir, file)
		if not os.path.isfile(filepath):
			continue

		date_created = os.path.getmtime(filepath)
		dt_m = datetime.datetime.fromtimestamp(date_created)
		difference = datetime.datetime.now() - dt_m

		if difference.days < 3:
			newArchives.append(filepath)

	if len(newArchives) > 0:
		result = deArchiveFiles(newArchives)
		if result:
			os.startfile(os.path.join(archiveDir, '_dearchive'))


def runArchiveCleanup():
	deArchiveDir = os.path.join(DOWNLOADS_FOLDER, '_archives','_dearchive')

	if not os.path.isdir(deArchiveDir):
		os.makedirs(deArchiveDir)

	for f in os.listdir(deArchiveDir):
		filepath = os.path.join(deArchiveDir, f)
		if not os.path.isdir(filepath):
			continue

		date_created = os.path.getmtime(filepath)
		dt_m = datetime.datetime.fromtimestamp(date_created)
		difference = datetime.datetime.now() - dt_m

		if difference.days > 5:
			shutil.rmtree(filepath)		


def moveFiles(fileManifest):
	download_catagories = []
	for entry in fileManifest:
		shutil.move(entry[0], entry[1])
		
		catagory = os.path.basename(os.path.dirname(entry[1]))
		if catagory not in download_catagories:
			download_catagories.append(catagory)

	for catagory in download_catagories:
		os.startfile(os.path.join(DOWNLOADS_FOLDER, catagory))

	if "_archives" in download_catagories:
		print('running')
		runArchiveManager()


def generateFolderManifest(folders):
	folderManifest = []
	for folder in folders:
		targetDir = os.path.join(DOWNLOADS_FOLDER, '_unsorted')
		targetFolderPath = os.path.join(targetDir, os.path.basename(folder))

		folderManifest.append((folder, targetFolderPath))

	return folderManifest


def moveFolders(folderManifest):
	for entry in folderManifest:
		shutil.move(entry[0], entry[1])


def sort():
	createDefaultFolders()
	files,folders = getFilesAndFolders()

	fileManifest = generateFileManifest(files)
	moveFiles(fileManifest)

	folderManifest = generateFolderManifest(folders)
	moveFolders(folderManifest)	


def start(watchList = [], intervalSeconds = 5):
	watchers = []
	for target in watchList:
		watcher = FolderWatcher(target)
		watchers.append(watcher)

	while True:
		for watcher in watchers:
			if watcher.checkForUpdates():
				sort()
				watcher.updateContents()

		runArchiveCleanup()

		time.sleep(intervalSeconds)
		print('looping')


if __name__ == '__main__':
	start(watchList = [os.path.join(os.environ['USERPROFILE'], 'Downloads')])