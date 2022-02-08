from iptcinfo3 import IPTCInfo

iptc_keys = [
    'supplemental category',
    'keywords',
    'contact',
    'date created',
    'digital creation date',
    'time created',
    'digital creation time',
    'by-line',
    'object name'
]


def run_cli() -> None:
    jpg = "/mnt/photos/2022-01-16/IMG_6105-DeNoiseAI-standard (Bald Eagle).jpg"
    info = IPTCInfo(jpg)
    print(info)
    print('data:  ', {k: info[k] for k in iptc_keys})


if __name__ == '__main__':
    run_cli()
