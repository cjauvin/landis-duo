import re, os, random, argparse
from collections import OrderedDict, defaultdict


# command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument('aos_file', help='path to AOS values input file')
parser.add_argument('--out_dir', help='path to output dir (default ./out)', default='./out')
parser.add_argument('-n', help='number of samples/files (default 10)', type=int, default=10)
try: args = parser.parse_args()
except IOError, msg: parser.error(str(msg))

# species -> ecoregion -> [min, max]
params = OrderedDict() # OD because we need to keep keys in order
header = [] # top part (i.e. non-table) of file

for line in open(args.aos_file):
    parts = line.split(',')
    if len(parts) != 15: header.append(line.strip())
    if not re.match('\d+', parts[0]): continue
    species, ecoregion, min_val, max_val = [parts[i] for i in [1, 2, -6, -5]]
    params.setdefault(species, OrderedDict())
    params[species][ecoregion] = [float(min_val), float(max_val)]
    assert params[species][ecoregion][0] < params[species][ecoregion][1]

try: os.mkdir(args.out_dir) # create subdir (if it doesn't exist)
except: pass

for i in range(args.n):
    fout = open('%s/aos_%s.txt' % (args.out_dir, i), 'w')
    fout.write('\n'.join(header))
    values = defaultdict(list) # species -> list of values
    for species in params:
        for ecoregion, vals in params[species].items():
            values[species].append(str(random.uniform(vals[0], vals[1])))
    fout.write('\t'.join([''] + next(params.itervalues()).keys()) + '\n')
    for species in params.keys():
        fout.write('\t'.join([species] + values[species]) + '\n')
    fout.close()
