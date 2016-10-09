#!/usr/bin/env python
from __future__ import division
from __future__ import print_function
from subprocess import call
import logging
import tempfile
import StringIO
import pyaudio

"""
this isn't being used yet
"""


class SoxError(Exception):
	pass


# class Microphone(object):
# 	"""
# 	Uses SoX to capture audio from the default microphone
# 	"""
# 	def __init__(self, threshold='3%'):
# 		# sensitivity of silence recognition
# 		self.threshold = threshold
# 		logging.basicConfig(level=logging.INFO)
# 		self.logger = logging.getLogger('microphone')
# 		self.audio = None
#
# 	def __del__(self):
# 		# print 'Microphone ... goodbye'
# 		if self.audio:
# 			self.audio.close()
# 		self.logger.debug('microphone closing')
#
# 	@staticmethod
# 	def playAudioFile(fileName):
# 		"""
# 		Plays back the captured audio
# 		in: file name
# 		out: none
# 		"""
# 		cmd = 'play -q {0!s}'.format(fileName)
# 		call(cmd, shell=True)
#
# 	def readAudio(self, fileName, chunk=1024):
# 		"""
# 		Reads a wave file into memory and stores it in a StringIO. It is kept
# 		as a class member audio
# 		in: file name of wave
# 		out: length of file
# 		"""
# 		f = open(fileName)
# 		byte = f.read(chunk)  # this was 1 and it worked fine
#
# 		s = StringIO.StringIO()
# 		s.write(byte)
# 		while byte != '':
# 			byte = f.read(chunk)
# 			s.write(byte)
# 		self.audio = s
# 		return s.len
#
# 	def getAudio(self):
# 		"""
# 		from: https://wit.ai/docs/http/20160330#get-intent-via-text-link
# 		sox -d -b 16 -c 1 -r 16k sample.wav
# 		-b: bits
# 		-c: number of channels
# 		-d: default device
# 		-e: encoding signed-integer
# 		-q: quiet mode, no graphics
# 		-r: sampling rate
# 		-t: file type -> wav
#
# 		$ file sample.wav
# 			sample.wav: RIFF (little-endian) data, WAVE audio, Microsoft PCM, 16 bit, mono 16000 Hz
#
# 		$ curl -XPOST 'https://api.wit.ai/speech?v=20141022' \
# 			-i -L \
# 			-H "Authorization: Bearer $TOKEN" \
# 			-H "Content-Type: audio/wav" \
# 			--data-binary "@sample.wav"
# 		"""
# 		# print 'Ready'
# 		self.logger.debug('Ready')
#
# 		# rec -q -t wav -c 1 test.wav rate 8k silence 1 0.1 3% 1 3.0 3%
# 		temp = tempfile.NamedTemporaryFile().name
# 		self.logger.debug('Openned tempfile: %s', temp)
# 		cmd = 'rec -q -t wav -c 1 {0!s} rate 16k silence 1 0.1 {1!s} 1 3.0 {2!s}'.format(temp, self.threshold, self.threshold)
# 		call(cmd, shell=True)
#
# 		# print 'ok ... got it!'
# 		self.logger.debug('ok ... got it!')
#
# 		return self.readAudio(temp)  # grab it from the disk
#
# 	def play(self):
# 		"""
# 		Plays captured audio
# 		"""
# 		if self.audio is None:
# 			raise SoxError('Audio not collected yet to play')
# 		# if not io.__class__ == StringIO.StringIO:
# 		# 	print 'Wrong type of input'
# 		# 	return
#
# 		# instantiate PyAudio
# 		p = pyaudio.PyAudio()
#
# 		# open stream
# 		stream = p.open(format=pyaudio.paInt16,
# 						channels=1,
# 						rate=16000,
# 						output=True)
# 		self.audio.seek(0)
# 		stream.write(self.audio.read())
#
# 		# stop stream
# 		stream.stop_stream()
# 		stream.close()
#
# 		# close PyAudio
# 		p.terminate()


class BaseMicrophone(object):
	def __init__(self):
		self.wave_buffer = []

	def playAudio(self, fileName):
		"""
		Plays back the captured audio
		in: file name
		out: none
		"""
		cmd = 'play -q %s' % fileName
		call(cmd, shell=True)


