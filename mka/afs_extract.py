import argparse
import collections
import pathlib
import subprocess
import sys


def afs_extract(filepath: pathlib.Path):
    with open(filepath, 'rb') as afs:
        # read 8 bytes from file, with the first four bytes
        # being hdr.id, and the last four bytes being the
        # number of ADX files in the archive
        HDR = collections.namedtuple('HDR', ('id', 'num'))
        hdr = HDR(
            id=afs.read(4),
            # assuming little endian because the sample AFS file
            # I'm working with gives this as "CF 00 00 00", which
            # is 207 with little endian and 3,472,883,712 with big
            # endian, which... just feels too big.
            num=int.from_bytes(afs.read(4), 'little')
        )

        # We compare hdr.id to the literal bytestring b'AFS\x00'
        # and when these don't match, we close the file and complain
        # that it's not a proper AFS file.
        if hdr.id != b'AFS\x00':
            sys.exit('Not an AFS file')

        # output the file we're extracting from and the number of
        # ADX blocks contained within it
        print(f'{filepath} - {hdr.num} ADX blocks')

        # read blocks of 8 bytes each, assigning them into `idx`
        ADXHeader = collections.namedtuple('ADXHeader', ('offset', 'size'))
        idx = [
            ADXHeader(
                offset=int.from_bytes(afs.read(4), 'little'),
                size=int.from_bytes(afs.read(4), 'little')
            )
            for _ in range(hdr.num)
        ]

        # now, we loop through each of these ADX "header" structs
        for i, header in enumerate(idx):
            # assign outfile as the path of the destination ADX file
            # indexed by the number of the loop, then open it in "wb"
            # mode
            outfile = filepath.with_name(f'{filepath.stem}_{i:03}.adx')

            with open(outfile, 'wb') as adx:
                # set the file position of the input stream according
                # to the data in the header
                afs.seek(header.offset)

                # output {destination} {offset} {size}
                print(f'{str(outfile):<50} offset=0x{header.offset:08X} size=0x{header.size:08X}')

                # read the necessary number of bytes into memory
                # and write it out to the adx file
                adx.write(afs.read(header.size))


def convert_to_ogg(filepath: pathlib.Path) -> int:
    args = ('ffmpeg', '-i', filepath, filepath.with_suffix('.ogg'))
    r = subprocess.run(args, capture_output=True)
    return r.status_code


def parse_command_line():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'filenames',
        nargs='+', type=pathlib.Path,
        help='the AFS files to extract'
    )
    parser.add_argument(
        '-c', '--convert-ogg',
        action='store_true',
        help='pass this flag to convert the resulting .adx files to .ogg'
    )
    parser.add_argument(
        '-r', '--remove-adx', '--delete-adx',
        dest='remove_adx', action='store_true',
        help='pass this flag to delete the resulting .adx files'
    )

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_command_line()

    for filename in args.filenames:
        path = pathlib.Path(filename).resolve()
        afs_extract(path)

        for adx in path.parent.glob('*.adx'):
            if args.convert:
                success = convert_to_ogg(adx)
                if not success:
                    sys.stderr.write(f'Error in converting {adx} to .ogg.\n')

            if args.remove_adx:
                adx.unlink()
