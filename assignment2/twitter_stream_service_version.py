# To run this code, first edit config.py with your configuration, then:
#
# mkdir data
# python twitter_stream.py -q apple -d data
# 
# It will produce the list of tweets for the query "apple" 
# in the file data/stream_apple.json
import hdfs
from hdfs import InsecureClient
import tweepy
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import time
import argparse
import string
import json


def get_parser():
	"""Get parser for command line arguments."""
	parser = argparse.ArgumentParser(description="Twitter Downloader")
	parser.add_argument("-q",
	                    "--query",
	                    dest="query",
	                    help="Query/Filter",
	                    default='*')
	return parser


class MyListener(StreamListener):
	"""Custom StreamListener for streaming data."""
	
	def __init__(self, query):
		query_fname = format_filename(query)
		self.count = 0
	
	def on_data(self, data):
		try:
			#buffersize=131072
			client.write(hdfs_path, json.dumps(data), append=True,encoding='utf-8')
			self.count += len(data)
			print(self.count)
			return True
		except BaseException as e:
			print("Error on_data: %s" % str(e))
			time.sleep(5)
		return True
	
	def on_error(self, status):
		print(status)
		return True


def format_filename(fname):
	"""Convert file name into a safe string.
    Arguments:
        fname -- the file name to convert
    Return:
        String -- converted file name
    """
	return ''.join(convert_valid(one_char) for one_char in fname)


def convert_valid(one_char):
	"""Convert a character into '_' if invalid.
    Arguments:
        one_char -- the char to convert
    Return:
        Character -- converted char
    """
	valid_chars = "-_.%s%s" % (string.ascii_letters, string.digits)
	if one_char in valid_chars:
		return one_char
	else:
		return '*'


if __name__ == '__main__':
	parser = get_parser()
	args = parser.parse_args()
	twitter_info = json.load(open('twitter_config.json'))

	auth = OAuthHandler(twitter_info['api_key']['consumer_key'], twitter_info['api_key']['consumer_secret'])
	auth.set_access_token(twitter_info['api_key']['access_token'],twitter_info['api_key']['access_secret'] )
	api = tweepy.API(auth)
	client = InsecureClient('http://115.146.86.32:50070', user='qilongz')
	hdfs_path = '/team40/stream_data/stream_data_2.json'
	if client.status(hdfs_path,strict  = False) == None:
		client.write(hdfs_path, '')
	
	twitter_stream = Stream(auth, MyListener(args.query))
	if args.query:
		twitter_stream.filter(track=args.query, locations=twitter_info['harvest_config']['ausCoordinates'])
	else:
		twitter_stream.filter(track='*', locations=twitter_info['harvest_config']['ausCoordinates'])
