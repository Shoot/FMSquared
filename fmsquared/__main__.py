import logging
import argparse
import platform
import pkg_resources

from .fmsquared import Collage

version = pkg_resources.require('fmsquared')[0].version
logger = logging.getLogger(__name__)

def main():
	# Print out a simple menu
	print('fmsquared | version ' + version + ' | python ' + platform.python_version())

	# Get the arguments
	parser = argparse.ArgumentParser(description='Generate a Last FM collage')

	# Necessary
	parser.add_argument('token', type=str, help='Your Last FM API key')
	parser.add_argument('user', type=str, help='The user to generate the collage for')

	# Optional
	parser.add_argument('-width', type=int, default=3, help='The amount of albums to display horizontally')
	parser.add_argument('-height', type=int, default=3, help='The amount of albums to display vertically')
	parser.add_argument('-period', type=str, default='overall', help='The time period to get albums from (overall, 7day, 1month, 3month, 6month, 12month)')
	parser.add_argument('--no-empty', action='store_true', default=False, help='Remove albums that have no album art')
	parser.add_argument('--artist-only', action='store_true', default=False, help='Display only artist name')
	parser.add_argument('--listen-count', action='store_true', default=False, help='Display listen count')
	parser.add_argument('--verbose', action='store_true', default=False, help='Increase verbosity of output')

	# Process the arguments
	args = parser.parse_args()

	# Increase verbosity (include DEBUG logs)
	if args.verbose:
		logging.basicConfig(
			level=logging.DEBUG,
			format="[%(asctime)s] [%(threadName)s] %(levelname)s: %(message)s",
			datefmt="%H:%M:%S"
		)
	else:
		logging.basicConfig(
			level=logging.INFO,
			format="[%(asctime)s] [%(threadName)s] %(levelname)s: %(message)s",
			datefmt="%H:%M:%S"
		)

	# Start making the collage
	client = Collage(args.token)
	logger.info('Initialized the collage generator')

	# Get a larger amount (25% more) of albums if we remove empty album covers
	if not args.no_empty:
		limit = int(args.width * args.height)
	else:
		limit = int((args.width * args.height) + (25 * ((args.width * args.height) / 100)))

	albums = client.get_top_albums(args.user, period=args.period, limit=limit)
	logger.info('Got ' + str(limit) + ' albums')

	data = client.build_collage_data(args.width, args.height, albums, no_empty=args.no_empty)
	logger.info('Built the collage data')
	
	image = client.generate_image(data, artist_only=args.artist_only, listen_count=args.listen_count)
	logger.info('Generated the final image')

	# Save the image
	image.save('final.png')
	logger.info('Saved the image')

if __name__ == "__main__":
	main()