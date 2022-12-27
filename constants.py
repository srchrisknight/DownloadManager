import os,sys

DOWNLOADS_FOLDER = os.path.join(os.environ.get('USERPROFILE'),'Downloads')


if __name__ == '__main__':
	print(DOWNLOADS_FOLDER)