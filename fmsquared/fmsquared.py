import io
import math
import numpy
import logging
import requests
import binascii
from PIL import Image, ImageDraw, ImageFont

import scipy
import scipy.cluster

from .constants import Constants
from .exceptions import TooFewAlbums

class Collage:
	def __init__(self, apikey):
		self.apikey = apikey
		self.logger = logging.getLogger(__name__)

	def _api_call(self, method, params):
		"""
		Make a request to the Last.fm API

		:param str method: the API method to use (https://www.last.fm/api/)
		:param array params: data given for the API call

		:return: the request object for the API call
		"""

		params['api_key'] = self.apikey
		params['format'] = 'json'
		params['method'] = method

		resp = requests.get('http://ws.audioscrobbler.com/2.0/', params=params)
		resp.raise_for_status()

		return resp

	def get_top_albums(self, user, period='overall', limit=50):
		"""
		Get the user's top albums

		:param str user: the user to get the album data for
		:param str period: the time period to get data from
		:param int limit: the limit on the amount of albums to fetch

		:return: a list of the user's albums
		"""

		if not period in Constants.valid_time_periods:
			raise ValueError('Invalid time period')

		albums = []

		# Limit is 1000 albums per page
		for page in range(math.ceil(limit / 1000)):
			api_limit = 1000 if limit > 1000 else limit
			self.logger.debug('Getting ' + str(api_limit) + ' albums')
			data = self._api_call('user.gettopalbums', {
				'user': user,
				'period': period,
				'limit': api_limit
			}).json()['topalbums']['album']

			if limit > 1000:
				limit -= 1000

			albums += data

		return albums

	def build_collage_data(self, width, height, albums, no_empty=False):
		"""
		Build the collage data into a 2D array, like so:
		[
			[album1, album2, album3],
			[album4, album5, album6],
			[album7, album8, album9],
		]

		:param int width: the amount of albums to display horizontally
		:param int height: the amount of albums to display vertically
		:param array albums: array of albums in order from most to least listened to from the Last.fm API
		:param bool no_empty: whether or not to remove albums without album art

		:return: the collage data, such as in the example above
		"""

		if no_empty:
			for album in albums[:]:
				for image in album['image']:
					if not image['#text']:
						albums.remove(album)
						break

		if (width * height) > len(albums):
			raise TooFewAlbums('Not enough albums available')

		rows = []
		count = 0

		for i in range(height):
			item = []
			for i in range(width):
				item.append(albums[count])
				count += 1
			rows.append(item)

		return rows

	def album_art(self, album):
		"""
		Download the album art from an album, if it doesn't exist, a black image will be used instead.

		:param array album: the album's information from the Last.fm API

		:return: the album art as a PIL image
		"""

		# Get the highest quality album art
		album_url = album['image'][-1]['#text']

		# If album art doesn't exist, create a blank image
		if album_url and album_url.split('.')[-1] in Constants.valid_art_extensions:
			self.logger.debug('Downloading album art for ' + album['name'])
			resp = requests.get(album_url)
			image = Image.open(io.BytesIO(resp.content))
		else:
			self.logger.debug('Creating empty album art for ' + album['name'])
			image = Image.new('RGB', (200, 200))
		
		image.format = 'PNG'
		return image

	def generate_image(self, data, artist_only=False, listen_count=False):
		"""
		Generate the collage using album info

		:param array data: data generated in self.build_collage_data()
		:param bool artist_only: only use the artist's name in the text
		:param bool listen_count: include the listen count in the text

		:return: the final collage image
		"""

		vertical_albums = []
		font = ImageFont.truetype('arial.ttf', 15)

		for vertical_album in data:
			horizontal_group = []

			for album in vertical_album:
				# Download the album art
				album_art = self.album_art(album).resize((200, 200))
				
				# Getting dominant color from the album art
				# https://stackoverflow.com/questions/3241929/python-find-dominant-most-common-color-in-an-image
				ar = numpy.asarray(album_art)
				shape = ar.shape
				ar = ar.reshape(numpy.product(shape[:2]), shape[2]).astype(float)

				codes, dist = scipy.cluster.vq.kmeans(ar, 5)
				vecs, dist = scipy.cluster.vq.vq(ar, codes)
				counts, bins = numpy.histogram(vecs, len(codes))

				index_max = numpy.argmax(counts)
				peak = codes[index_max]
				dom_color = binascii.hexlify(bytearray(int(c) for c in peak)).decode('ascii')

				# If the image is darker, we choose a white font, and vice versa
				# https://stackoverflow.com/questions/9780632/how-do-i-determine-if-a-color-is-closer-to-white-or-black
				color = 0.2126 * peak[0] + 0.7152 * peak[1] + 0.0722 * peak[2]

				self.logger.debug('Dominant color for ' + album['name'] + ' is ' + '#' + dom_color)

				if color < 128:
					font_color = (255, 255, 255)
				else:
					font_color = (0, 0, 0)

				# Draw text onto the album art
				self.logger.debug('Writing text to image')

				draw = ImageDraw.Draw(album_art)
				draw.text((0, 0), album['artist']['name'] + ('\n' + album['name'] if not artist_only else '') + ('\n' + album['playcount'] + ' plays' if listen_count else ''), font_color, font=font)

				# Resize the image and add it to the array
				horizontal_group.append(album_art)

			# Make a new image with the three covers
			self.logger.debug('Making a new horizontal group of images')
			new_image = Image.new('RGB', (200 * len(vertical_album), 200))
			x_offset = 0

			for image in horizontal_group:
				new_image.paste(image, (x_offset, 0))
				x_offset += image.size[0]

			vertical_albums.append(new_image)

		# Generate the final image
		self.logger.debug('Making the final image')
		
		final_image = Image.new('RGB', (vertical_albums[0].size[0], 200 * len(vertical_albums)))
		y_offset = 0

		for image in vertical_albums:
			final_image.paste(image, (0, y_offset))
			y_offset += image.size[1]

		return final_image