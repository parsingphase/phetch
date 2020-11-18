import flickrapi
from yaml import BaseLoader, load as yload
from pathlib import Path


# config eg: {'api_key': 'MYKEY', 'api_secret': 'MYSECRET'}

configFile = './flickr.yml'
configPath = Path(configFile)
if not configPath.exists():
    print(f'Configfile {configFile} not found')
    exit(1)

configData = configPath.read_text()
config = yload(configData, Loader=BaseLoader)
# print(config)

flickr = flickrapi.FlickrAPI(config['api_key'], config['api_secret'], format='parsed-json')

album_id = '72157714145527936'

# test = flickr.test.echo(foo="bar")

# photos = flickr.photos.search(user_id='73509078@N00', per_page='10')

# print(photos)

album = flickr.photosets.getInfo(photoset_id=album_id)
print(album)

photos = flickr.photosets.getPhotos(photoset_id=album_id, extras="url_o")
print(photos)