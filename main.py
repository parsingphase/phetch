import flickrapi
from yaml import BaseLoader, load as yload
from pathlib import Path
import requests
from time import sleep


album_id = '72157714145527936'
output_dir = './download'

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

# test = flickr.test.echo(foo="bar")

# photos = flickr.photos.search(user_id='73509078@N00', per_page='10')

# print(photos)

album = flickr.photosets.getInfo(photoset_id=album_id)
# print(album)

photoset_response = flickr.photosets.getPhotos(photoset_id=album_id, extras="url_o")
# urls = [photo['url_o'] for photo in photoset_response['photoset']['photo']]
# print(urls)
#
# print (photoset_response)
i = 1

for photo in photoset_response['photoset']['photo']:
    outfile = f'{output_dir}/{photo["id"]}.jpg'
    if not Path(outfile).exists():
        print(f'Downloading: {i}: {photo["url_o"]}:')
        r = requests.get(photo["url_o"])
        open(outfile, 'wb').write(r.content)
        print(' Done')
        sleep(2)
        i += 1

print("\nAll done")
