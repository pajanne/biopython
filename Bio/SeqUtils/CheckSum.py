# Copyright 2002 by Yves Bastide and Brad Chapman.
# Copyright 2007 by Sebastian Bassi
# All rights reserved.
# This code is part of the Biopython distribution and governed by its
# license.  Please see the LICENSE file that should have been included
# as part of this package.

"""Functions to calculate assorted sequence checksums."""

# crc32, crc64, gcg, and seguid
# crc64 is adapted from BioPerl

from binascii import crc32 as _crc32

def crc32(seq):
    """Returns the crc32 checksum for a sequence (string or Seq object)."""
    try:
        #Assume its a Seq object
        return _crc32(seq.tostring())
    except AttributeError:
        #Assume its a string
        return _crc32(seq)

def _init_table_h():
    _table_h = []
    for i in range(256):
        l = i
        part_h = 0
        for j in range(8):
            rflag = l & 1
            l >>= 1
            if part_h & 1: l |= (1L << 31)
            part_h >>= 1L
            if rflag: part_h ^= 0xd8000000L
        _table_h.append(part_h)
    return _table_h

# Initialisation
_table_h = _init_table_h()

def crc64(s):
    """Returns the crc64 checksum for a sequence (string or Seq object)."""
    crcl = 0
    crch = 0
    for c in s:
        shr = (crch & 0xFF) << 24
        temp1h = crch >> 8
        temp1l = (crcl >> 8) | shr
        idx  = (crcl ^ ord(c)) & 0xFF
        crch = temp1h ^ _table_h[idx]
        crcl = temp1l

    return "CRC-%08X%08X" % (crch, crcl)


def gcg(seq):
    """Returns the GCG checksum (int) for a sequence (string or Seq object).

    Given a nucleotide or amino-acid secuence (or any string),
    returns the GCG checksum (int). Checksum used by GCG program.
    seq type = str.
    Based on BioPerl GCG_checksum. Adapted by Sebastian Bassi
    with the help of John Lenton, Pablo Ziliani, and Gabriel Genellina.
    All sequences are converted to uppercase """
    index = checksum = 0
    if type(seq)!=type("aa"):
        seq=seq.tostring()
    for char in seq:
        index += 1
        checksum += index * ord(char.upper())
        if index == 57: index = 0
    return checksum % 10000

def seguid(seq):
    """Returns the SEGUID (string) for a sequence (string or Seq object).
    
    Given a nucleotide or amino-acid secuence (or any string),
    returns the SEGUID string (A SEquence Globally Unique IDentifier).
    seq type = str. 
    For more information about SEGUID, see:
    http://bioinformatics.anl.gov/seguid/
    DOI: 10.1002/pmic.200600032 """
    try:
        #Python 2.5 sha1 is in hashlib
        import hashlib
        m = hashlib.sha1()
    except:
        #For older versions 
        import sha
        m = sha.new()
    import base64
    if type(seq)!=type("aa"):
        seq=seq.tostring().upper()
    else:
        seq=seq.upper()
    m.update(seq)
    try:
        #For Python 2.5
        return base64.b64encode(m.digest()).rstrip("=")
    except:
        #For older versions
        import os
        #Note: Using os.linesep doesn't work on Windows,
        #where os.linesep= "\r\n" but the encoded string
        #contains "\n" but not "\r\n"
        return base64.encodestring(m.digest()).replace("\n","").rstrip("=")

if __name__ == "__main__":
    print "Quick self test"

    str_light_chain_one = "QSALTQPASVSGSPGQSITISCTGTSSDVGSYNLVSWYQQHPGK" \
                    + "APKLMIYEGSKRPSGVSNRFSGSKSGNTASLTISGLQAEDEADY" \
                    + "YCSSYAGSSTLVFGGGTKLTVL"

    str_light_chain_two = "QSALTQPASVSGSPGQSITISCTGTSSDVGSYNLVSWYQQHPGK" \
                    + "APKLMIYEGSKRPSGVSNRFSGSKSGNTASLTISGLQAEDEADY" \
                    + "YCCSYAGSSTWVFGGGTKLTVL"

    assert crc64(str_light_chain_one) == crc64(str_light_chain_two)
    assert 'CRC-44CAAD88706CC153' == crc64(str_light_chain_one)

    assert 'BpBeDdcNUYNsdk46JoJdw7Pd3BI' == seguid(str_light_chain_one)
    assert 'X5XEaayob1nZLOc7eVT9qyczarY' == seguid(str_light_chain_two)
    
    print "Done"