class SoxMicrophone(object):
	"""
	Uses SoX to capture audio from the default microphone
	"""
	def __init__(self, threshold='3%'):
		# sensitivity of silence recognition
		self.threshold = threshold
		# logging.basicConfig(level=logging.INFO)
		# self.logger = logging.getLogger('microphone')

	def __del__(self):
		# print 'Microphone ... goodbye'
		# self.logger.debug('microphone closing')
		pass

	def playAudio(self, fileName):
		"""
		Plays back the captured audio
		in: file name
		out: none
		"""
		cmd = 'play -q %s' % fileName
		call(cmd, shell=True)

	def readAudio(self, fileName):
		"""
		Reads a wave file into memory and stores it in a StringIO
		in: file name of wave
		out: returns the StringIO
		"""
		f = open(fileName)
		byte = f.read()
		return byte

		# s = StringIO.StringIO()
		# s.write(byte)
		# while byte != '':
		# 	byte = f.read(1)
		# 	s.write(byte)
		# return s

	def getAudio(self):
		"""
		from: https://wit.ai/docs/http/20160330#get-intent-via-text-link
		sox -d -b 16 -c 1 -r 16k sample.wav

		$ file sample.wav
			sample.wav: RIFF (little-endian) data, WAVE audio, Microsoft PCM, 16 bit, mono 16000 Hz

		"""
		# print 'Ready'
		# self.logger.debug('Ready')

		# rec -q -t wav -c 1 test.wav rate 8k silence 1 0.1 3% 1 3.0 3%
		temp = tempfile.NamedTemporaryFile().name
		temp = './test.wav'
		# self.logger.debug('Openned tempfile: %s' % {temp})
		# cmd = 'rec -q -t wav -c 1 %s -r 16000 silence 1 0.1 %s 1 3.0 %s' % (temp, self.threshold, self.threshold)
		cmd = 'rec -q -b 16 -c 1 -t wavpcm -r 16000 --endian little {} silence 1 0.1 3% 1 3.0 3%'.format(temp)
		call(cmd, shell=True)

		# print 'ok ... got it!'
		# self.logger.debug('ok ... got it!')

		return temp


import pyaudio
import wave


class PyAudioMicrophone(object):
	def __init__(self):
		self.format = pyaudio.paInt16
		self.channels = 2
		self.rate = 44100
		self.chunk = 1024
		self.record_time = 5  # seconds
		# self.filename = "file.wav"

		self.frames = []

	def grab(self):

		audio = pyaudio.PyAudio()

		# start Recording
		stream = audio.open(
			format=self.format,
			channels=self.channels,
			rate=self.rate,
			input=True,
			frames_per_buffer=self.chunk
		)
		print("recording...")
		frames = []

		for i in range(0, int(self.rate / self.chunk * self.record_time)):
			data = stream.read(self.chunk)
			frames.append(data)
		print("finished recording")

		self.frames = frames  # audio

		# stop Recording
		stream.stop_stream()
		stream.close()
		audio.terminate()
		self.sample_size = audio.get_sample_size(self.format)

	def saveToWave(self, filename):
		if not self.frames:
			raise Exception('No audio captured yet')
		waveFile = wave.open(filename, 'wb')
		waveFile.setnchannels(self.channels)
		waveFile.setsampwidth(self.sample_size)
		waveFile.setframerate(self.rate)
		waveFile.writeframes(b''.join(self.frames))
		waveFile.close()

	def playAudio(self, filename):
		"""
		Plays back the captured audio
		in: file name
		out: none
		"""
		cmd = 'play -q {}'.format(filename)
		call(cmd, shell=True)


def main():
	# mic = Microphone()
	# print('Say something:')
	# f = mic.getAudio()
	# print('I heard:')
	# mic.playAudio(f)

	t = PyAudioMicrophone()
	t.grab()
	t.saveToWave('file.wav')
	t.playAudio('file.wav')

	# mic.playAudio(filename)
	# snd = mic.readAudio(filename)
	# print 'Sound size: %s' % {snd.len}


if __name__ == "__main__":
	main()
