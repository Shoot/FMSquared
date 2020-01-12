import io
import numpy
import requests
import binascii
from PIL import Image, ImageDraw, ImageFont

import scipy
import scipy.misc
import scipy.cluster

class Collage:
	def __init__(self, apikey):
		self.apikey = apikey

	def _request(self, params):
		params['api_key'] = self.apikey
		params['format'] = 'json'

		resp = requests.get('http://ws.audioscrobbler.com/2.0/', params=params)
		resp.raise_for_status()

		return resp

	def get_top_albums(self, user, period='overall', limit=50):
		valid_time_periods = ['overall', '7day', '1month', '3month', '6month', '12month']
		if not period in valid_time_periods:
			raise Exception('Invalid time period (' + ', '.join(valid_time_periods) + ')')
		
		return self._request({
			'method': 'user.gettopalbums',
			'user': user,
			'period': period,
			'limit': limit
		}).json()['topalbums']['album']

	def build_collage_data(self, width, height, albums):
		if (width * height) > 50:
			raise Exception('Total amount of albums must be less than 50')

		if (width * height) > len(albums):
			raise Exception('Not enough albums available')

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
		# Get the highest quality album art
		album_url = album['image'][-1]['#text']

		# If album art doesn't exist, create a blank image
		if album_url:
			resp = requests.get(album_url)
			image = Image.open(io.BytesIO(resp.content))
		else:
			image = Image.new('RGB', (200, 200))
		
		image.format = 'PNG'

		return image

	def generate_image(self, data):
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

				# If the image is darker, we choose a white font, and vice versa
				# https://stackoverflow.com/questions/9780632/how-do-i-determine-if-a-color-is-closer-to-white-or-black
				color = 0.2126 * peak[0] + 0.7152 * peak[1] + 0.0722 * peak[2]

				if color < 128:
					font_color = (255, 255, 255)
				else:
					font_color = (0, 0, 0)

				# Draw text onto the album art
				draw = ImageDraw.Draw(album_art)
				draw.text((0, 0), album['artist']['name'] + '\n' + album['name'], font_color, font=font)

				# Resize the image and add it to the array
				horizontal_group.append(album_art)

			# Make a new image with the three covers
			new_image = Image.new('RGB', (200 * len(vertical_album), 200))
			x_offset = 0

			for image in horizontal_group:
				new_image.paste(image, (x_offset, 0))
				x_offset += image.size[0]

			vertical_albums.append(new_image)

		# Generate the final image
		final_image = Image.new('RGB', (vertical_albums[0].size[0], 200 * len(vertical_albums)))
		y_offset = 0

		for image in vertical_albums:
			final_image.paste(image, (0, y_offset))
			y_offset += image.size[1]

		return final_image