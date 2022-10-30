#!/usr/bin/env python

import json

from phetch_tools import init_flickr_client

# Path to JSON file downloaded from iNat
iNatJsonPath = '/Users/wechsler/repos/inat-history/stats/source/birds.json'

always_replace = [
    'Cyanocitta Cristata',
    'Greater Shearwater',
    'Parulidae',
]


def run_cli() -> None:
    flickr = init_flickr_client('./config.yml')
    with open(iNatJsonPath) as content_fp:
        observations = json.load(content_fp)
        for observation in observations:
            if observation['taxon']['rank'] in ['species', 'subspecies']:
                species = observation['taxon']['common_name']['name']
                photos = observation['photos']
                inat_uri = observation['uri']
                inat_description = observation['short_description']
                for photo in photos:
                    if 'native_page_url' in photo:
                        native_page_url = photo['native_page_url']
                        if native_page_url:
                            photo_id = native_page_url.split('/')[-2]
                            try:
                                photo_info = flickr.photos.getInfo(photo_id=photo_id)
                            except Exception as e:
                                print(f'Failed to fetch {photo_id} ({native_page_url})')
                                continue

                            photo = photo_info['photo']
                            # print(json.dumps(photo, indent=2))
                            # print(photo)
                            flickr_title = photo['title']['_content']
                            # print(f'{photo_id}: {species}, {title}')
                            # exit(1)
                            if flickr_title != species:
                                ignore_description = (len(inat_description) == 0) or 'Species TBD' in inat_description
                                replaceable_title = '4Y6A' in flickr_title or '?' in flickr_title or flickr_title in always_replace
                                species_name_longer = (len(species) >= len(flickr_title))
                                if replaceable_title or (species_name_longer and ignore_description):
                                    print(
                                        f'{photo_id}: {flickr_title} => {species} ({native_page_url} / {inat_uri}) - UPDATING …',
                                        end=''
                                    )
                                    flickr.photos.setMeta(photo_id=photo_id, title=species)
                                    flickr.photos.addTags(photo_id=photo_id, tags=f'"fixed:oldTitle={flickr_title}"')
                                    print(' OK')
                                else:
                                    desc_block = f': {inat_description}' if inat_description else ''
                                    print(
                                        f'{photo_id}: F: {flickr_title} => iN: {species}{desc_block} DIFFER ({native_page_url} / {inat_uri}) - no fix'
                                    )


run_cli()
