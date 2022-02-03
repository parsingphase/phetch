from iptcinfo3 import IPTCInfo


def run_cli():
    jpg = "tmp/Exports/2022-01-16/IMG_6105-DeNoiseAI-standard (Bald Eagle).jpg"
    info = IPTCInfo(jpg)
    print(info)


if __name__ == '__main__':
    run_cli()
